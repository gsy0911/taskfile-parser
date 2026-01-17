from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import yaml

from taskfile_parser.domain.taskfile import Include, Task, Taskfile


class TaskFileRepository:
    def __init__(self, path: str = "", prefix: str | None = None):
        self.path = Path(path) if path else None
        self.prefix = prefix

    def _read(self, content: str | None = None) -> Taskfile:
        if content is not None:
            docs = list(yaml.safe_load_all(content))
        else:
            if self.path is None:
                raise ValueError("Path must be provided when reading from file")
            with open(self.path, encoding="utf-8") as f:
                docs = list(yaml.safe_load_all(f))

        includes = []
        for k, v in docs[0].get("includes", {}).items():
            if isinstance(v, str):
                i = Include(prefix=k, taskfile=v)
                includes.append(i)
            elif isinstance(v, dict):
                i = Include(prefix=k, taskfile=v.get("taskfile", ""))
                includes.append(i)

        tasks = []
        for k, v in docs[0].get("tasks", {}).items():
            t = Task(
                prefix=self.prefix,
                name=k,
                desc=v.get("desc", ""),
                requires=v.get("requires", {}),
            )
            tasks.append(t)
        return Taskfile(includes=includes, tasks=tasks)

    def read_tasks(self) -> list[Task]:
        base_taskfile = self._read()
        tasks = base_taskfile.tasks
        for i in base_taskfile.includes:
            if i.taskfile.startswith("https://"):
                # Fetch remote taskfile via HTTP GET
                try:
                    with urlopen(i.taskfile) as response:
                        content = response.read().decode("utf-8")
                        remote_taskfile = TaskFileRepository(prefix=i.prefix)._read(content=content)
                        tasks.extend(remote_taskfile.tasks)
                except (URLError, HTTPError, OSError, ValueError):
                    # If fetching or parsing fails, skip this include
                    pass
            else:
                relative_path = Path(i.taskfile)
                if self.path is None:
                    raise ValueError("Base taskfile path required for resolving relative includes")
                target_path = self.path.parent / relative_path
                tasks.extend(TaskFileRepository(path=str(target_path), prefix=i.prefix)._read().tasks)

        return tasks


class TaskfileFinder:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def find(self) -> str | None:
        # Check for all possible taskfile name variations
        candidates = [
            "taskfile.yaml",
            "taskfile.yml",
            "Taskfile.yaml",
            "Taskfile.yml",
        ]
        for candidate in candidates:
            taskfile_path = self.root_dir / candidate
            if taskfile_path.exists():
                return str(taskfile_path)
        return None

from pathlib import Path

from taskfile_parser.domain.taskfile import Taskfile
from taskfile_parser.repository.repository import TaskfileFinder, TaskFileRepository


class TestTaskFileRepository:
    """Test cases for the TaskFileRepository class."""

    def test_init_with_path(self, tmp_path):
        """Test TaskFileRepository initialization with path only."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_path.touch()

        repo = TaskFileRepository(path=str(taskfile_path))
        assert repo.path == taskfile_path
        assert repo.prefix is None

    def test_init_with_path_and_prefix(self, tmp_path):
        """Test TaskFileRepository initialization with path and prefix."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_path.touch()

        repo = TaskFileRepository(path=str(taskfile_path), prefix="test-prefix")
        assert repo.path == taskfile_path
        assert repo.prefix == "test-prefix"

    def test_read_simple_taskfile(self, tmp_path):
        """Test reading a simple Taskfile with only tasks."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_content = """
tasks:
  build:
    desc: Build the application
  test:
    desc: Run tests
    requires:
      vars:
        - VAR1
"""
        taskfile_path.write_text(taskfile_content)

        repo = TaskFileRepository(path=str(taskfile_path))
        taskfile = repo._read()

        assert isinstance(taskfile, Taskfile)
        assert len(taskfile.tasks) == 2
        assert taskfile.tasks[0].name == "build"
        assert taskfile.tasks[0].desc == "Build the application"
        assert taskfile.tasks[1].name == "test"
        assert taskfile.tasks[1].desc == "Run tests"
        assert taskfile.tasks[1].requires == {"vars": ["VAR1"]}
        assert len(taskfile.includes) == 0

    def test_read_taskfile_with_string_includes(self, tmp_path):
        """Test reading a Taskfile with string-type includes."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_content = """
includes:
  backend: ./backend/Taskfile.yml
  frontend: ./frontend/Taskfile.yml
tasks:
  all:
    desc: Run all tasks
"""
        taskfile_path.write_text(taskfile_content)

        repo = TaskFileRepository(path=str(taskfile_path))
        taskfile = repo._read()

        assert isinstance(taskfile, Taskfile)
        assert len(taskfile.includes) == 2
        assert taskfile.includes[0].prefix == "backend"
        assert taskfile.includes[0].taskfile == "./backend/Taskfile.yml"
        assert taskfile.includes[1].prefix == "frontend"
        assert taskfile.includes[1].taskfile == "./frontend/Taskfile.yml"
        assert len(taskfile.tasks) == 1

    def test_read_taskfile_with_dict_includes(self, tmp_path):
        """Test reading a Taskfile with dictionary-type includes."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_content = """
includes:
  backend:
    taskfile: ./backend/Taskfile.yml
  frontend:
    taskfile: ./frontend/Taskfile.yml
tasks:
  deploy:
    desc: Deploy application
"""
        taskfile_path.write_text(taskfile_content)

        repo = TaskFileRepository(path=str(taskfile_path))
        taskfile = repo._read()

        assert isinstance(taskfile, Taskfile)
        assert len(taskfile.includes) == 2
        assert taskfile.includes[0].prefix == "backend"
        assert taskfile.includes[0].taskfile == "./backend/Taskfile.yml"
        assert taskfile.includes[1].prefix == "frontend"
        assert taskfile.includes[1].taskfile == "./frontend/Taskfile.yml"

    def test_read_taskfile_with_prefix(self, tmp_path):
        """Test reading a Taskfile with a prefix applied to tasks."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_content = """
tasks:
  build:
    desc: Build the application
  test:
    desc: Run tests
"""
        taskfile_path.write_text(taskfile_content)

        repo = TaskFileRepository(path=str(taskfile_path), prefix="myprefix")
        taskfile = repo._read()

        assert len(taskfile.tasks) == 2
        assert taskfile.tasks[0].prefix == "myprefix"
        assert taskfile.tasks[1].prefix == "myprefix"

    def test_read_tasks_without_includes(self, tmp_path):
        """Test read_tasks method with a Taskfile without includes."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_content = """
tasks:
  build:
    desc: Build the application
  test:
    desc: Run tests
"""
        taskfile_path.write_text(taskfile_content)

        repo = TaskFileRepository(path=str(taskfile_path))
        tasks = repo.read_tasks()

        assert len(tasks) == 2
        assert tasks[0].name == "build"
        assert tasks[1].name == "test"

    def test_read_tasks_with_local_includes(self, tmp_path):
        """Test read_tasks method with local includes."""
        # Create main Taskfile
        main_taskfile = tmp_path / "Taskfile.yml"
        main_content = """
includes:
  backend: ./backend/Taskfile.yml
tasks:
  main-task:
    desc: Main task
"""
        main_taskfile.write_text(main_content)

        # Create backend directory and Taskfile
        backend_dir = tmp_path / "backend"
        backend_dir.mkdir()
        backend_taskfile = backend_dir / "Taskfile.yml"
        backend_content = """
tasks:
  build:
    desc: Build backend
  test:
    desc: Test backend
"""
        backend_taskfile.write_text(backend_content)

        repo = TaskFileRepository(path=str(main_taskfile))
        tasks = repo.read_tasks()

        assert len(tasks) == 3
        # Check main task
        main_tasks = [t for t in tasks if t.name == "main-task"]
        assert len(main_tasks) == 1
        assert main_tasks[0].desc == "Main task"

        # Check backend tasks
        backend_tasks = [t for t in tasks if t.prefix == "backend"]
        assert len(backend_tasks) == 2
        assert backend_tasks[0].name == "build"
        assert backend_tasks[1].name == "test"

    def test_read_tasks_with_nested_includes(self, tmp_path):
        """Test read_tasks method with nested includes (not expanded recursively)."""
        # Create main Taskfile
        main_taskfile = tmp_path / "Taskfile.yml"
        main_content = """
includes:
  sub: ./sub/Taskfile.yml
tasks:
  main:
    desc: Main task
"""
        main_taskfile.write_text(main_content)

        # Create sub directory and Taskfile
        sub_dir = tmp_path / "sub"
        sub_dir.mkdir()
        sub_taskfile = sub_dir / "Taskfile.yml"
        sub_content = """
tasks:
  sub-task:
    desc: Sub task
"""
        sub_taskfile.write_text(sub_content)

        repo = TaskFileRepository(path=str(main_taskfile))
        tasks = repo.read_tasks()

        assert len(tasks) == 2
        assert any(t.name == "main" for t in tasks)
        assert any(t.name == "sub-task" and t.prefix == "sub" for t in tasks)

    def test_read_tasks_with_remote_includes_skipped(self, tmp_path):
        """Test that remote includes (https://) are skipped."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_content = """
includes:
  remote: https://example.com/Taskfile.yml
tasks:
  local-task:
    desc: Local task
"""
        taskfile_path.write_text(taskfile_content)

        repo = TaskFileRepository(path=str(taskfile_path))
        tasks = repo.read_tasks()

        # Only local task should be present, remote include is skipped
        assert len(tasks) == 1
        assert tasks[0].name == "local-task"

    def test_read_empty_taskfile(self, tmp_path):
        """Test reading a Taskfile with no tasks or includes."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_content = """
tasks: {}
includes: {}
"""
        taskfile_path.write_text(taskfile_content)

        repo = TaskFileRepository(path=str(taskfile_path))
        taskfile = repo._read()

        assert len(taskfile.tasks) == 0
        assert len(taskfile.includes) == 0

    def test_read_taskfile_with_dict_format_requires(self, tmp_path):
        """Test reading a Taskfile with dict format requires (name and enum)."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_content = """
tasks:
  deploy:
    desc: Deploy to environment
    requires:
      vars:
        - name: ENV
          enum: [dev, beta, prod]
"""
        taskfile_path.write_text(taskfile_content)

        repo = TaskFileRepository(path=str(taskfile_path))
        taskfile = repo._read()

        assert len(taskfile.tasks) == 1
        assert taskfile.tasks[0].name == "deploy"
        assert taskfile.tasks[0].desc == "Deploy to environment"
        assert taskfile.tasks[0].requires == {"vars": [{"name": "ENV", "enum": ["dev", "beta", "prod"]}]}
        # Test that gen_buffer works correctly with dict format
        buffer = taskfile.tasks[0].gen_buffer()
        assert "ENV=dev|beta|prod" in buffer
        assert "task deploy" in buffer

    def test_read_taskfile_with_mixed_format_requires(self, tmp_path):
        """Test reading a Taskfile with mixed format requires (both string and dict)."""
        taskfile_path = tmp_path / "Taskfile.yml"
        taskfile_content = """
tasks:
  deploy:
    desc: Deploy to environment
    requires:
      vars:
        - VAR1
        - name: ENV
          enum: [dev, beta, prod]
        - VAR2
"""
        taskfile_path.write_text(taskfile_content)

        repo = TaskFileRepository(path=str(taskfile_path))
        taskfile = repo._read()

        assert len(taskfile.tasks) == 1
        assert taskfile.tasks[0].name == "deploy"
        # Test that gen_buffer works correctly with mixed format
        buffer = taskfile.tasks[0].gen_buffer()
        assert "VAR1=" in buffer
        assert "ENV=dev|beta|prod" in buffer
        assert "VAR2=" in buffer
        assert "task deploy" in buffer


class TestTaskfileFinder:
    """Test cases for the TaskfileFinder class."""

    def test_init(self, tmp_path):
        """Test TaskfileFinder initialization."""
        finder = TaskfileFinder(root_dir=str(tmp_path))
        assert finder.root_dir == tmp_path

    def test_find_taskfile_yml(self, tmp_path):
        """Test finding a Taskfile.yml file."""
        taskfile = tmp_path / "taskfile.yml"
        taskfile.touch()

        finder = TaskfileFinder(root_dir=str(tmp_path))
        found = finder.find()

        assert found is not None
        assert Path(found).name == "taskfile.yml"

    def test_find_taskfile_yaml(self, tmp_path):
        """Test finding a Taskfile.yaml file."""
        taskfile = tmp_path / "taskfile.yaml"
        taskfile.touch()

        finder = TaskfileFinder(root_dir=str(tmp_path))
        found = finder.find()

        assert found is not None
        assert Path(found).name == "taskfile.yaml"

    def test_find_returns_first_match(self, tmp_path):
        """Test that find returns the first match when multiple taskfiles exist."""
        taskfile_yml = tmp_path / "taskfile.yml"
        taskfile_yaml = tmp_path / "taskfile.yaml"
        taskfile_yml.touch()
        taskfile_yaml.touch()

        finder = TaskfileFinder(root_dir=str(tmp_path))
        found = finder.find()

        assert found is not None
        # Should return the first one found based on priority order
        assert Path(found).name in ["taskfile.yml", "taskfile.yaml"]

    def test_find_no_taskfile(self, tmp_path):
        """Test finding when no Taskfile exists."""
        finder = TaskfileFinder(root_dir=str(tmp_path))
        found = finder.find()

        assert found is None

    def test_find_with_subdirectories(self, tmp_path):
        """Test that find only looks in the specified directory, not subdirectories."""
        # Create a subdirectory with a taskfile
        sub_dir = tmp_path / "subdir"
        sub_dir.mkdir()
        sub_taskfile = sub_dir / "taskfile.yml"
        sub_taskfile.touch()

        # No taskfile in root
        finder = TaskfileFinder(root_dir=str(tmp_path))
        found = finder.find()

        assert found is None

    def test_find_taskfile_uppercase_yml(self, tmp_path):
        """Test finding a Taskfile.yml file (uppercase T)."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.touch()

        finder = TaskfileFinder(root_dir=str(tmp_path))
        found = finder.find()

        assert found is not None
        assert Path(found).name == "Taskfile.yml"

    def test_find_taskfile_uppercase_yaml(self, tmp_path):
        """Test finding a Taskfile.yaml file (uppercase T)."""
        taskfile = tmp_path / "Taskfile.yaml"
        taskfile.touch()

        finder = TaskfileFinder(root_dir=str(tmp_path))
        found = finder.find()

        assert found is not None
        assert Path(found).name == "Taskfile.yaml"

    def test_find_priority_order(self, tmp_path):
        """Test that find returns taskfiles in priority order."""
        # Create all four variations
        taskfile_yaml_lower = tmp_path / "taskfile.yaml"
        taskfile_yml_lower = tmp_path / "taskfile.yml"
        taskfile_yaml_upper = tmp_path / "Taskfile.yaml"
        taskfile_yml_upper = tmp_path / "Taskfile.yml"

        taskfile_yaml_lower.touch()
        taskfile_yml_lower.touch()
        taskfile_yaml_upper.touch()
        taskfile_yml_upper.touch()

        finder = TaskfileFinder(root_dir=str(tmp_path))
        found = finder.find()

        assert found is not None
        # Should return the first one found in priority order:
        # taskfile.yaml > taskfile.yml > Taskfile.yaml > Taskfile.yml
        assert Path(found).name == "taskfile.yaml"

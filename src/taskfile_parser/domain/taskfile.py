from pydantic import BaseModel


class Include(BaseModel):
    prefix: str
    taskfile: str


class Task(BaseModel):
    desc: str
    prefix: str | None
    name: str
    requires: dict

    def gen_command(self) -> str:
        if self.prefix:
            return f"{self.prefix}:{self.name}"
        else:
            return self.name

    def gen_buffer(self) -> str:
        if self.requires and "vars" in self.requires:
            var_names = []
            for v in self.requires["vars"]:
                if isinstance(v, dict):
                    var_names.append(v.get("name", ""))
                else:
                    var_names.append(v)
            args = " ".join([f"{v}=" for v in var_names if v])
            return f"{args} task {self.gen_command()}" if args else f"task {self.gen_command()}"
        else:
            return f"task {self.gen_command()}"


class Taskfile(BaseModel):
    includes: list[Include]
    tasks: list[Task]

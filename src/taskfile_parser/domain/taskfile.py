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
                    # Extract 'name' from dict format; use empty string if not present
                    # Empty strings are filtered out below
                    var_names.append(v.get("name", ""))
                else:
                    var_names.append(v)
            # Filter out empty variable names and build the args string
            args = " ".join([f"{v}=" for v in var_names if v])
            if args:
                return f"{args} task {self.gen_command()}"
        return f"task {self.gen_command()}"


class Taskfile(BaseModel):
    includes: list[Include]
    tasks: list[Task]

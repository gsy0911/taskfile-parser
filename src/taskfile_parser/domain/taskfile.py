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
        vars_list = self.requires.get("vars") if self.requires else None
        if vars_list:
            var_names = []
            for v in vars_list:
                if isinstance(v, dict):
                    # Extract 'name' from dict format, only if it exists and is non-empty
                    name = v.get("name", "")
                    if name:
                        var_names.append(name)
                else:
                    var_names.append(v)
            if var_names:
                args = " ".join([f"{v}=" for v in var_names])
                return f"{args} task {self.gen_command()}"
        return f"task {self.gen_command()}"



class Taskfile(BaseModel):
    includes: list[Include]
    tasks: list[Task]

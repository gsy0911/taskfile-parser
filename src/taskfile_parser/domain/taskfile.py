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
            var_args = []
            for v in vars_list:
                if isinstance(v, dict):
                    # Extract 'name' from dict format, only if it exists and is non-empty
                    name = v.get("name", "")
                    if name:
                        # Check if enum is specified
                        enum_values = v.get("enum", [])
                        if enum_values:
                            # Join enum values with pipe separator
                            # Enum values are expected to be simple types (str, int, etc.)
                            enum_str = "|".join(str(val) for val in enum_values)
                            var_args.append(f"{name}={enum_str}")
                        else:
                            var_args.append(f"{name}=")
                else:
                    var_args.append(f"{v}=")
            if var_args:
                args = " ".join(var_args)
                return f"{args} task {self.gen_command()}"
        return f"task {self.gen_command()}"


class Taskfile(BaseModel):
    includes: list[Include]
    tasks: list[Task]

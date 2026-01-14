from os import wait
import yaml
from pydantic import BaseModel
from pathlib import Path
import argparse


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
        if self.requires:
            args = " ".join([f"{v}=" for v in self.requires["vars"]])
            return f"{args} task {self.gen_command()}"
        else:
            return f"task {self.gen_command()}"


class Taskfile(BaseModel):
    includes: list[Include]
    tasks: list[Task]

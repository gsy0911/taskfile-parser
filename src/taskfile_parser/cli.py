import argparse

from taskfile_parser.repository.repository import TaskfileFinder, TaskFileRepository


def main():
    parser = argparse.ArgumentParser(
        prog="parser",
    )

    # 引数・オプションの定義
    parser.add_argument("--pwd", type=str)
    parser.add_argument("--taskfile-task-name", type=str)
    args = parser.parse_args()

    path = TaskfileFinder(root_dir=args.pwd).find()
    task_name = args.taskfile_task_name
    if not path:
        return ""
    tasks = TaskFileRepository(path).read_tasks()
    target_task = [v for v in tasks if v.gen_command() == task_name]
    buffer = target_task[0].gen_buffer()
    return buffer


if __name__ == "__main__":
    main()

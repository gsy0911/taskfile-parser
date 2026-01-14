from taskfile_parser.domain.taskfile import Include, Task, Taskfile


class TestInclude:
    """Test cases for the Include model."""

    def test_include_creation(self):
        """Test creating an Include instance."""
        include = Include(prefix="test", taskfile="path/to/taskfile.yml")
        assert include.prefix == "test"
        assert include.taskfile == "path/to/taskfile.yml"

    def test_include_with_dict(self):
        """Test creating an Include with dictionary-like taskfile path."""
        include = Include(prefix="remote", taskfile="https://example.com/taskfile.yml")
        assert include.prefix == "remote"
        assert include.taskfile == "https://example.com/taskfile.yml"


class TestTask:
    """Test cases for the Task model."""

    def test_task_creation_without_prefix(self):
        """Test creating a Task without a prefix."""
        task = Task(
            desc="Test task description",
            prefix=None,
            name="test-task",
            requires={},
        )
        assert task.desc == "Test task description"
        assert task.prefix is None
        assert task.name == "test-task"
        assert task.requires == {}

    def test_task_creation_with_prefix(self):
        """Test creating a Task with a prefix."""
        task = Task(
            desc="Task with prefix",
            prefix="myprefix",
            name="task-name",
            requires={},
        )
        assert task.desc == "Task with prefix"
        assert task.prefix == "myprefix"
        assert task.name == "task-name"

    def test_gen_command_without_prefix(self):
        """Test generating command without prefix."""
        task = Task(
            desc="Test task",
            prefix=None,
            name="test-task",
            requires={},
        )
        assert task.gen_command() == "test-task"

    def test_gen_command_with_prefix(self):
        """Test generating command with prefix."""
        task = Task(
            desc="Test task",
            prefix="myprefix",
            name="test-task",
            requires={},
        )
        assert task.gen_command() == "myprefix:test-task"

    def test_gen_buffer_without_requires(self):
        """Test generating buffer without requirements."""
        task = Task(
            desc="Test task",
            prefix=None,
            name="test-task",
            requires={},
        )
        assert task.gen_buffer() == "task test-task"

    def test_gen_buffer_with_prefix_without_requires(self):
        """Test generating buffer with prefix but without requirements."""
        task = Task(
            desc="Test task",
            prefix="myprefix",
            name="test-task",
            requires={},
        )
        assert task.gen_buffer() == "task myprefix:test-task"

    def test_gen_buffer_with_requires(self):
        """Test generating buffer with requirements."""
        task = Task(
            desc="Test task",
            prefix=None,
            name="test-task",
            requires={"vars": ["VAR1", "VAR2"]},
        )
        buffer = task.gen_buffer()
        # The buffer should contain the variables and the task command
        assert "VAR1=" in buffer
        assert "VAR2=" in buffer
        assert "task test-task" in buffer

    def test_gen_buffer_with_prefix_and_requires(self):
        """Test generating buffer with both prefix and requirements."""
        task = Task(
            desc="Test task",
            prefix="myprefix",
            name="test-task",
            requires={"vars": ["VAR1", "VAR2"]},
        )
        buffer = task.gen_buffer()
        assert "VAR1=" in buffer
        assert "VAR2=" in buffer
        assert "task myprefix:test-task" in buffer


class TestTaskfile:
    """Test cases for the Taskfile model."""

    def test_taskfile_creation_empty(self):
        """Test creating an empty Taskfile."""
        taskfile = Taskfile(includes=[], tasks=[])
        assert taskfile.includes == []
        assert taskfile.tasks == []

    def test_taskfile_with_includes(self):
        """Test creating a Taskfile with includes."""
        includes = [
            Include(prefix="test1", taskfile="path/to/taskfile1.yml"),
            Include(prefix="test2", taskfile="path/to/taskfile2.yml"),
        ]
        taskfile = Taskfile(includes=includes, tasks=[])
        assert len(taskfile.includes) == 2
        assert taskfile.includes[0].prefix == "test1"
        assert taskfile.includes[1].prefix == "test2"

    def test_taskfile_with_tasks(self):
        """Test creating a Taskfile with tasks."""
        tasks = [
            Task(desc="Task 1", prefix=None, name="task1", requires={}),
            Task(desc="Task 2", prefix="prefix", name="task2", requires={}),
        ]
        taskfile = Taskfile(includes=[], tasks=tasks)
        assert len(taskfile.tasks) == 2
        assert taskfile.tasks[0].name == "task1"
        assert taskfile.tasks[1].name == "task2"

    def test_taskfile_with_includes_and_tasks(self):
        """Test creating a Taskfile with both includes and tasks."""
        includes = [Include(prefix="test", taskfile="path/to/taskfile.yml")]
        tasks = [Task(desc="Task 1", prefix=None, name="task1", requires={})]
        taskfile = Taskfile(includes=includes, tasks=tasks)
        assert len(taskfile.includes) == 1
        assert len(taskfile.tasks) == 1

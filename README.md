# taskfile-parser

[Taskfile](https://taskfile.dev/)のYAMLファイルをパースして、タスク情報を取得するPythonライブラリです。

## 機能

- Taskfile.yamlの読み込みと解析
- タスクの説明、変数要件の取得
- includesによる外部Taskfileの読み込みサポート
- タスク実行のためのバッファ文字列生成

## インストール

### uvxを使用する場合（推奨）

`uvx`を使用すると、インストールせずに直接実行できます：

```bash
# リポジトリのパスからTaskfileを読み込んで特定のタスク情報を取得
uvx --from git+https://github.com/gsy0911/taskfile-parser parser --pwd /path/to/your/project --taskfile-task-name your-task-name
```

### pipでインストール

```bash
# GitHubから直接インストール
pip install git+https://github.com/gsy0911/taskfile-parser.git

# ローカルからインストール
pip install .
```

## 使い方

### CLIコマンド

このパッケージは`parser`コマンドを提供します。

#### 基本的な使い方

```bash
# カレントディレクトリのTaskfileから特定のタスク情報を取得
parser --pwd . --taskfile-task-name build

# 別のディレクトリのTaskfileを解析
parser --pwd /path/to/project --taskfile-task-name test
```

#### uvxを使用した実行例

```bash
# インストール不要で直接実行
uvx --from git+https://github.com/gsy0911/taskfile-parser parser --pwd . --taskfile-task-name build

# prefixが付いたタスクの場合
uvx --from git+https://github.com/gsy0911/taskfile-parser parser --pwd . --taskfile-task-name backend:build
```

### CLIオプション

- `--pwd`: Taskfileを検索するディレクトリパス（必須）
- `--taskfile-task-name`: 取得したいタスクの名前（必須）

### 出力例

変数が必要なタスクの場合、実行に必要なコマンドバッファが出力されます：

```bash
$ uvx --from git+https://github.com/gsy0911/taskfile-parser parser --pwd . --taskfile-task-name deploy
ENV= task deploy
```

この出力は、`ENV`変数を設定してタスクを実行するためのコマンドテンプレートです。

### Pythonライブラリとして使用

```python
from taskfile_parser.repository.repository import TaskfileFinder, TaskFileRepository

# Taskfileを検索
finder = TaskfileFinder(root_dir="/path/to/project")
taskfile_path = finder.find()

# Taskfileを読み込んでタスクを取得
if taskfile_path:
    repo = TaskFileRepository(path=taskfile_path)
    tasks = repo.read_tasks()
    
    # タスク情報を表示
    for task in tasks:
        print(f"Task: {task.gen_command()}")
        print(f"Description: {task.desc}")
        print(f"Buffer: {task.gen_buffer()}")
```

## サポートされるTaskfile形式

### 基本的なタスク定義

```yaml
tasks:
  build:
    desc: アプリケーションをビルド
  test:
    desc: テストを実行
```

### 変数が必要なタスク

```yaml
tasks:
  deploy:
    desc: 環境にデプロイ
    requires:
      vars:
        - ENV
        - REGION
```

### 辞書形式の変数定義

```yaml
tasks:
  deploy:
    desc: 環境にデプロイ
    requires:
      vars:
        - name: ENV
          enum: [dev, beta, prod]
```

### 外部Taskfileの読み込み

```yaml
includes:
  backend: ./backend/Taskfile.yml
  frontend:
    taskfile: ./frontend/Taskfile.yml

tasks:
  all:
    desc: すべてのタスクを実行
```

includesで読み込んだタスクは`prefix:task-name`の形式でアクセスできます（例：`backend:build`）。

## 開発

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/gsy0911/taskfile-parser.git
cd taskfile-parser

# 依存関係をインストール
uv sync
```

### テスト実行

```bash
# すべてのテストを実行
uv run pytest

# 特定のテストファイルを実行
uv run pytest tests/repository/test_repository.py

# カバレッジ付きで実行
uv run pytest --cov=taskfile_parser
```

### コードフォーマット・リント

```bash
# フォーマット
uv run ruff format

# リント
uv run ruff check

# 自動修正
uv run ruff check --fix
```

## 対応しているTaskfileの検索パターン

以下の名前のファイルを優先順位順に検索します：

1. `taskfile.yaml`
2. `taskfile.yml`
3. `Taskfile.yaml`
4. `Taskfile.yml`

## 制限事項

- リモートinclude（`https://`で始まるURL）は現在サポートされていません
- ネストされたincludeは1階層のみサポート

## ライセンス

MIT License

## 作者

gsy0911
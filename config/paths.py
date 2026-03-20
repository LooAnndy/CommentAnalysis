from pathlib import Path

# base path: CommentAnalyzer
# resolve保证绝对路径
BASE_DIR = Path(__file__).resolve().parent.parent

# 创建data目录（如果不存在）
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

PROGRESS_FILE = DATA_DIR / "progress.json"
COOKIE_FILE = DATA_DIR / "cookies.json"

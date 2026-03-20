import json
import os.path
from config.paths import PROGRESS_FILE
from typing import Optional, Dict, Any


class ProgressManager:
    def __init__(self):
        pass

    @staticmethod
    def save_progress(bv, data):
        progress = {}

        # 如果文件存在先读取
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE) as f:
                progress = json.load(f)

        # 更新当前BV
        progress[bv] = data

        # 写回文件
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress, f, indent=4)

        print("json has been dumped")

    @staticmethod
    def load_progress(bv: str):

        try:
            with open(PROGRESS_FILE) as f:
                progress = json.load(f)

            return progress.get(bv)

        except FileNotFoundError:
            return None

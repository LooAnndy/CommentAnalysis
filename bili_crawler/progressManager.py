import json
import os.path


class ProgressManager:
    def __init__(self):
        pass

    def save_progress(self, bv, data):
        progress = {}

        # 如果文件存在先读取
        if os.path.exists("progress.json"):
            with open("progress.json") as f:
                progress = json.load(f)

        # 更新当前BV
        progress[bv] = data

        # 写回文件
        with open("progress.json", "w") as f:
            json.dump(progress, f, indent=4)

        print("json has been dumped")

    def load_progress(self, bv):

        try:
            with open("progress.json") as f:
                progress = json.load(f)

            return progress.get(bv)

        except FileNotFoundError:
            return None

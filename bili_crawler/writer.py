import csv
import os
from typing import Dict, Any
from config.paths import DATA_DIR


class CommentWriter:
    """评论CSV写入器（带字段约束 + 数据校验）

    特性：
        - 固定字段 schema
        - 自动数据校验
        - 缓冲区批量写入
        - 支持 with 上下文
    """

    def __init__(self, file_name: str, append: bool = True):
        self.buffer = []
        self.batch_size = 5000

        # 固定字段（写入顺序）
        self.fields = ["user", "comment", "likes", "time"]

        file_name = DATA_DIR / file_name
        file_is_exist = os.path.exists(file_name)

        mode = "a" if append else "w"
        self.stream = open(file_name, mode, newline="", encoding="utf-8-sig")
        self.writer = csv.writer(self.stream)

        # 写入表头
        if not file_is_exist or not append:
            self.writer.writerow(self.fields)

    # 写入文件
    def write(self, row: Dict[str, Any]):
        """写入一条评论（带校验）

        Args:
            row (dict):
                必须包含字段：
                user, comment, likes, time
        """

        # 校验字段完整性
        for field in self.fields:
            if field not in row:
                raise ValueError(f"缺少字段: {field}")

        # 类型校验
        self._validate(row)

        # 顺序写入
        formatted_row = [row[field] for field in self.fields]

        self.buffer.append(formatted_row)

        if len(self.buffer) >= self.batch_size:
            self._flush_buffer()

    # 数据校验
    @staticmethod
    def _validate(row: Dict[str, Any]):
        """数据校验"""

        if not isinstance(row["user"], str):
            raise TypeError("user 必须是 str")

        if not isinstance(row["comment"], str):
            raise TypeError("comment 必须是 str")

        if not isinstance(row["likes"], int):
            raise TypeError("likes 必须是 int")

        if not isinstance(row["time"], str):
            raise TypeError("time 必须是 str")

        # 简单时间格式检查
        if len(row["time"]) < 10:
            raise ValueError("time 格式异常")

    # 写入磁盘
    def _flush_buffer(self):
        if not self.buffer:
            return

        self.writer.writerows(self.buffer)
        self.stream.flush()
        self.buffer.clear()

    def close(self):
        self._flush_buffer()
        self.stream.close()
        print("successfully closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
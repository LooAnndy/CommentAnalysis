import csv
import os
from typing import Dict, Any
from config.paths import DATA_DIR


class CommentWriter:
    """评论CSV写入器（已更新字段以匹配 B 站评论数据）"""

    def __init__(self, file_name: str, append: bool = True):
        self.buffer = []
        self.batch_size = 5000

        # 1. 更新固定字段顺序（对应你传入 write 的 key）
        self.fields = [
            "rpid", "mid", "user", "level", "location",
            "comment", "likes", "replies", "time", "root", "parent"
        ]

        file_path = DATA_DIR / file_name
        file_is_exist = os.path.exists(file_path)

        mode = "a" if append else "w"
        # 使用 utf-8-sig 确保 Excel 打开不乱码
        self.stream = open(file_path, mode, newline="", encoding="utf-8-sig")
        self.writer = csv.writer(self.stream)

        # 写入表头
        if not file_is_exist or not append:
            self.writer.writerow(self.fields)

    def write(self, row: Dict[str, Any]):
        """写入一条评论"""
        # 校验字段完整性
        for field in self.fields:
            if field not in row:
                raise ValueError(f"缺少字段: {field}")

        # 数据类型校验
        self._validate(row)

        # 按照 fields 定义的顺序提取数据
        formatted_row = [row[field] for field in self.fields]
        self.buffer.append(formatted_row)

        if len(self.buffer) >= self.batch_size:
            self._flush_buffer()

    @staticmethod
    def _validate(row: Dict[str, Any]):
        # 字符串类型校验
        for str_field in ["user", "comment", "location", "time"]:
            if not isinstance(row[str_field], str):
                # 尝试强制转字符串，防止因为 None 或其他类型崩溃
                row[str_field] = str(row[str_field])

        # 整数类型转换与校验
        for int_field in ["rpid", "mid", "level", "likes", "replies", "root", "parent"]:
            try:
                # 只要能转换成整数，就通过校验并更新原数据
                row[int_field] = int(row[int_field])
            except (ValueError, TypeError):
                raise TypeError(f"{int_field} 无法转换为数字类型，当前值: {row[int_field]}")

        if len(row["time"]) < 10:
            raise ValueError("time 格式异常")

    def _flush_buffer(self):
        if not self.buffer:
            return
        self.writer.writerows(self.buffer)
        self.stream.flush()
        self.buffer.clear()

    def close(self):
        self._flush_buffer()
        self.stream.close()
        print(f"数据已成功保存，连接已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
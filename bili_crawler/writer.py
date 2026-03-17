import csv
import json
import os.path

class CommentWriter:

    def __init__(self, file_name, append=True):

        self.buffer = []
        self.BATCH_SIZE = 5000

        # check if file is existed
        file_is_exist = os.path.exists(file_name)

        read_type = "a" if append else "w"
        self.stream = open(file_name, read_type, newline="", encoding="utf-8-sig")
        self.writer = csv.writer(self.stream)

        # start new file
        if not file_is_exist or not append:
            self.writer.writerow(["user", "comment", "likes", "time"])

    def write(self, user, comment, like, time):

        self.buffer.append([user, comment, like, time])

        if len(self.buffer) >= self.BATCH_SIZE:
            self._flush_buffer()

    def _flush_buffer(self):

        if not self.buffer:
            return

        self.writer.writerows(self.buffer)
        self.stream.flush()
        self.buffer.clear()

    def close(self):

        # 写入剩余的数据
        self._flush_buffer()

        self.stream.close()

        print("successfully closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

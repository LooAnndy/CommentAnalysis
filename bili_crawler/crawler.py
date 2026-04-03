import requests
import time
import random
import math
import json
from typing import Dict, Any, Tuple, Optional

from config.paths import COOKIE_FILE

from .utils import bv2av, safe_get, graceful_shutdown
from .writer import CommentWriter
from .progressManager import ProgressManager


class BiliCrawler:
    """
    B站视频评论爬虫
    支持：
    - 主评论爬取
    - 楼中楼评论爬取
    - 断点续爬 (实现比较粗糙，有少量评论会重复爬取）
    """
    def __init__(self, bv, progress_callback=None):
        """
        初始化爬虫

        Args:
            bv (str): 视频BV号
            progress_callback (func): 进度反馈函数
        """
        self.bv = bv
        self.progress_callback = progress_callback

        # read cookie
        with open(COOKIE_FILE, "r") as f:
            self.cookie = json.load(f)
        print(self.cookie)

        self.aid = bv2av(bv)
        self.session = requests.Session()
        # 不使用外部的代理
        self.session.trust_env = False
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        })
        self.session.cookies.update(self.cookie)
        # 每页楼中楼评论数量
        self.ps = 20

        # 爬虫状态
        self.state: Dict[str, Any] = {
            "next_page": 1,                # 当前主评论页
            "total_comments": 0,              # 评论总数（运行时爬取）
            "comments_have_fetched": 0,    # 已爬评论数
            "last_rpid": 0,                # 最后一个评论ID
            "sub_progress": None           # dict, 楼中楼进度
        }

        # 主评论API
        self.url_main = "https://api.bilibili.com/x/v2/reply/main"
        # 楼中楼API
        self.url_reply = "https://api.bilibili.com/x/v2/reply/reply"

    def report_progress(self):
        if not self.progress_callback:
            return

        total = self.state.get("total_comments", 0)
        fetched = self.state.get("comments_have_fetched", 0)

        percent = int(100 * fetched / total) if total > 0 else 0
        self.progress_callback(self.bv, fetched, total, percent)

    def fetch_page(self, writer: CommentWriter, url: str, params: dict) -> Tuple[dict, bool]:
        """
        爬取一页评论

        Args:
            writer (CommentWriter): CSV写入器
            url (str): 请求API地址
            params (dict): 请求参数

        Returns:
            tuple:
                sub_replies (dict): 楼中楼评论信息
                has_page (bool): 是否还有数据
        """
        r = safe_get(self.session, url, params)

        data = r.json()

        # 获取评论列表
        replies = data.get("data", {}).get("replies")

        if not replies:
            return {}, False

        # 楼中楼评论
        sub_replies = {}

        for reply in replies:
            # 评论ID
            rpid = reply["rpid"]

            # 用户名
            user = reply["member"]["uname"]

            # 评论内容
            message = reply["content"]["message"]

            # 点赞数
            like = reply["like"]

            # 评论时间
            timestamp = reply["ctime"]
            comment_time = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(timestamp)
            )

            # 写入爬取数据
            writer.write({
                "user": user,
                "comment": message,
                "likes": like,
                "time": comment_time
            })

            self.state["comments_have_fetched"] += 1
            # 更新进度
            self.report_progress()
            self.state["last_rpid"] = rpid

            # 楼中楼评论的数量
            if reply.get("count"):
                sub_replies[rpid] = reply["count"]

        return sub_replies, True

    @graceful_shutdown
    def run(self):
        """运行爬虫主流程

        功能：
            1. 获取总评论数
            2. 加载断点进度
            3. 爬取主评论
            4. 爬取楼中楼评论
            5. 保存进度
        """
        self.manager = ProgressManager()
        self.writer = CommentWriter(f"{self.bv}.csv")
        try:
            # 获取评论总数
            data = safe_get(self.session, self.url_main, {
                "next": 1,
                "type": 1,
                "oid": self.aid,
                "mode": 3  # time order
            }).json()
            self.state["total_comments"] = data["data"]["cursor"]["all_count"]

            print(f"总共有 {self.state['total_comments']} 条评论")
            # 初始化进度
            self.report_progress()

            # 加载断点进度
            rom = self.manager.load_progress(self.bv)
            if rom:
                self.state = rom
                print("loaded ", rom)
            else:
                self.state["next_page"] = 1
                self.state["comments_have_fetched"] = 0
                self.state["last_rpid"] = -1
                self.state["sub_progress"] = None

            while True:
                sub_replies, has_page = self.fetch_page(self.writer, self.url_main, {
                    "next": self.state["next_page"],
                    "type": 1,
                    "oid": self.aid,
                })

                if not has_page:
                    break

                # 处理楼中楼
                for rpid, count in sub_replies.items():

                    print("发现楼中楼:", count)
                    total_comments = math.ceil(count / max(1.0, self.ps))

                    start_pn = 1
                    if self.state["sub_progress"] and self.state["sub_progress"].get("root") == rpid:
                        start_pn = self.state["sub_progress"]["pn"] + 1

                    for pn in range(start_pn, total_comments + 1):

                        self.fetch_page(self.writer, self.url_reply, {
                            "type": 1,
                            "oid": self.aid,
                            "ps": self.ps,
                            "pn": pn,
                            "root": rpid,
                            "mode": 3
                        })

                        self.state["sub_progress"] = {
                            "root": rpid,
                            "pn": pn,
                        }

                        time.sleep(random.uniform(0.2, 0.5))

                self.state["next_page"] += 1
                self.state["sub_progress"] = None

                print("当前已爬:", self.state["comments_have_fetched"])

                time.sleep(random.uniform(0.7, 1.2))

            print("爬取完成，总评论:", self.state["comments_have_fetched"])

        except Exception as e:

            print("\n爬虫异常:", e)

            # 打印错误堆栈
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # BV号
    BV = "BV1KxNPzSEhF"
    crawler = BiliCrawler(BV)
    crawler.run()

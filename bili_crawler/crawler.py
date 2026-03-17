import requests
import time
import random
import math

from utils import bv2av, safe_get
from writer import CommentWriter
from progressManager import ProgressManager

# cookie
with open("cookies.txt", "r") as f:
    cookie = f.read().strip()

class BiliCrawler:

    def __init__(self, bv):

        self.bv = bv
        self.aid = bv2av(bv)
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Cookie": cookie
        })

        self.ps = 1
        self.total_comments = 0
        self.state = {
            "next_page": 1,
            "comments_have_fetched": 0,
            "last_rpid": 0,
            "sub_progress": None
        }

        # API
        self.url_main = "https://api.bilibili.com/x/v2/reply/main"
        # 楼中楼api
        self.url_reply = "https://api.bilibili.com/x/v2/reply/reply"

    # return inner comment count
    def fetch_page(self, writer, url, params):
        r = safe_get(self.session, url, params)

        data = r.json()
        # print(json.dumps(data, ensure_ascii=False, indent=4))

        replies = data.get("data", {}).get("replies")

        if not replies:
            return {}, False

        sub_replies = {}

        for reply in replies:
            rpid = reply["rpid"]

            user = reply["member"]["uname"]
            message = reply["content"]["message"]
            like = reply["like"]

            timestamp = reply["ctime"]
            comment_time = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(timestamp)
            )
            print("comment_time: ", comment_time)
            writer.write(user, message, like, comment_time)

            self.state["comments_have_fetched"] += 1
            self.state["last_rpid"] = rpid

            if reply.get("count"):
                sub_replies[rpid] = reply["count"]

        return sub_replies, True

    def run(self):
        manager = ProgressManager()
        writer = CommentWriter(f"bilibili_comments_{self.bv}.csv")
        try:
            # 获取评论总数
            data = safe_get(self.session, self.url_main, {
                "next": 1,
                "type": 1,
                "oid": self.aid,
                "mode": 3  # time order
            }).json()
            self.total_comments = data["data"]["cursor"]["all_count"]
            # print(json.dumps(data, ensure_ascii=False, indent=4))

            print(f"总共有 {self.total_comments} 条评论")

            # load pre data
            rom = manager.load_progress(self.bv)
            if rom:
                self.state = rom
                print("loaded ", rom)
            else:
                self.state = {
                    "next_page": 1,
                    "comments_have_fetched": 0,
                    "last_rpid": -1,
                    "sub_progress": None
                }

            while True:
                sub_replies, has_page = self.fetch_page(writer, self.url_main, {
                    "next": self.state["next_page"],
                    "type": 1,
                    "oid": self.aid,
                })

                if not has_page:
                    print("booom")
                    break

                # 二级评论
                for rpid, count in sub_replies.items():

                    print("发现楼中楼:", count)
                    total_pages = math.ceil(count / max(1.0, self.ps))

                    for pn in range(1, total_pages + 1):

                        data = self.fetch_page(writer, self.url_reply, {
                            "type": 1,
                            "oid": self.aid,
                            "ps": self.ps,
                            "pn": pn,
                            "root": rpid,
                            "mode": 3
                        })

                        # print("inner state :", data)
                        self.state["sub_progress"] = {
                            "root": rpid,
                            "pn": pn,
                        }

                        time.sleep(random.uniform(0.2, 0.5))

                self.state["next_page"] += 1
                print("当前已爬:", self.state["comments_have_fetched"])

                self.state["sub_progress"] = None
                time.sleep(random.uniform(0.7, 1.2))

            print("爬取完成，总评论:", self.state["comments_have_fetched"])

        except Exception as e:

            print("\n爬虫异常:", e)

            # 打印错误堆栈
            import traceback
            traceback.print_exc()
        finally:
            manager.save_progress(self.bv, self.state)
            writer.close()


if __name__ == "__main__":
    # BV号
    BV = "BV1KxNPzSEhF"
    crawler = BiliCrawler(BV)
    crawler.run()

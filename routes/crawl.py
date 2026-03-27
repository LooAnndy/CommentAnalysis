from flask import Blueprint, request, send_file
import threading
from queue import Queue
import time

from config.paths import DATA_DIR

crawl_bp = Blueprint("crawl", __name__, url_prefix="/crawl")

task_queue = Queue()   # 任务队列
BV_progress = {}       # 进度表
current_BV = None      # 当前爬取的BV号


def update_progress(bv, fetched, total, percent):
    """
    更新特定BV任务进度
    """
    BV_progress[bv] = {
        "fetched": fetched,
        "total": total,
        "percent": percent,
        "status": "running" if fetched < total else "done"
    }


def background_worker():
    """
    独立后台线程，无限从队列取任务执行
    """
    global current_BV

    from bili_crawler import BiliCrawler
    while True:
        try:
            # 从队列拿一个任务（没有任务就阻塞等待）
            current_BV = None
            bv = task_queue.get()
            current_BV = bv

            # 开始执行爬虫
            crawler = BiliCrawler(bv, update_progress)
            crawler.run()

            # 标记任务完成
            task_queue.task_done()
        except Exception as e:
            print(f"后台线程异常: {e}")
            time.sleep(1)


# 启动任务队列
def start_background_thread():
    threading.Thread(target=background_worker, daemon=True).start()


@crawl_bp.route("/start", methods=["POST"])
def start_crawl():
    bv = request.form.get("bv")
    if not bv:
        return {"error": "请输入BV号"}

    # 初始化进度
    BV_progress[bv] = {
        "fetched": 0,
        "total": 1,
        "percent": 0,
        "status": "running"
    }
    # 新加入BV号
    task_queue.put(bv)

    if task_queue.qsize() <= 1:
        return {"msg": "started"}
    return {"msg": "queued"}


# 返回当前爬取BV的进度
@crawl_bp.route("/progress")
def get_progress():
    #  current_BV 是否存在、是否有效
    if current_BV is None or current_BV not in BV_progress:
        return {
            "current_BV": None,
            "fetched": 0,
            "total": 0,
            "percent": 0,
            "status": "idle"  # 空闲状态
        }

    return {
        "current_BV": current_BV,
        **BV_progress[current_BV]
    }


@crawl_bp.route("/download", methods=["GET"])
def download():
    """
        Args:
        bv (str): form参数，视频BV号

    Returns:
        Response:
            文件下载流（CSV文件）

        str:
            错误信息（当BV为空或文件生成失败时）


    Raises:
        error:
            - 请输入 BV 号: 未提供BV参数
            - 文件生成失败: 爬虫未成功生成CSV文件
    """
    import os

    bv = request.args.get("bv")
    filename = DATA_DIR / f"{bv}.csv"

    if not os.path.exists(filename):
        return {"error": "文件不存在"}

    return send_file(
        str(filename),
        as_attachment=True,
        download_name=filename.name
    )
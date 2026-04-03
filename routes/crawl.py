from flask import Blueprint, request, send_file
import threading
from queue import Queue
import time
import atexit

from config.paths import DATA_DIR

crawl_bp = Blueprint("crawl", __name__, url_prefix="/crawl")

task_queue = Queue()   # 任务队列
BV_progress = {}       # 进度表
current_BV = None      # 当前爬取的BV号
current_crawler = None  # 当前运行的爬虫实例


def _cleanup_on_exit():
    """Flask 退出时保存当前爬虫进度"""
    global current_crawler
    if current_crawler is not None:
        print("\nFlask 退出，正在保存爬虫进度...")
        try:
            if hasattr(current_crawler, 'manager') and hasattr(current_crawler, 'state'):
                current_crawler.manager.save_progress(current_crawler.bv, current_crawler.state)
                print("进度已保存")
            if hasattr(current_crawler, 'writer'):
                current_crawler.writer.close()
                print("CSV已关闭")
        except Exception as e:
            print(f"⚠ 保存失败: {e}")


# 注册退出钩子
atexit.register(_cleanup_on_exit)


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
    global current_BV, current_crawler

    from bili_crawler import BiliCrawler
    while True:
        try:
            # 从队列拿一个任务（没有任务就阻塞等待）
            current_BV = None
            current_crawler = None
            bv = task_queue.get()
            current_BV = bv

            # 开始执行爬虫
            current_crawler = BiliCrawler(bv, update_progress)
            current_crawler.run()

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
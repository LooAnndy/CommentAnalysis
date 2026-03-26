from flask import Blueprint, request, send_file
import threading
from config.paths import DATA_DIR

crawl_bp = Blueprint("crawl", __name__, url_prefix="/crawl")

BV_progress = {}


def update_progress(bv, fetched, total, percent):
    BV_progress[bv] = {
        "fetched": fetched,
        "total": total,
        "percent": percent,
        "status": "running" if fetched < total else "done"
    }


@crawl_bp.route("/start", methods=["POST"])
def start_crawl():
    from bili_crawler import BiliCrawler

    print("start crawl")
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

    def task():
        crawler = BiliCrawler(bv, update_progress)
        crawler.run()
    # 后端非阻塞，保证可以看得到进度
    threading.Thread(target=task).start()

    return {"msg": "started"}


@crawl_bp.route("/progress")
def get_progress():
    bv = request.args.get("bv")

    if bv not in BV_progress:
        return {"error": "no task"}

    return BV_progress[bv]


@crawl_bp.route("/download")
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
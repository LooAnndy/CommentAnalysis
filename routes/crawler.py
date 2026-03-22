from flask import Blueprint, request, send_file
import os
from config.paths import  DATA_DIR

from bili_crawler import BiliCrawler

crawler_bp = Blueprint("crawler", __name__)

# 返回文件流
@crawler_bp.route("/crawl", methods=["POST"])
def crawl():
    #爬取接口（提交 BV 号）
    bv = request.form.get("bv")
    print(bv)
    if not bv:
        return "请输入 BV 号"

    crawler = BiliCrawler(bv)
    crawler.run()

    # 爬取文件csv
    filename = DATA_DIR / f"{bv}.csv"

    if not os.path.exists(filename):
        return "文件生成失败"

    return send_file(
        str(filename),                 # 文件路径（必须是字符串）
        as_attachment=True,            # 强制下载
        download_name=filename.name    # 下载文件名
    )
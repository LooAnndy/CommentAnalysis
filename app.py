from flask import Flask, render_template, request, send_file, redirect
import requests
from config.paths import DATA_DIR, COOKIE_FILE
import os

from bili_crawler import BiliCrawler

app = Flask(__name__)

# 首页
@app.route("/", methods=["GET"])
def index():
    if not os.path.exists(COOKIE_FILE):
        return redirect("/login")
    return render_template("index.html")


# 登录页面
@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


# 爬取接口（提交 BV 号）
@app.route("/crawl", methods=["POST"])
def crawl():
    bv = request.form.get("bv")
    if not bv:
        return "请输入 BV 号"

    crawler = BiliCrawler(bv)
    crawler.run()

    # 爬取文件csv
    filename = DATA_DIR / f"bilibili_comments_{bv}.csv"

    if not os.path.exists(filename):
        return "文件生成失败"

    return send_file(
        str(filename),                 # 文件路径（必须是字符串）
        as_attachment=True,            # 强制下载
        download_name=filename.name    # 下载文件名
    )


# 获取二维码
@app.route("/api/qrcode")
def get_qrcode():
    # B站生成二维码接口
    url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bilibili.com"
    }

    resp = requests.get(url, headers=headers)

    data = resp.json()["data"]

    return {
        "url": data["url"],
        "qrcode_key": data["qrcode_key"]
    }

# 轮询登录状态
@app.route("/api/check_login")
def check_login():
    key = request.args.get("key")

    url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
    params = {"qrcode_key": key}
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    # 如果返回html证明是被反爬虫了
    resp = requests.get(url, headers=headers , params=params)

    result = resp.json()["data"]

    code = result["code"]

    if code == 0:
        cookies = resp.cookies.get_dict()

        import json
        with open(COOKIE_FILE, "w") as f:
            json.dump(cookies, f)

        return {"status": "success"}

    elif code == 86038:
        return {"status": "expired"}

    elif code == 86101:
        return {"status": "scanned"}  # 已扫码未确认

    else:
        return {"status": "waiting"}  # 未扫码


if __name__ == "__main__":
    app.run(debug=True)

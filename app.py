from flask import Flask, render_template, request, send_file, redirect, session
import requests
from config.paths import DATA_DIR, COOKIE_FILE
import os

from bili_crawler import BiliCrawler

app = Flask(__name__)

app.secret_key = os.urandom(24)


def is_cookie_valid():
    if not os.path.exists(COOKIE_FILE):
        return False

    import json
    with open(COOKIE_FILE) as f:
        cookies = json.load(f)

    url = "https://api.bilibili.com/x/web-interface/nav"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    resp = requests.get(url, headers=headers, cookies=cookies)

    data = resp.json()

    return data.get("code") == 0

# 首页
@app.route("/", methods=["GET"])
def index():
    if not is_cookie_valid():
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


# 后端向bilibili请求二维码api
@app.route("/api/qrcode_data")
def get_qrcode():
    # B站生成二维码接口
    url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bilibili.com"
    }

    resp = requests.get(url, headers=headers)

    data = resp.json()["data"]
    session["qrcode_key"] = data["qrcode_key"]

    return {
        "url": data["url"]
    }

@app.route("/api/qrcode_image")
def qrcode_image():
    qr_url = request.args.get("url")

    import qrcode
    from io import BytesIO
    from flask import send_file

    img = qrcode.make(qr_url)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")

# 轮询登录状态
@app.route("/api/check_login")
def check_login():
    key = session.get("qrcode_key", None)

    if not key:
        return {"status": "error"}

    url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
    params = {"qrcode_key": key}
    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    # 如果返回html证明是被反爬虫了
    resp = requests.get(url, headers=headers, params=params)

    result = resp.json()["data"]
    status_code = result["code"]

    if status_code == 0:
        # 字典化
        cookies = resp.cookies.get_dict()

        import json
        with open(COOKIE_FILE, "w") as f:
            json.dump(cookies, f)

        return {"status": "success"}

    elif status_code == 86038:
        return {"status": "expired"}

    elif status_code == 86101:
        return {"status": "scanned"}  # 已扫码未确认

    else:
        return {"status": "waiting"}  # 未扫码


if __name__ == "__main__":
    app.run(debug=True)

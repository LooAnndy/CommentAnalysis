from flask import Blueprint, request, session, send_file
import requests
from config.paths import DATA_DIR, COOKIE_FILE

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/qrcode_data")
def get_qrcode():
    """
    获取B站登录二维码数据
    向B站接口请求二维码URL和key，并将key保存到session中，
    用于后续轮询登录状态。

    Returns:
        dict:
            url (str): 二维码内容（用于前端生成二维码）
    """
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


@api_bp.route("/qrcode_image")
def qrcode_image():
    """
    生成二维码图片

    根据前端传入的URL生成二维码图片并返回。

    Args:
        url (str): query参数，二维码内容

    Returns:
        Response: PNG格式图片流
    """
    qr_url = request.args.get("url")

    import qrcode
    from io import BytesIO

    img = qrcode.make(qr_url)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")


# 轮询登录状态
@api_bp.route("/check_login")
def check_login():
    """
    检查二维码登录状态

    根据session中的qrcode_key轮询B站接口，判断当前登录状态。

    Returns:
        dict:
            status (str): 登录状态
                - success: 登录成功
                - expired: 二维码过期
                - scanned: 已扫码未确认
                - waiting: 未扫码
                - error: 缺少key
    """

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

    # 状态判断来源 https://bilibiliapi.github.io/api/login/poll_qrcode.html
    if status_code == 0:
        cookies = resp.cookies.get_dict()

        import json
        with open(COOKIE_FILE, "w") as f:
            json.dump(cookies, f)

        return {"status": "success"}

    elif status_code == 86038:
        return {"status": "expired"}

    elif status_code == 86090:
        return {"status": "scanned"}  # 已扫码未确认

    else:
        return {"status": "waiting"}  # 未扫码


# 获取现有的所有bv文件名
@api_bp.route("/bv_list")
def get_bv_list():
    """
    获取已下载的BV列表
    扫描本地data目录下的CSV文件，提取BV号。

    Returns:
        list[str]: 已下载的BV号列表
    """
    file_name = list(DATA_DIR.glob("*.csv"))
    bv_name = [str(f)[-16:-4] for f in file_name]
    return bv_name


@api_bp.route("/heat_analysis", methods=["GET"])
def heat_analysis():
    """
    获取评论热度趋势（按天统计）

    根据BV号读取对应CSV文件，并统计每天评论数量。
    GET /api/heat_analysis?bv=XXX

    Args:
        bv (str): query参数，视频BV号

    Returns:
        dict:
            dates (list[str]): 日期列表
            counts (list[int]): 对应每天评论数

    Raises:
        error:
            - missing bv: 未提供BV
            - file not found: 文件不存在
            - missing time column: CSV缺少time字段
    """
    import pandas as pd
    from flask import request

    bv = request.args.get("bv")

    if not bv:
        return {"error": "missing bv"}

    file_path = DATA_DIR / f"{bv}.csv"
    if not file_path.exists():
        return {"error": "file not found"}

    df = pd.read_csv(file_path)

    # 检查字段
    if "time" not in df.columns:
        return {"error": "missing time column"}

    # 转换时间格式
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    # 去掉无效时间
    df = df.dropna(subset=["time"])

    # 按照天数排序统计评论数量
    # 每天评论数量
    daily = df.groupby(df["time"].dt.date).size()
    daily = daily.sort_index()

    return {
        "dates": [str(d) for d in daily.index],
        "counts": daily.values.tolist()
    }


# 返回文件流
@api_bp.route("/crawl", methods=["POST"])
def crawl():
    """
    执行评论爬虫并返回CSV文件

    接收前端提交的BV号，调用爬虫程序抓取评论数据，
    并将结果保存为CSV文件，最终以文件流形式返回给前端下载。

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
    from bili_crawler import BiliCrawler
    import os

    bv = request.form.get("bv")

    if not bv:
        return {"error": "请输入BV号"}

    crawler = BiliCrawler(bv)
    crawler.run()

    # 爬取文件csv
    filename = DATA_DIR / f"{bv}.csv"

    if not os.path.exists(filename):
        return {"error": "文件生成失败"}

    return send_file(
        str(filename),                 # 文件路径（必须是字符串）
        as_attachment=True,            # 强制下载
        download_name=filename.name    # 下载文件名
    )
from flask import Blueprint, request, session, send_file
import requests
from config.paths import DATA_DIR, COOKIE_FILE

api_bp = Blueprint("api", __name__, url_prefix="/api")

# 后端向bilibili请求二维码api
@api_bp.route("/qrcode_data")
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


@api_bp.route("/qrcode_image")
def qrcode_image():
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


# 获取现有的所有bv文件名
@api_bp.route("/bv_list")
def get_bv_list():
    file_name = list(DATA_DIR.glob("*.csv"))
    bv_name = [str(f)[-16:-4] for f in file_name]
    return bv_name


@api_bp.route("/heat_analysis", methods=["GET"])
def heat_analysis():
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

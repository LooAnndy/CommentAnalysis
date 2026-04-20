import json

import requests

from config.paths import COOKIE_FILE


def fetch_qrcode_data():
    url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bilibili.com",
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()["data"]


def is_cookie_valid():
    """
    检查本地Cookie是否有效
    """
    import requests
    import os

    if not os.path.exists(COOKIE_FILE):
        return False

    import json
    with open(COOKIE_FILE) as f:
        cookies = json.load(f)

    # B站用户信息接口（用于校验登录状态）
    url = "https://api.bilibili.com/x/web-interface/nav"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    resp = requests.get(url, headers=headers, cookies=cookies)

    data = resp.json()

    return data.get("code") == 0


def poll_qrcode_login(qrcode_key: str):
    url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
    params = {"qrcode_key": qrcode_key}
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    payload = resp.json()
    status_code = payload["data"]["code"]

    if status_code == 0:
        cookies = resp.cookies.get_dict()
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f)
        return "success"
    if status_code == 86038:
        return "expired"
    if status_code == 86090:
        return "scanned"
    return "waiting"

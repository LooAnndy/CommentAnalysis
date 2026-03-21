from flask import Blueprint, render_template, redirect
import requests
import os
from config.paths import COOKIE_FILE

view_bp = Blueprint("view", __name__)

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
@view_bp.route("/", methods=["GET"])
def index():
    if not is_cookie_valid():
        return redirect("/login")

    return render_template("index.html")
from flask import Blueprint, render_template, redirect
from config.paths import COOKIE_FILE

view_bp = Blueprint("view", __name__)


def is_cookie_valid():
    """
    检查本地Cookie是否有效

    从本地COOKIE_FILE读取cookies，并请求B站用户信息接口，
    判断当前登录状态是否仍然有效。

    Returns:
        bool:
            True  -> Cookie有效（已登录）
            False -> Cookie无效或文件不存在

    Raises:
        error:
            - 文件不存在: 未找到COOKIE_FILE
            - JSON解析失败: cookie文件损坏（隐含风险）
            - 请求失败: 网络异常或被反爬（隐含风险）
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


@view_bp.route("/", methods=["GET"])
def index():
    """
    首页路由

    访问首页时先检查登录状态：
    - 若Cookie无效，跳转到登录页
    - 若有效，返回主页面

    Returns:
        Response:
            - 重定向到 /login（未登录）
            - 渲染 index.html（已登录）
    """

    # 登录后跳转登录页
    if not is_cookie_valid():
        return redirect("/login")

    return render_template("index.html")
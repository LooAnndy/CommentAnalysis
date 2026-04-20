from flask import Blueprint, render_template, redirect
from services.auth_service import is_cookie_valid

view_bp = Blueprint("view", __name__)

@view_bp.route("/login")
def login():
    return render_template("login.html")

@view_bp.route("/", methods=["GET"])
def index():
    """
    首页路由
    - 重定向到 /login（未登录）
    - 渲染 index.html（已登录）
    """

    # 登录后跳转登录页
    if not is_cookie_valid():
        return redirect("/login")

    return render_template("index.html")
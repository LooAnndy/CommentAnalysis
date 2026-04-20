from io import BytesIO

import qrcode
from flask import Blueprint, request, send_file, session

from services.auth_service import fetch_qrcode_data, poll_qrcode_login

auth_api_bp = Blueprint("auth_api", __name__, url_prefix="/api")


@auth_api_bp.route("/qrcode_data")
def get_qrcode():
    data = fetch_qrcode_data()
    session["qrcode_key"] = data["qrcode_key"]
    return {"url": data["url"]}


@auth_api_bp.route("/qrcode_image")
def qrcode_image():
    qr_url = request.args.get("url")
    img = qrcode.make(qr_url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@auth_api_bp.route("/check_login")
def check_login():
    key = session.get("qrcode_key")
    if not key:
        return {"status": "error"}
    return {"status": poll_qrcode_login(key)}

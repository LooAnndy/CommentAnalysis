import os

from flask import Flask

from routes.auth import auth_bp
from routes.api import api_bp
from routes.crawler import crawler_bp
from routes.views import view_bp


app = Flask(__name__)
app.secret_key = os.urandom(24)

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(crawler_bp)
app.register_blueprint(view_bp)


if __name__ == "__main__":
    app.run(debug=True)

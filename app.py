import os
from flask import Flask

from routes.auth_api import auth_api_bp
from routes.analysis_api import analysis_api_bp
from routes.views import view_bp
from routes.crawl import crawl_bp, start_background_thread


app = Flask(__name__)

# session 秘钥，用于保存cookie
app.secret_key = os.urandom(24)

# 注册蓝图
app.register_blueprint(auth_api_bp)
app.register_blueprint(analysis_api_bp)
app.register_blueprint(view_bp)
app.register_blueprint(crawl_bp)


if __name__ == "__main__":
    # 启用爬取BV多线程
    start_background_thread()
    app.run(debug=True)

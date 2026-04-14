import json
import re
from collections import Counter

import pandas as pd
import requests
from flask import Blueprint, request, session, send_file

from config.paths import DATA_DIR, COOKIE_FILE

api_bp = Blueprint("api", __name__, url_prefix="/api")

DEFAULT_STOPWORDS = {
    "的", "了", "是", "我", "你", "他", "她", "它", "啊", "吧", "呢", "吗", "呀", "这", "那",
    "一个", "没有", "就是", "这个", "那个", "我们", "他们", "你们", "然后", "但是", "因为",
}


# 读取单个 BV 对应的 CSV，并做基础字段清洗。
def _load_bv_dataframe(bv: str):
    file_path = DATA_DIR / f"{bv}.csv"
    if not file_path.exists():
        return None

    df = pd.read_csv(file_path)
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df.dropna(subset=["time"])
    else:
        df["time"] = pd.NaT

    for col, default_val in (
        ("location", "未知"),
        ("level", -1),
        ("comment", ""),
        ("likes", 0),
        ("replies", 0),
    ):
        if col not in df.columns:
            df[col] = default_val

    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0)
    df["replies"] = pd.to_numeric(df["replies"], errors="coerce").fillna(0)
    return df


# 解析分析接口统一请求体。
def _parse_analysis_payload():
    payload = request.get_json(silent=True) or {}
    bvs = payload.get("bvs", [])
    if not isinstance(bvs, list):
        bvs = []
    bvs = [str(item).strip() for item in bvs if str(item).strip()]
    mode = payload.get("mode", "count")
    granularity = payload.get("granularity", "day")
    time_range = payload.get("time_range", None)
    if mode not in {"count", "percent"}:
        mode = "count"
    if granularity not in {"day", "hour"}:
        granularity = "day"
    return bvs, mode, granularity, time_range


# 按粒度把时间分桶：day 或 hour。
def _time_bucket(series, granularity: str):
    if granularity == "hour":
        return series.dt.floor("h")
    return series.dt.floor("d")


# 根据粒度格式化时间轴显示文本。
def _format_time_label(ts, granularity: str):
    if granularity == "hour":
        return ts.strftime("%Y-%m-%d %H:%M")
    return ts.strftime("%Y-%m-%d")


# ----------------------------
# 登录相关接口
# ----------------------------


# 获取 B 站登录二维码数据，并把 qrcode_key 存入 session。
@api_bp.route("/qrcode_data")
def get_qrcode():
    url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bilibili.com",
    }
    resp = requests.get(url, headers=headers)
    data = resp.json()["data"]
    session["qrcode_key"] = data["qrcode_key"]
    return {"url": data["url"]}


# 根据前端传入的 URL 生成二维码 PNG 图片。
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


# 轮询二维码登录状态并返回统一状态值。
@api_bp.route("/check_login")
def check_login():
    key = session.get("qrcode_key")
    if not key:
        return {"status": "error"}

    url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
    params = {"qrcode_key": key}
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, params=params)
    status_code = resp.json()["data"]["code"]

    if status_code == 0:
        cookies = resp.cookies.get_dict()
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f)
        return {"status": "success"}
    if status_code == 86038:
        return {"status": "expired"}
    if status_code == 86090:
        return {"status": "scanned"}
    return {"status": "waiting"}


# ----------------------------
# 基础数据接口
# ----------------------------


# 获取本地已下载的 BV 列表（来源：data 目录下 CSV 文件名）。
@api_bp.route("/bv_list")
def get_bv_list():
    return [path.stem for path in DATA_DIR.glob("*.csv")]


# 获取评论热度趋势（兼容旧前端：单 BV，按天统计）。
@api_bp.route("/heat_analysis", methods=["GET"])
def heat_analysis():
    bv = request.args.get("bv")
    if not bv:
        return {"error": "missing bv"}

    df = _load_bv_dataframe(bv)
    if df is None:
        return {"error": "file not found"}
    if df["time"].isna().all():
        return {"error": "missing time column"}

    daily = df.groupby(df["time"].dt.date).size().sort_index()
    return {"dates": [str(d) for d in daily.index], "counts": daily.values.tolist()}


# ----------------------------
# 分析接口（供看板调用）
# ----------------------------


# 多 BV 时间轴趋势对比接口。
@api_bp.route("/analysis/trend", methods=["POST"])
def analysis_trend():
    bvs, mode, granularity, _time_range = _parse_analysis_payload()
    if not bvs:
        return {"error": "missing bvs"}

    union_index = None
    series_cache = {}

    for bv in bvs:
        df = _load_bv_dataframe(bv)
        if df is None or df["time"].isna().all():
            continue
        grouped = df.groupby(_time_bucket(df["time"], granularity)).size().sort_index()
        series_cache[bv] = grouped
        union_index = grouped.index if union_index is None else union_index.union(grouped.index)

    if union_index is None:
        return {"x_axis": [], "series": []}

    union_index = union_index.sort_values()
    x_axis = [_format_time_label(ts, granularity) for ts in union_index]

    result_series = []
    for bv in bvs:
        grouped = series_cache.get(bv)
        if grouped is None:
            continue
        aligned = grouped.reindex(union_index, fill_value=0).astype(float)
        if mode == "percent":
            total = aligned.sum()
            values = ((aligned / total) * 100).round(2).tolist() if total > 0 else [0.0] * len(aligned)
        else:
            values = aligned.astype(int).tolist()
        result_series.append({"bv": bv, "values": values})

    return {"x_axis": x_axis, "series": result_series}


# 多 BV 地理分布对比接口。
@api_bp.route("/analysis/geo", methods=["POST"])
def analysis_geo():
    bvs, _mode, _granularity, _time_range = _parse_analysis_payload()
    if not bvs:
        return {"error": "missing bvs"}

    location_counters = {}
    all_locations = set()

    for bv in bvs:
        df = _load_bv_dataframe(bv)
        if df is None:
            continue
        counts = df["location"].fillna("未知").astype(str).value_counts()
        location_counters[bv] = counts
        all_locations.update(counts.index.tolist())

    categories = sorted(all_locations)
    series = []
    for bv in bvs:
        counts = location_counters.get(bv)
        values = [int(counts.get(location, 0)) if counts is not None else 0 for location in categories]
        series.append({"bv": bv, "values": values})

    return {"categories": categories, "series": series}


# 多 BV 词云对比接口。
@api_bp.route("/analysis/wordcloud", methods=["POST"])
def analysis_wordcloud():
    bvs, _mode, _granularity, _time_range = _parse_analysis_payload()
    if not bvs:
        return {"error": "missing bvs"}

    token_pattern = re.compile(r"[\u4e00-\u9fffA-Za-z0-9]{2,}")
    result_series = []

    for bv in bvs:
        df = _load_bv_dataframe(bv)
        if df is None:
            continue

        counter = Counter()
        for text in df["comment"].fillna("").astype(str):
            cleaned = re.sub(r"\[[^\]]+\]", " ", text)
            for token in token_pattern.findall(cleaned):
                if token in DEFAULT_STOPWORDS:
                    continue
                counter[token] += 1

        words = [{"name": word, "value": int(freq)} for word, freq in counter.most_common(80)]
        result_series.append({"bv": bv, "words": words})

    return {"series": result_series}


# 多 BV 用户等级分布对比接口。
@api_bp.route("/analysis/level", methods=["POST"])
def analysis_level():
    bvs, _mode, _granularity, _time_range = _parse_analysis_payload()
    if not bvs:
        return {"error": "missing bvs"}

    categories = [f"Lv{i}" for i in range(7)]
    series = []
    for bv in bvs:
        df = _load_bv_dataframe(bv)
        if df is None:
            continue
        levels = pd.to_numeric(df["level"], errors="coerce").fillna(-1).astype(int)
        values = [int((levels == i).sum()) for i in range(7)]
        series.append({"bv": bv, "values": values})

    return {"categories": categories, "series": series}

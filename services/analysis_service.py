import re
from collections import Counter

import pandas as pd

from config.paths import DATA_DIR

DEFAULT_STOPWORDS = {
    "的", "了", "是", "我", "你", "他", "她", "它", "啊", "吧", "呢", "吗", "呀", "这", "那",
    "一个", "没有", "就是", "这个", "那个", "我们", "他们", "你们", "然后", "但是", "因为", "回复"
}


def get_bv_list():
    return [path.stem for path in DATA_DIR.glob("*.csv")]


def load_bv_dataframe(bv: str):
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


def parse_analysis_payload(payload: dict):
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


def time_bucket(series, granularity: str):
    if granularity == "hour":
        return series.dt.floor("h")
    return series.dt.floor("d")


def format_time_label(ts, granularity: str):
    if granularity == "hour":
        return ts.strftime("%Y-%m-%d %H:%M")
    return ts.strftime("%Y-%m-%d")


def heat_analysis_for_bv(bv: str):
    df = load_bv_dataframe(bv)
    if df is None:
        return {"error": "file not found"}
    if df["time"].isna().all():
        return {"error": "missing time column"}

    daily = df.groupby(df["time"].dt.date).size().sort_index()
    return {"dates": [str(d) for d in daily.index], "counts": daily.values.tolist()}


def trend_analysis(bvs, mode: str, granularity: str):
    union_index = None
    series_cache = {}

    for bv in bvs:
        df = load_bv_dataframe(bv)
        if df is None or df["time"].isna().all():
            continue
        grouped = df.groupby(time_bucket(df["time"], granularity)).size().sort_index()
        series_cache[bv] = grouped
        union_index = grouped.index if union_index is None else union_index.union(grouped.index)

    if union_index is None:
        return {"x_axis": [], "series": []}

    union_index = union_index.sort_values()
    x_axis = [format_time_label(ts, granularity) for ts in union_index]

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


def geo_analysis(bvs):
    location_counters = {}
    all_locations = set()

    for bv in bvs:
        df = load_bv_dataframe(bv)
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


def wordcloud_analysis(bvs):
    token_pattern = re.compile(r"[\u4e00-\u9fffA-Za-z0-9]{2,}")
    result_series = []

    for bv in bvs:
        df = load_bv_dataframe(bv)
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


def level_analysis(bvs):
    categories = [f"Lv{i}" for i in range(7)]
    series = []
    for bv in bvs:
        df = load_bv_dataframe(bv)
        if df is None:
            continue
        levels = pd.to_numeric(df["level"], errors="coerce").fillna(-1).astype(int)
        values = [int((levels == i).sum()) for i in range(7)]
        series.append({"bv": bv, "values": values})

    return {"categories": categories, "series": series}

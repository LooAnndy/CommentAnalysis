from flask import Blueprint, request

from services.analysis_service import (
    geo_analysis,
    get_bv_list,
    heat_analysis_for_bv,
    level_analysis,
    parse_analysis_payload,
    trend_analysis,
    wordcloud_analysis,
)

analysis_api_bp = Blueprint("analysis_api", __name__, url_prefix="/api")


@analysis_api_bp.route("/bv_list")
def bv_list():
    return get_bv_list()


@analysis_api_bp.route("/heat_analysis", methods=["GET"])
def heat_analysis():
    bv = request.args.get("bv")
    if not bv:
        return {"error": "missing bv"}
    return heat_analysis_for_bv(bv)


@analysis_api_bp.route("/analysis/trend", methods=["POST"])
def analysis_trend():
    payload = request.get_json(silent=True) or {}
    bvs, mode, granularity, _time_range = parse_analysis_payload(payload)
    if not bvs:
        return {"error": "missing bvs"}
    return trend_analysis(bvs, mode, granularity)


@analysis_api_bp.route("/analysis/geo", methods=["POST"])
def analysis_geo():
    payload = request.get_json(silent=True) or {}
    bvs, _mode, _granularity, _time_range = parse_analysis_payload(payload)
    if not bvs:
        return {"error": "missing bvs"}
    return geo_analysis(bvs)


@analysis_api_bp.route("/analysis/wordcloud", methods=["POST"])
def analysis_wordcloud():
    payload = request.get_json(silent=True) or {}
    bvs, _mode, _granularity, _time_range = parse_analysis_payload(payload)
    if not bvs:
        return {"error": "missing bvs"}
    return wordcloud_analysis(bvs)


@analysis_api_bp.route("/analysis/level", methods=["POST"])
def analysis_level():
    payload = request.get_json(silent=True) or {}
    bvs, _mode, _granularity, _time_range = parse_analysis_payload(payload)
    if not bvs:
        return {"error": "missing bvs"}
    return level_analysis(bvs)

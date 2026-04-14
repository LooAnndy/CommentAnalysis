/**
 * API 层：统一封装前端对 Flask 接口的调用。
 * 约定：这里只处理 HTTP 细节和错误抛出，不放业务分支判断。
 */

// 后端统一返回 JSON；非 2xx 交给上层捕获并展示提示。
async function parseJsonResponse(response) {
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "请求失败");
    }
    return data;
}

// 通用 POST JSON 方法，供分析类接口复用。
async function postJson(url, payload) {
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    return parseJsonResponse(res);
}

// 获取本地已缓存的 BV 列表（来自 data/*.csv）。
export async function fetchBvList() {
    const res = await fetch("/api/bv_list");
    return parseJsonResponse(res);
}

// 发起抓取任务。当前接口使用 form 格式，便于兼容后端 request.form。
export async function startCrawlTask(bv) {
    const payload = new URLSearchParams({ bv });
    const res = await fetch("/crawl/start", {
        method: "POST",
        body: payload,
    });
    return parseJsonResponse(res);
}

// 查询后台 worker 当前抓取进度。
export async function fetchCrawlProgress() {
    const res = await fetch("/crawl/progress");
    return parseJsonResponse(res);
}

// 趋势占位接口：当前仅单 BV，后续可替换为多 BV 聚合接口。
export async function fetchTrendData(bv) {
    const res = await fetch(`/api/heat_analysis?bv=${encodeURIComponent(bv)}`);
    return parseJsonResponse(res);
}

// 多 BV 趋势对比接口（时间轴热度）。
export async function fetchTrendCompareData(payload) {
    return postJson("/api/analysis/trend", payload);
}

// 多 BV 地理分布对比接口。
export async function fetchGeoCompareData(payload) {
    return postJson("/api/analysis/geo", payload);
}

// 多 BV 词云对比接口。
export async function fetchWordcloudCompareData(payload) {
    return postJson("/api/analysis/wordcloud", payload);
}

// 多 BV 用户等级分布对比接口。
export async function fetchLevelCompareData(payload) {
    return postJson("/api/analysis/level", payload);
}
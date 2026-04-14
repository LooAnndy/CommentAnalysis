async function parseJsonResponse(response) {
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "请求失败");
    }
    return data;
}

export async function fetchBvList() {
    const res = await fetch("/api/bv_list");
    return parseJsonResponse(res);
}

export async function startCrawlTask(bv) {
    const payload = new URLSearchParams({ bv });
    const res = await fetch("/crawl/start", {
        method: "POST",
        body: payload,
    });
    return parseJsonResponse(res);
}

export async function fetchCrawlProgress() {
    const res = await fetch("/crawl/progress");
    return parseJsonResponse(res);
}

export async function fetchTrendData(bv) {
    const res = await fetch(`/api/heat_analysis?bv=${encodeURIComponent(bv)}`);
    return parseJsonResponse(res);
}

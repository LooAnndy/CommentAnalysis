import { getJson, postJson } from "./client.js";

export async function fetchBvList() {
    return getJson("/api/bv_list");
}

export async function fetchTrendData(bv) {
    return getJson(`/api/heat_analysis?bv=${encodeURIComponent(bv)}`);
}

export async function fetchTrendCompareData(payload) {
    return postJson("/api/analysis/trend", payload);
}

export async function fetchGeoCompareData(payload) {
    return postJson("/api/analysis/geo", payload);
}

export async function fetchWordcloudCompareData(payload) {
    return postJson("/api/analysis/wordcloud", payload);
}

export async function fetchLevelCompareData(payload) {
    return postJson("/api/analysis/level", payload);
}

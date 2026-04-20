import { getJson, postForm } from "./client.js";

export async function startCrawlTask(bv) {
    return postForm("/crawl/start", { bv });
}

export async function fetchCrawlProgress() {
    return getJson("/crawl/progress");
}

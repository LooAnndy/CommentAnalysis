// 兼容层：保留旧导入路径，内部已按域拆分到 modules/api/*
export {
    fetchBvList,
    fetchTrendCompareData,
    fetchGeoCompareData,
    fetchWordcloudCompareData,
    fetchLevelCompareData,
    fetchTrendData,
} from "./api/analysis.js";
export { startCrawlTask, fetchCrawlProgress } from "./api/crawl.js";
export { checkLoginStatus, fetchQrcodeData, buildQrcodeImageUrl } from "./api/auth.js";
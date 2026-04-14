import { appState } from "../state.js";
import {
    fetchGeoCompareData,
    fetchLevelCompareData,
    fetchTrendCompareData,
    fetchWordcloudCompareData,
} from "../api.js";

// 看板框架通用 option：接口未返回时使用统一占位样式。
function createBaseOption(title) {
    return {
        title: { text: title, left: "center", top: 10, textStyle: { fontSize: 14 } },
        tooltip: { trigger: "axis" },
        xAxis: { type: "category", data: [] },
        yAxis: { type: "value" },
        series: [],
        grid: { left: 36, right: 18, top: 48, bottom: 28 },
    };
}

// 在固定 DOM 容器上初始化图表实例（只初始化一次）。
export function initCharts() {
    const chartTargets = {
        trend: document.getElementById("trendChart"),
        geo: document.getElementById("geoChart"),
        wordcloud: document.getElementById("wordcloudChart"),
        level: document.getElementById("levelChart"),
    };

    Object.entries(chartTargets).forEach(([key, el]) => {
        if (!el) {
            return;
        }
        // 先注册所有图表实例，后续只更新 option，避免重复 init。
        appState.chartInstances[key] = echarts.init(el);
    });
}

export function renderDashboardSkeleton() {
    // 渲染四张图的占位态，用于“无 BV”或“未请求”场景。
    if (appState.chartInstances.trend) {
        appState.chartInstances.trend.setOption(createBaseOption("时间轴热度对比（框架占位）"));
    }

    if (appState.chartInstances.geo) {
        appState.chartInstances.geo.setOption(createBaseOption("地理分布（框架占位）"));
    }

    if (appState.chartInstances.wordcloud) {
        appState.chartInstances.wordcloud.setOption(createBaseOption("词云对比（框架占位）"));
    }

    if (appState.chartInstances.level) {
        appState.chartInstances.level.setOption(createBaseOption("用户等级分布（框架占位）"));
    }
}

function buildTrendOption(data) {
    // 趋势图：兼容 x_axis/dates 两种后端命名。
    const dates = data?.x_axis || data?.dates || [];
    const series = data?.series || [];
    return {
        title: { text: "时间轴热度对比", left: "center", top: 10, textStyle: { fontSize: 14 } },
        tooltip: { trigger: "axis" },
        legend: { top: 30 },
        xAxis: { type: "category", data: dates },
        yAxis: { type: "value" },
        series: series.map((item) => ({
            name: item.bv,
            type: "line",
            smooth: true,
            data: item.values || [],
        })),
        grid: { left: 36, right: 18, top: 60, bottom: 28 },
    };
}

// 通用柱图构建器：给地理分布和等级分布复用。
function buildBarOption(title, data) {
    const categories = data?.categories || [];
    const series = data?.series || [];
    return {
        title: { text: title, left: "center", top: 10, textStyle: { fontSize: 14 } },
        tooltip: { trigger: "axis" },
        legend: { top: 30 },
        xAxis: { type: "category", data: categories },
        yAxis: { type: "value" },
        series: series.map((item) => ({
            name: item.bv || item.name,
            type: "bar",
            stack: title.includes("等级") ? "total" : undefined,
            data: item.values || [],
        })),
        grid: { left: 36, right: 18, top: 60, bottom: 28 },
    };
}

// 词云暂用“词条数量柱图”作为可视化占位，避免图表区域空白。
function buildWordcloudFallbackOption(data) {
    const categories = (data?.series || []).map((item) => item.bv || item.name);
    const values = (data?.series || []).map((item) => (item.words || []).length);
    return {
        title: { text: "词云对比（接口占位）", left: "center", top: 10, textStyle: { fontSize: 14 } },
        tooltip: { trigger: "axis" },
        xAxis: { type: "category", data: categories },
        yAxis: { type: "value" },
        series: [{ type: "bar", name: "词条数", data: values }],
        grid: { left: 36, right: 18, top: 48, bottom: 28 },
    };
}

// 统一组装四个分析接口的公共入参。
function getPayload(selectedBvs, options = {}) {
    return {
        bvs: selectedBvs,
        mode: options.mode || "count",
        granularity: options.granularity || "day",
        time_range: options.timeRange || null,
    };
}

// 并行请求四张图的数据；单个接口失败不影响其他图渲染。
export async function renderChartsWithApi(selectedBvs, options = {}) {
    if (!selectedBvs.length) {
        renderDashboardSkeleton();
        return;
    }

    const payload = getPayload(selectedBvs, options);
    const [trendRes, geoRes, wordcloudRes, levelRes] = await Promise.allSettled([
        fetchTrendCompareData(payload),
        fetchGeoCompareData(payload),
        fetchWordcloudCompareData(payload),
        fetchLevelCompareData(payload),
    ]);

    if (trendRes.status === "fulfilled" && appState.chartInstances.trend) {
        appState.chartInstances.trend.setOption(buildTrendOption(trendRes.value));
    } else if (appState.chartInstances.trend) {
        appState.chartInstances.trend.setOption(createBaseOption("时间轴热度对比（接口未就绪）"));
    }

    if (geoRes.status === "fulfilled" && appState.chartInstances.geo) {
        appState.chartInstances.geo.setOption(buildBarOption("地理分布", geoRes.value));
    } else if (appState.chartInstances.geo) {
        appState.chartInstances.geo.setOption(createBaseOption("地理分布（接口未就绪）"));
    }

    if (wordcloudRes.status === "fulfilled" && appState.chartInstances.wordcloud) {
        appState.chartInstances.wordcloud.setOption(buildWordcloudFallbackOption(wordcloudRes.value));
    } else if (appState.chartInstances.wordcloud) {
        appState.chartInstances.wordcloud.setOption(createBaseOption("词云对比（接口未就绪）"));
    }

    if (levelRes.status === "fulfilled" && appState.chartInstances.level) {
        appState.chartInstances.level.setOption(buildBarOption("用户等级分布", levelRes.value));
    } else if (appState.chartInstances.level) {
        appState.chartInstances.level.setOption(createBaseOption("用户等级分布（接口未就绪）"));
    }
}

// 窗口变化时统一 resize，避免图表容器错位。
export function resizeCharts() {
    Object.values(appState.chartInstances).forEach((chart) => chart.resize());
}

import { appState } from "../state.js";

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
        appState.chartInstances[key] = echarts.init(el);
    });
}

export function renderDashboardSkeleton() {
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

export function resizeCharts() {
    Object.values(appState.chartInstances).forEach((chart) => chart.resize());
}

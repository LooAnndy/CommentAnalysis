import { fetchBvList, fetchCrawlProgress, startCrawlTask } from "./modules/api.js";
import { addBvToSelection, appState, removeBvFromSelection } from "./modules/state.js";
import { renderSourceOptions, renderTags, updateProgress } from "./modules/ui.js";
import { initCharts, renderChartsWithApi, renderDashboardSkeleton, resizeCharts } from "./modules/charts/index.js";

/**
 * 看板页面入口脚本。
 * 负责协调：状态管理、DOM 事件、接口调用、图表渲染。
 */
const refs = {
    bvInput: document.getElementById("bvInput"),                 // BV号输入框
    addBvBtn: document.getElementById("addBvBtn"),               // 添加BV按钮
    crawlBtn: document.getElementById("crawlBtn"),               // 开始爬虫按钮
    refreshBtn: document.getElementById("refreshBtn"),           // 刷新数据按钮
    sourceSelect: document.getElementById("sourceSelect"),       // 数据源选择
    trendModeSelect: document.getElementById("trendModeSelect"), // 趋势模式选择
    timeGranularitySelect: document.getElementById("timeGranularitySelect"), // 时间粒度选择
    tagList: document.getElementById("tagList"),                 // 标签列表
    progressBox: document.getElementById("progressBox"),         // 进度条容器
    progressBar: document.getElementById("progressBar"),         // 进度条
    progressText: document.getElementById("progressText"),       // 进度文字
};

// 标签区统一从 appState 重绘，避免 UI 与状态不一致。
function syncTagView() {
    renderTags(refs.tagList, (bv) => {
        removeBvFromSelection(bv);
        syncTagView();
        renderDashboardSkeleton();
    });
}

// 拉取本地缓存 BV 列表并刷新下拉选择框。
async function loadLocalBvs() {
    try {
        const bvs = await fetchBvList();
        appState.localBvs = Array.isArray(bvs) ? bvs : [];
        renderSourceOptions(refs.sourceSelect);
    } catch (error) {
        console.error(error);
    }
}

function bindEvents() {
    // 手动输入 BV 后加入对比标签。
    refs.addBvBtn.addEventListener("click", () => {
        const bv = refs.bvInput.value.trim();
        if (!bv) {
            return;
        }
        addBvToSelection(bv);
        refs.bvInput.value = "";
        syncTagView();
    });

    // 从本地下拉选择 BV 后加入标签区。
    refs.sourceSelect.addEventListener("change", () => {
        const bv = refs.sourceSelect.value;
        if (!bv) {
            return;
        }
        addBvToSelection(bv);
        syncTagView();
    });

    // UI 选择器变更 -> 更新全局状态
    refs.trendModeSelect.addEventListener("change", () => {
        appState.trendMode = refs.trendModeSelect.value;
    });

    refs.timeGranularitySelect.addEventListener("change", () => {
        appState.granularity = refs.timeGranularitySelect.value;
    });

    // 触发抓取：优先使用第一个已选 BV，否则读取输入框。
    refs.crawlBtn.addEventListener("click", async () => {
        const targetBv = appState.selectedBvs[0] || refs.bvInput.value.trim();
        if (!targetBv) {
            return;
        }
        await startCrawlTask(targetBv);
        startProgressPolling();
    });

    // 刷新看板：按四个图表接口并行请求并分别更新图表。
    refs.refreshBtn.addEventListener("click", async () => {
        if (!appState.selectedBvs.length) {
            renderDashboardSkeleton();
            return;
        }
        try {
            await renderChartsWithApi(appState.selectedBvs, {
                mode: appState.trendMode,
                granularity: appState.granularity,
            });
        } catch (error) {
            console.error(error);
        }
    });
}

function startProgressPolling() {
    // 防止重复开启多个轮询。
    if (appState.crawlTimer) {
        window.clearInterval(appState.crawlTimer);
    }

    // 轮询后端抓取进度；任务结束后自动同步本地 BV 列表。
    appState.crawlTimer = window.setInterval(async () => {
        try {
            const progress = await fetchCrawlProgress();
            updateProgress(refs.progressBox, refs.progressBar, refs.progressText, progress);
            if (!progress.current_BV) {
                window.clearInterval(appState.crawlTimer);
                appState.crawlTimer = null;
                await loadLocalBvs();
            }
        } catch (error) {
            console.error(error);
        }
    }, 1000);
}

// 首屏初始化顺序：图表 -> 占位渲染 -> 事件 -> 本地数据 -> resize。
async function bootstrap() {
    initCharts();
    renderDashboardSkeleton();
    bindEvents();
    await loadLocalBvs();
    window.addEventListener("resize", resizeCharts);
}

bootstrap();
import { fetchBvList, fetchCrawlProgress, fetchTrendData, startCrawlTask } from "./modules/api.js";
import { addBvToSelection, appState, removeBvFromSelection } from "./modules/state.js";
import { renderSourceOptions, renderTags, updateProgress } from "./modules/ui.js";
import { initCharts, renderDashboardSkeleton, resizeCharts } from "./modules/charts/index.js";

const refs = {
    bvInput: document.getElementById("bvInput"),
    addBvBtn: document.getElementById("addBvBtn"),
    crawlBtn: document.getElementById("crawlBtn"),
    refreshBtn: document.getElementById("refreshBtn"),
    sourceSelect: document.getElementById("sourceSelect"),
    trendModeSelect: document.getElementById("trendModeSelect"),
    timeGranularitySelect: document.getElementById("timeGranularitySelect"),
    tagList: document.getElementById("tagList"),
    progressBox: document.getElementById("progressBox"),
    progressBar: document.getElementById("progressBar"),
    progressText: document.getElementById("progressText"),
};

function syncTagView() {
    renderTags(refs.tagList, (bv) => {
        removeBvFromSelection(bv);
        syncTagView();
        renderDashboardSkeleton();
    });
}

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
    refs.addBvBtn.addEventListener("click", () => {
        const bv = refs.bvInput.value.trim();
        if (!bv) {
            return;
        }
        addBvToSelection(bv);
        refs.bvInput.value = "";
        syncTagView();
    });

    refs.sourceSelect.addEventListener("change", () => {
        const bv = refs.sourceSelect.value;
        if (!bv) {
            return;
        }
        addBvToSelection(bv);
        syncTagView();
    });

    refs.trendModeSelect.addEventListener("change", () => {
        appState.trendMode = refs.trendModeSelect.value;
    });

    refs.timeGranularitySelect.addEventListener("change", () => {
        appState.granularity = refs.timeGranularitySelect.value;
    });

    refs.crawlBtn.addEventListener("click", async () => {
        const targetBv = appState.selectedBvs[0] || refs.bvInput.value.trim();
        if (!targetBv) {
            return;
        }
        await startCrawlTask(targetBv);
        startProgressPolling();
    });

    refs.refreshBtn.addEventListener("click", async () => {
        // 框架阶段仅演示调用流，不做完整多BV分析。
        const bv = appState.selectedBvs[0];
        if (!bv) {
            renderDashboardSkeleton();
            return;
        }
        try {
            await fetchTrendData(bv);
            renderDashboardSkeleton();
        } catch (error) {
            console.error(error);
        }
    });
}

function startProgressPolling() {
    if (appState.crawlTimer) {
        window.clearInterval(appState.crawlTimer);
    }

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

async function bootstrap() {
    initCharts();
    renderDashboardSkeleton();
    bindEvents();
    await loadLocalBvs();
    window.addEventListener("resize", resizeCharts);
}

bootstrap();

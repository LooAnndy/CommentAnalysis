import { appState, getBvColor } from "./state.js";

// 重绘“本地历史 BV”下拉选项。
export function renderSourceOptions(selectEl) {
    selectEl.innerHTML = '<option value="">从本地历史选择 BV</option>';
    appState.localBvs.forEach((bv) => {
        const option = document.createElement("option");
        option.value = bv;
        option.textContent = bv;
        selectEl.appendChild(option);
    });
}

/**
 * 渲染 BV 号标签列表（多彩 Tag）
 * @param {HTMLElement} tagListEl - 标签容器 DOM 元素
 * @param {Function} onRemove - 删除 BV 号的回调函数 (bv: string) => void
 */
// 选中的BV号多彩Tag渲染
// 每次全量重绘，保持渲染逻辑简单，避免增量更新复杂度。
export function renderTags(tagListEl, onRemove) {
    tagListEl.innerHTML = "";
    appState.selectedBvs.forEach((bv) => {
        const tag = document.createElement("div");
        tag.className = "tag-item";
        tag.style.backgroundColor = getBvColor(bv);
        tag.innerHTML = `<span>${bv}</span><button data-bv="${bv}" type="button">×</button>`;
        tagListEl.appendChild(tag);
    });

    // 绑定删除事件：交由外层决定删除后的联动动作。
    tagListEl.querySelectorAll("button[data-bv]").forEach((btn) => {
        btn.addEventListener("click", () => onRemove(btn.dataset.bv));
    });
}

// 渲染抓取进度条；当 current_BV 为空时表示 worker 空闲。
export function updateProgress(progressBoxEl, progressBarEl, progressTextEl, progress) {
    progressBoxEl.hidden = false;
    progressBarEl.style.width = `${progress.percent || 0}%`;
    progressTextEl.textContent = progress.current_BV
        ? `正在抓取 ${progress.current_BV}：${progress.fetched}/${progress.total} (${progress.percent}%)`
        : "任务空闲";
}
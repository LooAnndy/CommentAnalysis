import { appState, getBvColor } from "./state.js";

export function renderSourceOptions(selectEl) {
    selectEl.innerHTML = '<option value="">从本地历史选择 BV</option>';
    appState.localBvs.forEach((bv) => {
        const option = document.createElement("option");
        option.value = bv;
        option.textContent = bv;
        selectEl.appendChild(option);
    });
}

export function renderTags(tagListEl, onRemove) {
    tagListEl.innerHTML = "";
    appState.selectedBvs.forEach((bv) => {
        const tag = document.createElement("div");
        tag.className = "tag-item";
        tag.style.backgroundColor = getBvColor(bv);
        tag.innerHTML = `<span>${bv}</span><button data-bv="${bv}" type="button">×</button>`;
        tagListEl.appendChild(tag);
    });

    tagListEl.querySelectorAll("button[data-bv]").forEach((btn) => {
        btn.addEventListener("click", () => onRemove(btn.dataset.bv));
    });
}

export function updateProgress(progressBoxEl, progressBarEl, progressTextEl, progress) {
    progressBoxEl.hidden = false;
    progressBarEl.style.width = `${progress.percent || 0}%`;
    progressTextEl.textContent = progress.current_BV
        ? `正在抓取 ${progress.current_BV}：${progress.fetched}/${progress.total} (${progress.percent}%)`
        : "任务空闲";
}

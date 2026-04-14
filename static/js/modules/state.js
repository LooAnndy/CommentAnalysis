/**
 * 状态层：集中维护页面共享状态，避免状态散落在各事件回调中。
 * 原则：所有跨模块共享的数据优先放到 appState。
 */
const PALETTE = ["#2563eb", "#f97316", "#16a34a", "#7c3aed", "#0891b2", "#e11d48"];

export const appState = {
    selectedBvs: [],      // 当前参与对比的 BV 标签列表
    localBvs: [],         // 本地可选 BV（来自缓存文件）
    trendMode: "count",   // 趋势模式：绝对值 / 百分比
    granularity: "day",   // 时间粒度：day / hour
    chartInstances: {},   // ECharts 实例池
    crawlTimer: null,     // 抓取进度轮询定时器句柄
};

// 使用“字符编码求和”做稳定颜色映射，保证同一 BV 跨刷新颜色不变。
export function getBvColor(bv) {
    if (!bv) {
        return "#334155";
    }
    const sum = Array.from(bv).reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return PALETTE[sum % PALETTE.length];
}

// 去重保护：空值和已存在 BV 都不加入。
export function addBvToSelection(bv) {
    if (!bv || appState.selectedBvs.includes(bv)) {
        return;
    }
    appState.selectedBvs.push(bv);
}

// 删除指定 BV，并返回新的数组引用以便触发重绘。
export function removeBvFromSelection(bv) {
    appState.selectedBvs = appState.selectedBvs.filter((item) => item !== bv);
}
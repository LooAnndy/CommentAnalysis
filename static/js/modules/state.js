const PALETTE = ["#2563eb", "#f97316", "#16a34a", "#7c3aed", "#0891b2", "#e11d48"];

export const appState = {
    selectedBvs: [],
    localBvs: [],
    trendMode: "count",
    granularity: "day",
    chartInstances: {},
    crawlTimer: null,
};

export function getBvColor(bv) {
    if (!bv) {
        return "#334155";
    }
    const sum = Array.from(bv).reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return PALETTE[sum % PALETTE.length];
}

export function addBvToSelection(bv) {
    if (!bv || appState.selectedBvs.includes(bv)) {
        return;
    }
    appState.selectedBvs.push(bv);
}

export function removeBvFromSelection(bv) {
    appState.selectedBvs = appState.selectedBvs.filter((item) => item !== bv);
}

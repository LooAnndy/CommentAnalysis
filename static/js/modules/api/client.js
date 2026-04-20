async function parseJsonResponse(response) {
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "请求失败");
    }
    return data;
}

export async function getJson(url) {
    const res = await fetch(url);
    return parseJsonResponse(res);
}

export async function postJson(url, payload) {
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    return parseJsonResponse(res);
}

export async function postForm(url, payload) {
    const params = new URLSearchParams(payload);
    const res = await fetch(url, {
        method: "POST",
        body: params,
    });
    return parseJsonResponse(res);
}

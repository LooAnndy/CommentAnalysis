import { getJson } from "./client.js";

export async function fetchQrcodeData() {
    return getJson("/api/qrcode_data");
}

export function buildQrcodeImageUrl(url) {
    return `/api/qrcode_image?url=${encodeURIComponent(url)}`;
}

export async function checkLoginStatus() {
    return getJson("/api/check_login");
}

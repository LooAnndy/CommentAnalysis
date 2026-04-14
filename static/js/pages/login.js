// 登录页脚本：初始化二维码并轮询扫码状态。
const qrcodeEl = document.getElementById("qrcode");
const statusEl = document.getElementById("status");

// 记录轮询句柄，避免重复 setInterval。
let pollTimer = null;

// 统一更新页面状态提示文案。
function setStatus(text) {
    statusEl.innerText = text;
}

// 在重新初始化二维码或登录成功时停止旧轮询。
function stopPolling() {
    if (pollTimer) {
        window.clearInterval(pollTimer);
        pollTimer = null;
    }
}

// 查询后端保存的二维码登录状态。
async function checkLoginStatus() {
    const res = await fetch("/api/check_login");
    return res.json();
}

// 固定 2s 轮询，平衡响应速度与请求频率。
function startPolling() {
    stopPolling();
    pollTimer = window.setInterval(async () => {
        try {
            const data = await checkLoginStatus();
            if (data.status === "success") {
                setStatus("登录成功！");
                stopPolling();
                window.location.href = "/";
                return;
            }

            if (data.status === "expired") {
                setStatus("二维码过期，正在刷新...");
                stopPolling();
                await initLoginQrcode();
                return;
            }

            if (data.status === "scanned") {
                setStatus("已扫码，请在手机确认");
                return;
            }

            setStatus("等待扫码...");
        } catch (error) {
            console.error(error);
            setStatus("网络异常，请稍后重试");
        }
    }, 2000);
}

// 申请新的二维码链接，并通过本地接口生成二维码图片。
async function initLoginQrcode() {
    const res = await fetch("/api/qrcode_data");
    const data = await res.json();
    qrcodeEl.src = `/api/qrcode_image?url=${encodeURIComponent(data.url)}`;
    setStatus("等待扫码...");
    startPolling();
}

initLoginQrcode();
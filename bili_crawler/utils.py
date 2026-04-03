import time
import requests
import signal
import sys
import functools
import traceback


# BV转AV号的一些常数
XOR_CODE = 23442827791579
MASK_CODE = 2251799813685247
MAX_AID = 1 << 51
ALPHABET = "FcwAPNKTMug3GV5Lj7EJnHpWsx4tb8haYeviqBz6rkCy12mUSDQX9RdoZf"
ENCODE_MAP = 8, 7, 0, 5, 1, 3, 2, 4, 6
DECODE_MAP = tuple(reversed(ENCODE_MAP))
BASE = len(ALPHABET)
PREFIX = "BV1"
CODE_LEN = len(ENCODE_MAP)


def bv2av(bvid: str) -> int:
    """将B站BV号转换为AV号
    算法来源：
        https://sessionhu.github.io/bilibili-API-collect/docs/misc/bvid_desc.html#bv-av%E7%AE%97%E6%B3%95

    Args:
        bvid (str): B站视频BV号，例如 "BV1xx411c7mD"

    Returns:
        int: 对应的AV号

    Raises:
        AssertionError: 保证bvid前缀 "BV1"
    """
    assert bvid[:3] == PREFIX
    bvid = bvid[3:]
    tmp = 0
    for i in range(CODE_LEN):
        idx = ALPHABET.index(bvid[DECODE_MAP[i]])
        tmp = tmp * BASE + idx
    return (tmp & MASK_CODE) ^ XOR_CODE


def safe_get(session,  url, params):
    """安全请求URL，失败自动重试3次

    Args:
        session (requests.Session): requests 会话对象
        url (str): 请求的URL
        params (dict): GET请求参数

    Returns:
        requests.Response: 成功返回的响应对象

    Raises:
        Exception: 如果连续3次请求失败则抛出异常
    """
    for i in range(3):

        try:
            rep = session.get(url, params=params, timeout=10)

            if rep.status_code == 200:
                return rep

        except requests.exceptions.RequestException:
            print("请求失败，重试中...")

        time.sleep(2)

    raise Exception("请求失败3次")


def graceful_shutdown(func):
    """
    给长时间运行任务添加优雅退出能力：
    - Ctrl+C 自动保存（仅主线程）
    - kill 自动保存 (Linux/Mac，仅主线程)
    - 抛异常自动保存
    - 正常结束自动保存

    要求对象里存在：
        self.manager
        self.writer
        self.bv
        self.state
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):

        # ===== 退出信号处理函数 =====
        def _exit(signum, frame):
            print(f"\n收到退出信号({signum})，正在保存进度...")
            _save(self)
            sys.exit(0)

        # 只在主线程注册信号（子线程不支持 signal）
        import threading
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, _exit)   # Ctrl+C
            # Windows 不支持 SIGTERM
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, _exit)  # kill / 进程终止

        try:
            return func(self, *args, **kwargs)

        except Exception as e:
            print("\n程序异常退出：", e)
            traceback.print_exc()
            raise

        finally:
            print("\n执行 finally：保存进度")
            _save(self)

    return wrapper


def _save(self):
    """真正执行保存逻辑（避免重复写）"""
    try:
        if hasattr(self, "manager") and hasattr(self, "state"):
            self.manager.save_progress(self.bv, self.state)
            print("进度已保存")

        if hasattr(self, "writer"):
            self.writer.close()
            print("CSV已关闭")

    except Exception as e:
        print("⚠ 保存失败：", e)

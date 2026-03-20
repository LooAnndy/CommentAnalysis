import time
import requests
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

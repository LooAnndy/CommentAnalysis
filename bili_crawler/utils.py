import time
import requests
# BV转AV号
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
    assert bvid[:3] == PREFIX
    bvid = bvid[3:]
    tmp = 0
    for i in range(CODE_LEN):
        idx = ALPHABET.index(bvid[DECODE_MAP[i]])
        tmp = tmp * BASE + idx
    return (tmp & MASK_CODE) ^ XOR_CODE


def safe_get(session,  url, params):
    for i in range(3):

        try:
            rep = session.get(url, params=params, timeout=10)

            if rep.status_code == 200:
                return rep

        except requests.exceptions.RequestException:
            print("请求失败，重试中...")

        time.sleep(2)

    raise Exception("请求失败3次")

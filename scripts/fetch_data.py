import os
import time
import uuid
import hashlib
import json
import requests
from typing import Dict, List, Optional

# --- Xiaochan Config & Logic ---
XC_BASE_URL = "https://gw.xiaocantech.com/rpc"

def get_md5(data: str) -> str:
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def get_nami() -> str:
    u = str(uuid.uuid4()).replace("-", "")
    return u[:4] + "0" + u[4:15]

def get_ashe(server_name: str, method_name: str, time_ms: int, nami: str) -> str:
    x = get_md5(f"{server_name}.{method_name}".lower())
    return get_md5(f"{x}{time_ms}{nami}")

def fetch_xiaochan_data(city_code: int, lat: float, lng: float, token: str = "") -> List[Dict]:
    server = "SilkwormRec"
    method = "RecService.GetStorePromotionList"
    now = int(time.time() * 1000)
    nami = get_nami()
    ashe = get_ashe(server, method, now, nami)

    headers = {
        "Content-Type": "application/json",
        "servername": server,
        "methodname": method,
        "X-Ashe": ashe,
        "X-Garen": str(now),
        "X-Nami": nami,
        "x-City": str(city_code),
        "appid": "20",
        "X-Platform": "mini",
        "version": "3.15.9.10",
        "X-Version": "3.15.9.10",
        "x-Annie": "XC",
        "X-Model": "microsoft microsoft",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6309092b) XWEB/9079",
        "Referer": "https://servicewechat.com/wx52ae84595214/965/page-frame.html",
        "xweb_xhr": "1",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    if token:
        headers["token"] = token

    payload = {
        "longitude": lng,
        "latitude": lat,
        "cityCode": city_code,
        "pageIndex": 1,
        "pageSize": 20
    }

    try:
        resp = requests.post(XC_BASE_URL, headers=headers, json=payload, timeout=10)
        if resp.status_code != 200:
            print(f"Status Code: {resp.status_code}")
            print(f"Response: {resp.text}")
            return []
        data = resp.json()
        return data.get("data", {}).get("list", [])
    except Exception as e:
        print(f"Error fetching Xiaochan: {e}")
        if 'resp' in locals():
            print(f"Raw Response: {resp.text}")
        return []

if __name__ == "__main__":
    # 浠庣幆澧冨彉閲忚鍙栭厤缃?(榛樿闀挎矙)
    XC_TOKEN = os.getenv("XC_TOKEN", "")
    LAT = float(os.getenv("LAT", "28.22"))
    LNG = float(os.getenv("LNG", "112.93"))
    CITY_CODE = int(os.getenv("CITY_CODE", "430100"))

    print(f"Fetching Xiaochan data for {LAT}, {LNG}...")
    xc_data = fetch_xiaochan_data(CITY_CODE, LAT, LNG, XC_TOKEN)

    # 淇濆瓨缁撴灉
    os.makedirs("data", exist_ok=True)
    with open("data/shops.json", "w", encoding="utf-8") as f:
        json.dump({"xiaochan": xc_data, "updated_at": time.ctime()}, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(xc_data)} shops from Xiaochan.")

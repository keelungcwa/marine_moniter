import requests
import json
import os
import urllib.parse
from datetime import datetime

API_KEY = "CWA-63A8D5AE-8C97-4F9C-ADD7-BE84AE2E9276"


# ==================== 其餘設定 ====================
DATA_ID = "O-B0075-001"
WEATHER_ELEMENTS = "WaveHeight,WaveDirection,WavePeriod"
OUTPUT_JSON = "marine_data.json"

# 所有測站資訊（可自行增減）
ALL_STATION_LOCATIONS = {
    "46694A": {"name": "龍洞浮標", "unit": "中央氣象署"},
    "46699A": {"name": "花蓮浮標", "unit": "中央氣象署"},
    "46708A": {"name": "龜山島浮標", "unit": "中央氣象署"},
    "46714D": {"name": "小琉球浮標", "unit": "中央氣象署"},
    "46744A": {"name": "大鵬灣浮標", "unit": "中央氣象署"},
    "46757B": {"name": "新竹浮標", "unit": "中央氣象署"},
    "C6AH2":  {"name": "富貴角浮標", "unit": "中央氣象署"},
    "C6B01":  {"name": "彭佳嶼浮標", "unit": "中央氣象署"},
    "C6F01":  {"name": "臺中浮標", "unit": "中央氣象署"},
    "C6S62":  {"name": "臺東外洋浮標", "unit": "中央氣象署"},
    "C6S94":  {"name": "蘭嶼浮標", "unit": "中央氣象署"},
    "C6V27":  {"name": "東沙島浮標", "unit": "中央氣象署"},
    "C6W08":  {"name": "馬祖浮標", "unit": "中央氣象署"},
    "C6W10":  {"name": "七美浮標", "unit": "中央氣象署"},
    "46761F": {"name": "成功波浪站", "unit": "中央氣象署"},
    "C5W09":  {"name": "東吉島波浪站", "unit": "中央氣象署"},
    "46706A": {"name": "蘇澳浮標", "unit": "經濟部水利署"},
    "TPBU01": {"name": "臺北港浮標", "unit": "港灣技術研究中心"},
    "46778A": {"name": "七股浮標", "unit": "經濟部水利署"},
    "46735A": {"name": "澎湖浮標", "unit": "經濟部水利署"},
    "46759A": {"name": "鵝鑾鼻浮標", "unit": "經濟部水利署"},
    "WRA007": {"name": "臺東浮標", "unit": "經濟部水利署"},
    "COMC08": {"name": "彌陀浮標", "unit": "經濟部水利署"},
    "46787A": {"name": "金門浮標", "unit": "經濟部水利署"},
}

# ==================== 主要函數 ====================
def fetch_marine_data():
    station_ids = ",".join(ALL_STATION_LOCATIONS.keys())
    encoded_ids = urllib.parse.quote(station_ids)

    url = (
        f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{DATA_ID}"
        f"?Authorization={API_KEY}&format=JSON&StationID={encoded_ids}&WeatherElement={WEATHER_ELEMENTS}"
    )

    print(f"正在抓取 {len(ALL_STATION_LOCATIONS)} 個測站資料...")
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        print("API 請求成功")
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 錯誤: {e}")
        if response.status_code == 401:
            print("警告：401 Unauthorized → API Key 可能錯誤或過期")
        elif response.status_code == 400:
            print("提示：400 Bad Request → 部分站點可能不在此資料集")
        return None
    except Exception as e:
        print(f"請求失敗: {e}")
        return None


def parse_and_save(data):
    result = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S (UTC%z)"),
        "source": "中央氣象署開放資料平台",
        "total_stations": len(ALL_STATION_LOCATIONS),
        "stations": {}
    }

    # 先預設全部無資料
    for sid, info in ALL_STATION_LOCATIONS.items():
        result["stations"][sid] = {
            "name": info["name"],
            "unit": info["unit"],
            "wave_height": "-",
            "wave_direction": "-",
            "wave_period": "-",
            "obs_time": "-",
            "status": "無資料"
        }

    # 填入實際資料
    if data and data.get("success") == "true":
        records = data.get("result", {}).get("records", [])
        print(f"成功取得 {len(records)} 筆即時資料")
        
        for rec in records:
            sid = rec.get("StationID")
            if sid in ALL_STATION_LOCATIONS:
                obs_time = rec.get("ObsTime")
                if isinstance(obs_time, dict):
                    obs_time = obs_time.get("DateTime", "-")
                result["stations"][sid].update({
                    "wave_height": rec.get("WaveHeight", "-"),
                    "wave_direction": rec.get("WaveDirection", "-"),
                    "wave_period": rec.get("WavePeriod", "-"),
                    "obs_time": obs_time or "-",
                    "status": "正常"
                })

    # 寫入 JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"marine_data.json 已更新！共 {sum(1 for s in result['stations'].values() if s['status'] == '正常')} 站有資料")


# ==================== 主程式 ====================
if __name__ == "__main__":
    raw_data = fetch_marine_data()
    if raw_data:
        parse_and_save(raw_data)
    else:
        print("因 API 請求失敗，無法更新資料")

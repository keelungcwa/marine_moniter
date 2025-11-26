import requests
import os
import urllib.parse

# --- 參數設定 ---

# API Key 從環境變數讀取（安全）
#API_KEY = os.getenv("CWA_API_KEY")
API_KEY = "CWA-35C0E283-99B1-40F6-9749-3C8B23739D31"

# 輸出到專案根目錄的 marine_data.json
#OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "marine_data.json")
OUTPUT_PATH = "marine_data.json"

DATA_ID = "O-B0075-001"
WEATHER_ELEMENTS = "WaveHeight,WaveDirection,WavePeriod"

ALL_STATION_LOCATIONS = {
    "46694A": { "name": "龍洞浮標", "unit": "CWA" },
    "46699A": { "name": "花蓮浮標", "unit": "CWA" },
    "46708A": { "name": "龜山島浮標", "unit": "CWA" },
    "46714D": { "name": "小琉球浮標", "unit": "CWA" },
    "46744A": { "name": "大鵬灣浮標", "unit": "CWA" },
    "46757B": { "name": "新竹浮標", "unit": "CWA" },
    "C6AH2": { "name": "富貴角浮標", "unit": "CWA" },
    "C6B01": { "name": "彭佳嶼浮標", "unit": "CWA" },
    "C6F01": { "name": "臺中浮標", "unit": "CWA" },
    "C6S62": { "name": "臺東外洋浮標", "unit": "CWA" },
    "C6S94": { "name": "蘭嶼浮標", "unit": "CWA" },
    "C6V27": { "name": "東沙島浮標", "unit": "CWA" },
    "C6W08": { "name": "馬祖浮標", "unit": "CWA" },
    "C6W10": { "name": "七美浮標", "unit": "CWA" },
    "46761F": { "name": "成功浮球", "unit": "CWA" },
    "C5W09": { "name": "東吉島波浪站", "unit": "CWA" },

    # 新增
    "46706A": { "name": "蘇澳浮標", "unit": "水利署" },
    "TPBU01": { "name": "臺北港浮標", "unit": "港研中心" },
    "46778A": { "name": "七股浮標", "unit": "水利署" },
    "46735A": { "name": "澎湖浮標", "unit": "水利署" },
    "46759A": { "name": "鵝鑾鼻浮標", "unit": "水利署" },
    "WRA007": { "name": "臺東浮標", "unit": "水利署" },
    "COMC08": { "name": "彌陀浮標", "unit": "水利署" },
    "46787A": { "name": "金門浮標", "unit": "水利署" },
}


def download_marine_data():
    station_ids_string = ",".join(ALL_STATION_LOCATIONS.keys())
    encoded_station_ids = urllib.parse.quote(station_ids_string)

    url = (
        f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{DATA_ID}"
        f"?Authorization={API_KEY}&format=JSON&StationID={encoded_station_ids}&WeatherElement={WEATHER_ELEMENTS}"
    )

    print(f"下載中：{url}")

    try:
        response = requests.get(url, timeout=45)
        response.raise_for_status()

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"已更新 → {OUTPUT_PATH}")

    except Exception as e:
        print("下載失敗：", e)


if __name__ == "__main__":
    download_marine_data()

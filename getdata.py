import requests
import os
import urllib.parse 

# --- 參數設定 ---

# 你的 API Key (保持不變)
API_KEY = "CWA-63A8D5AE-8C97-4F9C-ADD7-BE84AE2E9276"

# 輸出目錄 (保持不變)
OUTPUT_DIR = r"D:\marine_moniter"

# API 相關設定
# 注意：CWA 的 O-B0075-001 資料集通常只包含 CWA 自行觀測的站點。
# 但根據 CWA 開放資料的設計，使用者可以嘗試透過 StationID 參數查詢其他單位協同發布的站點。
DATA_ID = "O-B0075-001"
WEATHER_ELEMENTS = "WaveHeight,WaveDirection,WavePeriod"
LOCAL_FILENAME = "marine_data.json"

# --- 欲查詢的全部測站 ID 列表 (CWA + 新增) ---
# 字典中的 Key 即為 API 請求所需的 StationID
ALL_STATION_LOCATIONS = {
    # 原始 CWA 浮標/波浪站 (16 站)
    "46694A": { "name": "龍洞浮標 (Longdong Buoy)", "unit": "CWA" },
    "46699A": { "name": "花蓮浮標 (Hualien Buoy)", "unit": "CWA" },
    "46708A": { "name": "龜山島浮標 (Guishandao Buoy)", "unit": "CWA" },
    "46714D": { "name": "小琉球浮標 (Xiao Liuqiu Buoy)", "unit": "CWA" },
    "46744A": { "name": "大鵬灣浮標 (Dapeng Bay buoy)", "unit": "CWA" }, 
    "46757B": { "name": "新竹浮標 (Hsinchu Buoy)", "unit": "CWA" },
    "C6AH2": { "name": "富貴角浮標 (Fugui Cape Buoy)", "unit": "CWA" },
    "C6B01": { "name": "彭佳嶼浮標 (Pengjiayu Buoy)", "unit": "CWA" },
    "C6F01": { "name": "臺中浮標 (Taichung Buoy)", "unit": "CWA" },
    "C6S62": { "name": "臺東外洋浮標 (Taitung Open Ocean Buoy)", "unit": "CWA" }, 
    "C6S94": { "name": "蘭嶼浮標 (Lanyu Buoy)", "unit": "CWA" },
    "C6V27": { "name": "東沙島浮標 (Pratas Buoy)", "unit": "CWA" },
    "C6W08": { "name": "馬祖浮標 (Matsu Buoy)", "unit": "CWA" },
    "C6W10": { "name": "七美浮標 (Qimei Buoy)", "unit": "CWA" },
    "46761F": { "name": "成功浮球 (Chenggong Wave Station)", "unit": "CWA" },
    "C5W09": { "name": "東吉島波浪站 (Dongjidao Wave Station)", "unit": "CWA" },

    # 新增的水利署/港研中心浮標 (8 站)
    "46706A": { "name": "蘇澳浮標", "unit": "經濟部水利署" },
    "TPBU01": { "name": "臺北港浮標", "unit": "港灣技術研究中心" },
    "46778A": { "name": "七股浮標", "unit": "經濟部水利署" },
    "46735A": { "name": "澎湖浮標", "unit": "經濟部水利署" },
    "46759A": { "name": "鵝鑾鼻浮標", "unit": "經濟部水利署" },
    "WRA007": { "name": "臺東浮標", "unit": "經濟部水利署" },
    "COMC08": { "name": "彌陀浮標", "unit": "經濟部水利署" },
    "46787A": { "name": "金門浮標", "unit": "經濟部水利署" },
}

# --- 核心 API 呼叫函數 ---

def download_marine_data(api_key, output_dir, data_id, elements, station_ids, filename):
    """
    呼叫指定的海象觀測資料 API (O-B0075-001) 並儲存為 JSON 檔案，可指定多個測站 ID。
    
    :param station_ids: 欲查詢的測站 ID 列表 (逗號分隔字串)。
    """
    
    # 1. 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)
    local_path = os.path.join(output_dir, filename)

    # 2. 建構 API 呼叫 URL
    # 使用 urllib.parse.quote 對 ID 字串進行編碼
    encoded_station_ids = urllib.parse.quote(station_ids)
    
    # 完整的 URL 結構
    url = (
        f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{data_id}"
        f"?Authorization={api_key}&format=JSON&StationID={encoded_station_ids}&WeatherElement={elements}"
    )

    print(f"🌊 正在呼叫 API: {data_id}...")
    print(f"👉 查詢測站數量: {len(station_ids.split(','))} 個")
    print(f"💾 將儲存到: {local_path}")

    try:
        # 3. 發送請求
        response = requests.get(url, timeout=45) # 稍微增加超時時間以應對較多站點的查詢
        response.raise_for_status() # 檢查 HTTP 狀態碼
        
        # 4. 將回傳的 JSON 文字內容寫入檔案
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"✅ 成功儲存所有指定測站的海象觀測資料到: {local_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 呼叫 API 失敗 {filename}。錯誤: {e}")
        if response.status_code == 400:
             print("   (提示: 400 Bad Request 可能表示某些非 CWA 站點的資料在該資料集中不可用，請檢查回傳的 JSON 內容確認包含哪些站點)")
    except Exception as e:
        print(f"❌ 儲存檔案時發生錯誤 {filename}。錯誤: {e}")


# --- 主執行區塊 ---
def main():
    # 提取 ALL_STATION_LOCATIONS 字典中的所有 key (即測站 ID)，並用逗號連接成字串
    station_ids_string = ",".join(ALL_STATION_LOCATIONS.keys())
    
    print(f"輸出目錄已設定為: {OUTPUT_DIR}")
    
    # 執行下載海象觀測資料
    download_marine_data(
        API_KEY, 
        OUTPUT_DIR, 
        DATA_ID, 
        WEATHER_ELEMENTS, 
        station_ids_string,  # 傳入包含所有 24 個站點的 ID 字串
        LOCAL_FILENAME
    )
    
    print("\n--- 所有指定測站檔案下載完成 ---")

if __name__ == "__main__":
    main()

import sys
import time
import pandas as pd
from curl_cffi import requests
import os      
import json

# ==========================================
# NHẬN THAM SỐ TỪ MAIN.PY
# ==========================================
league_name = sys.argv[1] if len(sys.argv) > 1 else "Premier_League"
tour_id = sys.argv[2] if len(sys.argv) > 2 else "17"
season_id = sys.argv[3] if len(sys.argv) > 3 else "76986"

print(f"\n[PASSING] Đang cào dữ liệu cho giải: {league_name.replace('_', ' ')}...")

url = f"https://www.sofascore.com/api/v1/unique-tournament/{tour_id}/season/{season_id}/statistics"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.sofascore.com/",
}

limit = 20
offset = 0
all_rows = []

while True:
    params = {
        "limit": limit,
        "offset": offset,
        "order": "-assists",
        "accumulation": "total",
        "group": "passing",
        "fields": "bigChancesCreated,assists,accuratePasses,accuratePassesPercentage,keyPasses,rating"
    }

    try:
        response = requests.get(url, headers=headers, params=params, impersonate="chrome124")
        
        if response.status_code != 200:
            print(f"Lỗi {response.status_code}. Dừng cào.")
            break
            
        data = response.json()
        raw_folder = "data/raw/passing"
        os.makedirs(raw_folder, exist_ok=True) # Tự động tạo thư mục nếu chưa có
        
        raw_filepath = f"{raw_folder}/{league_name}_offset_{offset}.json"
        with open(raw_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        players = data.get("results", [])
        
        if not players:
            break
            
        for p in players:
            player_info = p.get("player", {})
            team_info = p.get("team", {})
            stats = p

            all_rows.append({
                "League": league_name.replace("_", " "),
                "Team": team_info.get("name"),
                "Name": player_info.get("name"),
                "Big chances created": stats.get("bigChancesCreated", 0),
                "Assists": stats.get("assists", 0),
                "Accurate passes": stats.get("accuratePasses", 0),
                "Accurate passes %": stats.get("accuratePassesPercentage", 0),
                "Key passes": stats.get("keyPasses", 0),
                "Average Sofascore rating": stats.get("rating", 0)
            })

        offset += limit
        time.sleep(1.5)

    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        break

# Xuất CSV
if all_rows:
    df = pd.DataFrame(all_rows)
    df.index = range(1, len(df) + 1)
    df.index.name = "#"
    csv_filename = f"data/processed/{league_name}_passing_stats.csv"
    df.to_csv(csv_filename, index=True, encoding='utf-8-sig')
    print(f"✅ Đã lưu {len(df)} cầu thủ vào: {csv_filename}")
from curl_cffi import requests
import pandas as pd
import json
import os
import time

# ==========================================
# CẤU HÌNH API & HEADERS
# ==========================================
url = (
    "https://www.sofascore.com/api/v1/"
    "unique-tournament/17/season/76986/statistics"
)

headers = {
    "accept": "*/*",
    "referer": "https://www.sofascore.com/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    )
}

# ==========================================
# KHỞI TẠO BIẾN
# ==========================================
limit = 20
offset = 0
all_rows = []

os.makedirs("data/raw/goalkeeping", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

print("Bắt đầu crawl dữ liệu Thủ môn (Goalkeeping)...")

# ==========================================
# VÒNG LẶP CRAWL
# ==========================================
while True:
    print(f"Đang lấy dữ liệu từ offset: {offset}...")
    params = {
        "limit": limit,
        "offset": offset,
        "order": "-saves",
        "accumulation": "total",
        
        # [CẬP NHẬT] - Sửa lại tên key cho chính xác với database của Sofascore
        "fields": "saves,cleanSheet,penaltySave,savedShotsFromInsideTheBox,runsOut,rating",
        
        "filters": "position.in.G"
    }
    

    response = requests.get(
        url,
        params=params,
        headers=headers,
        impersonate="chrome124"
    )

    if response.status_code != 200:
        print(f"Lỗi ở offset {offset}: HTTP {response.status_code}")
        break

    data = response.json()
    players = data.get("results", [])

    if not players:
        print("Đã lấy hết dữ liệu!")
        break

    with open(f"data/raw/goalkeeping/goalkeeping_stats_offset_{offset}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # ==========================================
    # PARSE DỮ LIỆU
    # ==========================================
    for p in players:
        player_info = p.get("player", {})
        team_info = p.get("team", {})
        stats = p

        all_rows.append({
            "Team": team_info.get("name"),
            "Name": player_info.get("name"),
            "Total saves": stats.get("saves", 0),
            
            # [CẬP NHẬT] - dùng "cleanSheet"
            "Clean sheets": stats.get("cleanSheet", 0), 
            
            "Penalties saved": stats.get("penaltySave", 0), 
            
            # [CẬP NHẬT] - dùng "savedShotsFromInsideTheBox"
            "Saves from inside box": stats.get("savedShotsFromInsideTheBox", 0),
            
            "Runs out": stats.get("runsOut", 0),
            "Average Sofascore rating": stats.get("rating", 0)
        })
   
    offset += limit
    time.sleep(1.5)

# ==========================================
# XUẤT DATAFRAME VÀ LƯU CSV
# ==========================================
df = pd.DataFrame(all_rows)

df.index = df.index + 1
df.index.name = "#"

print("\nPreview Goalkeeping Stats:\n")
print(df.head())

csv_path = "data/processed/goalkeeping.csv"

df.to_csv(csv_path, index=True, encoding="utf-8-sig")

print(f"\nĐã lưu: {csv_path}")
print(f"Tổng số thủ môn đã lọc chuẩn xác: {len(df)}")
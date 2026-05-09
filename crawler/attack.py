from curl_cffi import requests
import pandas as pd
import json
import os
import time

# ==========================================
# CẤU HÌNH & HEADERS
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

# Tạo thư mục
os.makedirs("data/raw/attack", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

print("Bắt đầu crawl dữ liệu Tấn công (Attack)...")

# ==========================================
# VÒNG LẶP CRAWL
# ==========================================

while True:
    print(f"Đang lấy dữ liệu từ offset: {offset}...")
    
    params = {
        "limit": limit,
        "offset": offset,
        "order": "-goals",        # Sắp xếp theo bàn thắng
        "accumulation": "total",
        "group": "attack",        # Nhóm Tấn công
        
        # Đã cập nhật chuẩn xác 100% các keys từ JSON
        "fields": "goals,expectedGoals,bigChancesMissed,successfulDribbles,totalShots,goalConversionPercentage,rating"
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

    # Lưu raw json
    with open(f"data/raw/attack/attack_stats_offset_{offset}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # ==========================================
    # CẬP NHẬT PARSE DỮ LIỆU THEO ẢNH
    # ==========================================
    for p in players:
        player_info = p.get("player", {})
        team_info = p.get("team", {})
        stats = p

        all_rows.append({
            "Team": team_info.get("name"),
            "Name": player_info.get("name"),
            
            # Map chuẩn xác 100% theo JSON gốc
            "Goals": stats.get("goals", 0),
            "Expected goals (xG)": stats.get("expectedGoals", 0),
            "Big chances missed": stats.get("bigChancesMissed", 0),
            "Succ. dribbles": stats.get("successfulDribbles", 0),
            "Total shots": stats.get("totalShots", 0), 
            "Goal conversion %": stats.get("goalConversionPercentage", 0),
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

print("\nPreview Attack Stats (Cập nhật theo giao diện):\n")
print(df.head())

csv_path = "data/processed/attack_stats.csv"

df.to_csv(
    csv_path,
    index=True,  
    encoding="utf-8-sig"
)

print(f"\nĐã lưu: {csv_path}")
print(f"Tổng số cầu thủ đã crawl: {len(df)}")
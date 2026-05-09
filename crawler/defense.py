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

os.makedirs("data/raw/defense", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

print("Bắt đầu crawl dữ liệu Phòng ngự (Defense)...")

# ==========================================
# VÒNG LẶP CRAWL
# ==========================================
while True:
    print(f"Đang lấy dữ liệu từ offset: {offset}...")
    
    # [QUAN TRỌNG] - Cập nhật lại Params
    params = {
        "limit": limit,
        "offset": offset,
        "order": "-tackles",
        "accumulation": "total",
        # ÉP API TRẢ VỀ CÁC CỘT NÀY THAY VÌ DÙNG "group"
        "fields": "tackles,interceptions,clearances,errorLeadToGoal,outfielderBlocks,rating"
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

    with open(f"data/raw/defense/defense_stats_offset_{offset}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # ==========================================
    # CẬP NHẬT PARSE - Lưu ý các key API
    # ==========================================
    for p in players:
        player_info = p.get("player", {})
        team_info = p.get("team", {})
        
        # Các chỉ số thống kê lúc này sẽ nằm trực tiếp trong p
        stats = p

        all_rows.append({
            "Team": team_info.get("name"),
            "Name": player_info.get("name"),
            "Tackles": stats.get("tackles", 0),
            "Interceptions": stats.get("interceptions", 0),
            "Clearances": stats.get("clearances", 0),
            
            # Key API thường dùng chữ "error" số ít thay vì "errors"
            "Errors leading to goal": stats.get("errorLeadToGoal", 0), 
            
            "Blocked shots": stats.get("outfielderBlocks", 0),
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

print("\nPreview Defense Stats:\n")
print(df.head())

csv_path = "data/processed/defense_stats.csv"

df.to_csv(csv_path, index=True, encoding="utf-8-sig")

print(f"\nĐã lưu: {csv_path}")
print(f"Tổng số cầu thủ đã crawl: {len(df)}")
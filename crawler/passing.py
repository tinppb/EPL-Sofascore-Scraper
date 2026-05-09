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

# Tạo thư mục riêng cho Passing
os.makedirs("data/raw/passing", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

print("Bắt đầu crawl dữ liệu Chuyền bóng (Passing)...")

# ==========================================
# VÒNG LẶP CRAWL
# ==========================================
while True:
    print(f"Đang lấy dữ liệu từ offset: {offset}...")
    
    params = {
        "limit": limit,
        "offset": offset,
        "order": "-bigChancesCreated", # Sắp xếp theo Tạo cơ hội lớn như trong ảnh
        "accumulation": "total",
        # ÉP API TRẢ VỀ CÁC CHỈ SỐ PASSING
        "fields": "bigChancesCreated,assists,accuratePasses,accuratePassesPercentage,keyPasses,rating"
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

    with open(f"data/raw/passing/passing_stats_offset_{offset}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # ==========================================
    # PARSE DỮ LIỆU CHUYỀN BÓNG THEO ẢNH
    # ==========================================
    for p in players:
        player_info = p.get("player", {})
        team_info = p.get("team", {})
        
        stats = p

        all_rows.append({
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

# ==========================================
# XUẤT DATAFRAME VÀ LƯU CSV
# ==========================================
df = pd.DataFrame(all_rows)

# Cột # (Rank/STT)
df.index = df.index + 1
df.index.name = "#"

print("\nPreview Passing Stats:\n")
print(df.head())

csv_path = "data/processed/passing_stats.csv"

df.to_csv(csv_path, index=True, encoding="utf-8-sig")

print(f"\nĐã lưu: {csv_path}")
print(f"Tổng số cầu thủ đã crawl: {len(df)}")
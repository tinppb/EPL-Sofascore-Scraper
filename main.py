import subprocess
import time
import sys

# Khai báo kho tàng Top 5 Giải Đấu
# Khai báo kho tàng Top 5 Giải Đấu với ID chuẩn xác 100%
LEAGUES = {
    "Premier_League": {"tour_id": "17", "season_id": "76986"},
    "La_Liga": {"tour_id": "8", "season_id": "77559"},   
    "Serie_A": {"tour_id": "23", "season_id": "76457"},  
    "Bundesliga": {"tour_id": "35", "season_id": "77333"},
    "Ligue_1": {"tour_id": "34", "season_id": "77356"}   
}

SPIDERS = ["attack.py", "defense.py", "passing.py", "goalkeeping.py"]

def run_spider(script_name, league, tour_id, season_id):
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {script_name} | LEAGUE: {league.replace('_', ' ')}")
    print(f"{'='*60}")
    
    try:
        # Gọi lệnh: python crawler/attack.py La_Liga 8 61643
        subprocess.run([
            sys.executable, 
            f"crawler/{script_name}", 
            league,       # sys.argv[1]
            tour_id,      # sys.argv[2]
            season_id     # sys.argv[3]
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy {script_name} cho {league}: {e}")

if __name__ == "__main__":
    print("CRAWL TOP 5 GIẢI ĐẤU CHÂU ÂU TỪ SOFASCORE")
    
    # Chạy vòng lặp qua từng giải đấu
    for league, ids in LEAGUES.items():
        print(f"\n\n{'*'*60}")
        print(f"🏆 BẮT ĐẦU CÀO GIẢI: {league.upper().replace('_', ' ')}")
        print(f"{'*'*60}")
        
        # Với mỗi giải, chạy đủ 4 bộ chỉ số
        for spider in SPIDERS:
            run_spider(spider, league, ids["tour_id"], ids["season_id"])
            
            # Nghỉ ngơi giữa các script để chống block
            print("⏳ Đang nghỉ 3 giây...")
            time.sleep(3)
            
        print(f"✅ Hoàn thành toàn bộ dữ liệu cho {league}!")
        print("⏳ Chuyển qua giải tiếp theo... nghỉ 5 giây")
        time.sleep(5)
        
    print("\nĐÃ HOÀN THÀNH TOÀN BỘ TOP 5 GIẢI ĐẤU!")
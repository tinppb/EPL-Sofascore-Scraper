import subprocess
import sys
import time

# ==========================================
# 1. TỪ ĐIỂN TOP 5 GIẢI ĐẤU CHÂU ÂU (Mùa 25/26)
# ==========================================
# Cấu trúc: "Tên_Giải": ("Tournament_ID", "Season_ID")
# Lưu ý: Season ID có thể thay đổi theo từng năm, bạn có thể update lại nếu cần.
TOP_5_LEAGUES = {
    "Premier_League": ("17", "76986"),
    "La_Liga": ("8", "77559"),
    "Serie_A": ("23", "76457"),     # ID giải Ý
    "Bundesliga": ("35", "77333"),  # ID giải Đức
    "Ligue_1": ("34", "77356")      # ID giải Pháp
}

def main():
    print("="*60)
    print("BẮT ĐẦU CHIẾN DỊCH CÀO DATA TOP 5 EUROPEAN LEAGUES (MÙA 25/26)!")
    print("="*60)

    total_leagues = len(TOP_5_LEAGUES)
    current = 1

    for league_name, (tour_id, season_id) in TOP_5_LEAGUES.items():
        print(f"\n[{current}/{total_leagues}] Đang xử lý giải đấu: {league_name.replace('_', ' ')}...")
        
        # Tạo câu lệnh gọi file full_stats.py chạy ngầm
        # sys.executable đảm bảo nó gọi đúng môi trường ảo Python hiện tại
        command = [sys.executable, "crawler/full_stats.py", league_name, tour_id, season_id]
        
        try:
            # Chạy script con và chờ nó chạy xong
            subprocess.run(command, check=True)
            print(f"✅ Hoàn thành giải {league_name.replace('_', ' ')}!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Có lỗi xảy ra khi cào giải {league_name}: {e}")
        except FileNotFoundError:
            print(f"❌ Không tìm thấy file 'full_stats.py'.")
            break

        # Nếu chưa phải là giải đấu cuối cùng, nghỉ ngơi 10 giây để tránh bị block IP
        if current < total_leagues:
            print("⏳Nghỉ 5 giây...")
            time.sleep(5)
            
        current += 1

    print("\n" + "="*60)
    print("BỘ DỮ LIỆU ĐÃ ĐƯỢC LƯU TẠI DATA/PROCESSED/ 🎉")
    print("="*60)

if __name__ == "__main__":
    main()
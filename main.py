import subprocess
import time
import sys # Import thêm thư viện sys

def run_spider(script_name):
    print(f"\n{'='*50}")
    print(f"🚀 BẮT ĐẦU CHẠY: {script_name}")
    print(f"{'='*50}")
    
    try:
        # [CẬP NHẬT Ở ĐÂY] - Thay "python" bằng sys.executable
        subprocess.run([sys.executable, f"crawler/{script_name}"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Có lỗi xảy ra khi chạy {script_name}: {e}")

if __name__ == "__main__":
    print("🌟 CHƯƠNG TRÌNH CRAWL DỮ LIỆU NGOẠI HẠNG ANH TỪ SOFASCORE 🌟")
    
    # Danh sách các file cần chạy theo thứ tự
    spiders = [
        "attack.py",
        "defense.py",
        "passing.py",
        "goalkeeping.py"
    ]
    
    # Lặp qua từng file và chạy
    for spider in spiders:
        run_spider(spider)
        
        # Đợi 1 chút trước khi chuyển sang module khác
        if spider != spiders[-1]: # Không cần nghỉ sau khi chạy xong file cuối
            print(f"⏳ Đang nghỉ 3 giây trước khi chạy script tiếp theo...")
            time.sleep(3)
        
    print("\n✅ ĐÃ HOÀN THÀNH TẤT CẢ CÁC TIẾN TRÌNH CRAWL DỮ LIỆU!")
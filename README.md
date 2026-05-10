# ⚽ Top 5 European Leagues 25/26 Stats Scraper

Dự án thu thập tự động dữ liệu thống kê cầu thủ của **Top 5 giải vô địch quốc gia hàng đầu Châu Âu** (Premier League, La Liga, Serie A, Bundesliga, Ligue 1) mùa giải 2025/2026 từ hệ thống dữ liệu nội bộ của Sofascore. Toàn bộ dữ liệu được tự động phân trang, làm sạch và xuất ra file định dạng CSV sẵn sàng cho việc phân tích dữ liệu (Data Analysis).

---

## Mục Lục
- [Mục Tiêu Dự Án](#mục-tiêu-dự-án)
- [Yêu Cầu & Cài Đặt](#yêu-cầu--cài-đặt)
- [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
- [Kiến Trúc Dự Án](#kiến-trúc-dự-án)
- [Luồng Dữ Liệu](#luồng-dữ-liệu)
- [Từ Điển Dữ Liệu](#từ-điển-dữ-liệu)
- [Thông Tin API](#thông-tin-api)
- [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
- [Khắc Phục Sự Cố](#khắc-phục-sự-cố)

---

## Mục Tiêu Dự Án
Các trang thống kê thể thao lớn thường bảo vệ dữ liệu rất nghiêm ngặt bằng các công nghệ chống Bot (như Cloudflare, Akamai). Dự án này ra đời nhằm:
1. **Mục đích học tập:** Áp dụng kỹ thuật Web Scraping nâng cao, vượt qua hệ thống chống Bot bằng cách giả mạo TLS fingerprint của trình duyệt thực.
2. **Cung cấp dữ liệu sạch:** Lấy trực tiếp dữ liệu thô (Raw JSON) chuẩn xác 100% từ API nội bộ mà không cần cào (parse) mã nguồn HTML phức tạp.
3. **Phục vụ phân tích:** Tạo ra bộ dataset khổng lồ và đồng nhất về Tấn công, Phòng ngự, Chuyền bóng và Thủ môn của cả 5 giải đấu để phục vụ cho các bài toán phân tích thể thao (Sports Analytics).

---

## Yêu Cầu & Cài Đặt

**1. Môi trường yêu cầu**
- Python 3.8 trở lên.

**2. Mạng & Kết nối (Quan trọng)**
- Bạn CẦN sử dụng **Cloudflare WARP (1.1.1.1)** hoặc **VPN** khi chạy dự án này. Do một số nhà mạng có thể chặn truy cập vào máy chủ Sofascore, hoặc IP thường của bạn bị giới hạn khu vực.

**3. Clone dự án về máy**
```bash
git clone [https://github.com/tinppb/Top5-Leagues-Scraper-25-26](https://github.com/tinppb/Top5-Leagues-Scraper-25-26.git)
cd Top5-Leagues-Scraper-25-26
```

**4. Tạo và kích hoạt môi trường ảo (Khuyến nghị)**
```bash
python -m venv crawler
# Dành cho Windows:
crawler\Scripts\activate
# Dành cho MacOS/Linux:
source crawler/bin/activate
```

**5. Cài đặt các thư viện cần thiết**
```bash
pip install -r requirements.txt
```

---

## Hướng Dẫn Sử Dụng

**Cách 1: Chạy toàn bộ tiến trình cho Top 5 Giải (Khuyên dùng)**
Sử dụng file điều phối chính. Hệ thống sẽ tự động quét qua 5 giải đấu, thu thập 4 nhóm chỉ số cho từng giải.
```bash
python main.py
```

**Cách 2: Chạy từng script đơn lẻ cho một giải cụ thể**
Các script con giờ đây nhận tham số đầu vào linh hoạt. Cú pháp: `python crawler/<tên_file>.py [Tên_Giải] [Tournament_ID] [Season_ID]`.
Ví dụ, nếu chỉ muốn lấy chỉ số Tấn công của La Liga:
```bash
python crawler/attack.py La_Liga 8 77559
```
*(Nếu chạy không truyền tham số `python crawler/attack.py`, hệ thống sẽ mặc định cào giải Premier League).*

**Kết quả:** Dữ liệu Raw (JSON) được backup tại `data/raw/`. File CSV sạch sẵn sàng sử dụng được lưu tại `data/processed/`.

---

## Kiến Trúc Dự Án
Dự án được thiết kế theo Module linh hoạt:
- **Orchestrator (`main.py`):** Đóng vai trò điều phối tổng, chứa từ điển (`Dictionary`) lưu trữ ID của 5 giải đấu. Gọi tuần tự các script con thông qua thư viện `subprocess` và tham số dòng lệnh `sys.argv`.
- **Workers (`crawler/*.py`):** Chứa các script độc lập. Nhận thông số giải đấu từ `main.py`, xử lý phân trang (pagination) và parse JSON cho từng nhóm chỉ số.
- **Data Layer (`data/`):** Tách biệt rõ ràng giữa Dữ liệu thô (`raw/` JSON) dùng để đối chiếu backup và Dữ liệu đã xử lý (`processed/` CSV) dành cho End-user.

---

## Luồng Dữ Liệu
Quy trình xử lý dữ liệu của từng Worker tuân theo các bước sau:
1. **Khởi tạo Request:** Gửi HTTP GET request tới endpoint của Sofascore kèm các headers (User-Agent thực) và thông số `impersonate="chrome124"` qua `curl_cffi`.
2. **Xử lý Phân trang:** Vòng lặp `while True` liên tục tăng biến `offset` lên 20 (bằng với `limit`). Vòng lặp sẽ dừng (break) khi API trả về danh sách rỗng `[]`.
3. **Backup Raw Data:** Toàn bộ dữ liệu JSON trả về ở mỗi trang được lưu thành file tĩnh tại `data/raw/<chỉ_số>/` để dự phòng.
4. **Data Parsing:** Trích xuất thông tin Cầu thủ, Đội bóng, Giải đấu và các chỉ số chuyên môn cụ thể (`stats.get("...")`) đưa vào danh sách Python.
5. **Xuất CSV:** Chuyển đổi dữ liệu sang Pandas DataFrame, đánh số thứ tự (Rank/Index) và lưu thành file CSV định dạng chuẩn `utf-8-sig`.

---

## Từ Điển Dữ Liệu
Các file CSV đầu ra bao gồm các trường dữ liệu chính:

* **Tất cả các tệp đều có:** `#` (Xếp hạng), `League` (Tên giải đấu), `Team` (Tên đội bóng), `Name` (Tên cầu thủ), `Average Sofascore rating` (Điểm đánh giá trung bình).
* **Attack (Tấn công):** `Goals`, `Expected goals (xG)`, `Big chances missed`, `Succ. dribbles`, `Total shots`, `Goal conversion %`.
* **Defense (Phòng ngự):** `Tackles`, `Interceptions`, `Clearances`, `Errors leading to goal`, `Blocked shots` (outfielderBlock).
* **Passing (Chuyền bóng):** `Big chances created`, `Assists`, `Accurate passes`, `Accurate passes %`, `Key passes`.
* **Goalkeeping (Thủ môn):** `Total saves`, `Clean sheets`, `Penalties saved`, `Saves from inside box`, `Runs out`.

---

## Thông Tin API
- **Base URL (Động):** `https://www.sofascore.com/api/v1/unique-tournament/{tour_id}/season/{season_id}/statistics`
- **Phương thức:** `GET`
- **Tham số chính (Parameters):**
  - `limit`: Số lượng bản ghi mỗi trang (Mặc định: 20).
  - `offset`: Điểm bắt đầu của trang (0, 20, 40...).
  - `order`: Tiêu chí sắp xếp (VD: `-goals`, `-tackles`). Dấu `-` biểu thị sắp xếp giảm dần.
  - `accumulation`: Đặt là `total` để lấy tổng số của cả mùa giải.
  - `fields`: Ép API trả về đích danh các cột dữ liệu cần thiết (đồng bộ hóa dữ liệu, tránh bị API ẩn trường).
  - `filters`: Lọc dữ liệu ngay từ phía Server. (VD: `position.in.G` dùng để lấy chính xác danh sách các Thủ môn).

*Lưu ý: API này là tài sản nội bộ của Sofascore. Việc truy cập thông qua script chỉ phục vụ mục đích học tập và nghiên cứu cá nhân.*

---

## Cấu Trúc Thư Mục

```text
EPL-Sofascore-Scraper/
│
├── crawler/                  # Chứa các kịch bản cào dữ liệu độc lập
│   ├── attack.py
│   ├── defense.py
│   ├── goalkeeping.py
│   └── passing.py
│
├── data/                     # Thư mục lưu trữ dữ liệu
│   ├── processed/            
│   │   ├── Premier_League_attack_stats.csv
│   │   ├── La_Liga_attack_stats.csv
│   │   └── ... (Tương tự cho các giải và nhóm chỉ số khác)
│   └── raw/                  # Dữ liệu dạng JSON thô
│       ├── attack/
│       ├── defense/
│       ├── goalkeeping/
│       └── passing/
│
├── .gitignore                
├── main.py                   
├── README.md                
└── requirements.txt        
```

---

## Khắc Phục Sự Cố

**1. Lỗi kết nối, Timeout hoặc văng lỗi HTTP 403 Forbidden**
- **Nguyên nhân:** Địa chỉ IP mạng của bạn đang bị chặn truy cập vào Sofascore, hoặc nhà mạng (ISP) chặn kết nối.
- **Khắc phục:** Hãy bật phần mềm **Cloudflare WARP (1.1.1.1)** hoặc **VPN** trên máy tính rồi chạy lại script.

**2. Lỗi `ModuleNotFoundError: No module named 'curl_cffi'` khi chạy `main.py`**
- **Nguyên nhân:** Lệnh subprocess không tìm thấy thư viện trong môi trường ảo.
- **Khắc phục:** Đảm bảo đã kích hoạt môi trường ảo (ví dụ: `crawler\Scripts\activate`). `main.py` sử dụng `sys.executable` để tự động trỏ đúng vào Python của môi trường ảo đang chạy.

**3. Code chạy bị treo hoặc báo lỗi HTTP 429 Too Many Requests**
- **Nguyên nhân:** Gửi request quá nhanh khiến cơ chế Anti-Bot phát hiện. 
- **Khắc phục:** Tuyệt đối giữ nguyên hàm gọi qua thư viện `curl_cffi`. Đảm bảo trong code luôn có `time.sleep()` để mô phỏng thao tác của người thật.

**4. Cột dữ liệu toàn số 0**
- **Nguyên nhân:** Tên tham số khai báo trong `fields` không khớp với Database của Sofascore.
- **Khắc phục:** Code hiện tại đã được fix chuẩn xác 100% các keys. Nếu xuất hiện ở cột mới muốn thêm vào, hãy tự in JSON cục bộ (`print(json.dumps(data))`) để dò tìm tên biến thực tế.
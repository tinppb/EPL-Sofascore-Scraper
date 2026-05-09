# ⚽ English Premier League 25/26 Stats Scraper

Dự án thu thập tự động dữ liệu thống kê cầu thủ giải Ngoại hạng Anh (Premier League) mùa giải 2025/2026 từ hệ thống dữ liệu nội bộ của Sofascore. Toàn bộ dữ liệu được tự động phân trang, làm sạch và xuất ra file định dạng CSV sẵn sàng cho việc phân tích dữ liệu (Data Analysis).

---

## Mục Lục
- [Động Lực Dự Án](#động-lực-dự-án)
- [Yêu Cầu & Cài Đặt](#yêu-cầu--cài-đặt)
- [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
- [Kiến Trúc Dự Án](#kiến-trúc-dự-án)
- [Luồng Dữ Liệu](#luồng-dữ-liệu)
- [Từ Điển Dữ Liệu](#từ-điển-dữ-liệu)
- [Thông Tin API](#thông-tin-api)
- [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
- [Khắc Phục Sự Cố](#khắc-phục-sự-cố)

---

## Động Lực Dự Án
Các trang thống kê thể thao lớn thường bảo vệ dữ liệu rất nghiêm ngặt bằng các công nghệ chống Bot (như Cloudflare, Akamai). Dự án này ra đời nhằm:
1. **Mục đích học tập:** Áp dụng kỹ thuật Web Scraping nâng cao, vượt qua hệ thống chống Bot bằng cách giả mạo TLS fingerprint của trình duyệt thực.
2. **Cung cấp dữ liệu sạch:** Lấy trực tiếp dữ liệu thô (Raw JSON) chuẩn xác 100% từ API nội bộ mà không cần cào (parse) mã nguồn HTML phức tạp.
3. **Phục vụ phân tích:** Tạo ra bộ dataset đầy đủ về Tấn công, Phòng ngự, Chuyền bóng và Thủ môn để phục vụ cho các bài toán phân tích thể thao (Sports Analytics).

---

## Yêu Cầu & Cài Đặt

**1. Môi trường yêu cầu**
- Python 3.8 trở lên.

**2. Clone dự án về máy**
```bash
git clone https://github.com/tinppb/EPL-Sofascore-Scraper.git
cd EPL-Sofascore-Scraper
```

**3. Tạo và kích hoạt môi trường ảo (Khuyến nghị)**
```bash
python -m venv crawler
# Dành cho Windows:
crawler\Scripts\activate
# Dành cho MacOS/Linux:
source crawler/bin/activate
```

**4. Cài đặt các thư viện cần thiết**
```bash
pip install -r requirements.txt
```

---

## Hướng Dẫn Sử Dụng

**Cách 1: Chạy toàn bộ tiến trình (Khuyên dùng)**
Sử dụng file điều phối chính để thu thập tự động cả 4 nhóm chỉ số (Attack, Defense, Passing, Goalkeeping). Dữ liệu sẽ tự động có thời gian nghỉ (sleep) giữa các tiến trình để tránh quá tải server.
```bash
python main.py
```

**Cách 2: Chạy từng script đơn lẻ**
Nếu bạn chỉ muốn lấy một loại dữ liệu cụ thể, hãy gọi trực tiếp script trong thư mục `crawler/`:
```bash
python crawler/attack.py
python crawler/defense.py
python crawler/passing.py
python crawler/goalkeeping.py
```

**Kết quả:** Sau khi chạy xong, toàn bộ file `.csv` sẽ được lưu tại thư mục `data/processed/`.

---

## Kiến Trúc Dự Án
Dự án được thiết kế theo mô hình **Modular (Mô-đun hóa)**:
- **Orchestrator (`main.py`):** Đóng vai trò nhạc trưởng, điều phối việc gọi lần lượt các script con thông qua thư viện `subprocess`, quản lý thời gian nghỉ (`time.sleep`) và log tiến trình ra màn hình.
- **Workers (`crawler/*.py`):** Chứa các script độc lập. Mỗi script chịu trách nhiệm gọi một cấu hình API riêng biệt, phân trang dữ liệu (pagination) và xử lý JSON cho từng nhóm chỉ số cụ thể.
- **Data Layer (`data/`):** Tách biệt rõ ràng giữa Dữ liệu thô (`raw/` JSON) dùng để đối chiếu backup và Dữ liệu đã xử lý (`processed/` CSV) dành cho End-user.

---

## Luồng Dữ Liệu
Quy trình xử lý dữ liệu của từng Worker tuân theo các bước sau:
1. **Khởi tạo Request:** Gửi HTTP GET request tới endpoint của Sofascore kèm các headers (User-Agent thực) và thông số `impersonate="chrome124"` qua `curl_cffi`.
2. **Xử lý Phân trang:** Vòng lặp `while True` liên tục tăng biến `offset` lên 20 (bằng với `limit`). Vòng lặp sẽ dừng (break) khi API trả về danh sách rỗng `[]`.
3. **Backup Raw Data:** Toàn bộ dữ liệu JSON trả về ở mỗi trang được lưu thành file tĩnh tại `data/raw/` để dự phòng.
4. **Data Parsing:** Trích xuất thông tin Cầu thủ, Đội bóng và các chỉ số chuyên môn cụ thể (`stats.get("...")`) đưa vào danh sách Python (List of Dictionaries).
5. **Xuất CSV:** Chuyển đổi dữ liệu sang Pandas DataFrame, đánh số thứ tự (Rank/Index) và lưu thành file CSV định dạng chuẩn `utf-8-sig` (hỗ trợ hiển thị tiếng Việt và ký tự đặc biệt).

---

## Từ Điển Dữ Liệu
Các file CSV đầu ra bao gồm các trường dữ liệu chính:

* **Tất cả các tệp đều có:** `#` (Xếp hạng), `Team` (Tên đội bóng), `Name` (Tên cầu thủ), `Average Sofascore rating` (Điểm đánh giá trung bình).
* **Attack (Tấn công):** `Goals`, `Expected goals (xG)`, `Big chances missed`, `Succ. dribbles`, `Total shots`, `Goal conversion %`.
* **Defense (Phòng ngự):** `Tackles`, `Interceptions`, `Clearances`, `Errors leading to goal`, `Blocked shots` (outfielderBlock).
* **Passing (Chuyền bóng):** `Big chances created`, `Assists`, `Accurate passes`, `Accurate passes %`, `Key passes`.
* **Goalkeeping (Thủ môn):** `Total saves`, `Clean sheets`, `Penalties saved`, `Saves from inside box`, `Runs out`.

---

## Thông Tin API
- **Base URL:** `[https://www.sofascore.com/api/v1/unique-tournament/17/season/76986/statistics](https://www.sofascore.com/api/v1/unique-tournament/17/season/76986/statistics)`
- **Phương thức:** `GET`
- **Tham số chính (Parameters):**
  - `limit`: Số lượng bản ghi mỗi trang (Mặc định: 20).
  - `offset`: Điểm bắt đầu của trang (0, 20, 40...).
  - `order`: Tiêu chí sắp xếp (VD: `-goals`, `-tackles`, `-saves`). Dấu `-` biểu thị sắp xếp giảm dần.
  - `accumulation`: Đặt là `total` để lấy tổng số của cả mùa giải.
  - `fields`: Ép API trả về đích danh các cột dữ liệu cần thiết (tránh việc bị API ẩn dữ liệu khi lật trang).
  - `filters`: Lọc dữ liệu ngay từ phía Server. (VD: `position.in.G` dùng để lấy chính xác danh sách các Thủ môn).

*Lưu ý: API này là tài sản nội bộ của Sofascore. Việc truy cập thông qua script chỉ phục vụ mục đích học tập và nghiên cứu cá nhân.*

---

## Cấu Trúc Thư Mục

```text
PREMIER_LEAGUE25_26/
│
├── crawler/                  # Chứa các kịch bản cào dữ liệu độc lập
│   ├── attack.py
│   ├── defense.py
│   ├── goalkeeping.py
│   └── passing.py
│
├── data/                     # Thư mục lưu trữ dữ liệu
│   ├── processed/            # Dữ liệu dạng CSV đã được làm sạch 
│   │   ├── attack_stats.csv
│   │   ├── defense_stats.csv
│   │   ├── goalkeeping.csv
│   │   └── passing_stats.csv
│   └── raw/                  # Dữ liệu dạng JSON thô (Được ignore trên Git)
│       ├── attack/
│       ├── defense/
│       ├── goalkeeping/
│       └── passing/
│
├── .gitignore                # Quản lý các file không đưa lên Git
├── main.py                   # Điểm bắt đầu (Orchestrator) của hệ thống
├── README.md                 # Tài liệu mô tả dự án
└── requirements.txt          # Danh sách thư viện cần thiết
```

---

## Khắc Phục Sự Cố

**1. Lỗi `ModuleNotFoundError: No module named 'curl_cffi'` khi chạy `main.py`**
- **Nguyên nhân:** Lệnh subprocess không tìm thấy thư viện trong môi trường ảo.
- **Khắc phục:** Đảm bảo đã kích hoạt môi trường ảo. `main.py` đã được thiết kế sử dụng `sys.executable` thay cho chữ `python` cứng để tự động trỏ đúng vào Python của môi trường ảo.

**2. Code chạy bị treo hoặc báo lỗi HTTP 403 / HTTP 429**
- **Nguyên nhân:** Gửi request quá nhanh khiến cơ chế Anti-Bot phát hiện. Hoặc do bạn thay đổi thư viện sang `requests` thông thường.
- **Khắc phục:** Tuyệt đối giữ nguyên hàm gọi qua thư viện `curl_cffi`. Đảm bảo trong code luôn có `time.sleep(1.5)` đến `time.sleep(3)` để mô phỏng thao tác của người thật.

**3. Cột dữ liệu toàn số 0**
- **Nguyên nhân:** Tên tham số khai báo trong `fields` không khớp với Database của Sofascore (VD: Thủ môn phải gọi `cleanSheet` thay vì `cleanSheets`).
- **Khắc phục:** Code hiện tại trên nhánh `main` đã được fix chuẩn xác 100% các keys. Nếu xuất hiện ở cột mới, hãy tự in JSON cục bộ (`print(json.dumps(data))`) để dò tìm tên biến thực tế.
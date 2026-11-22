# Progress

> File trạng thái cho mỗi phiên làm việc mới. Giữ ngắn: cập nhật mục "Hiện tại" và "Tiếp theo", thêm 1 dòng vào "Nhật ký". Chi tiết công việc ở `docs/TASKS.md`.

## Hiện tại (cập nhật 22/11/2026)
- **Giai đoạn:** G1 Khởi tạo – xong · sắp vào G2 Tri thức & dữ liệu (hạn 24/11).
- **Chạy được:** `python -m src.cli data` (German Credit tự tải; Home Credit cần tải tay/token), `python -m src.cli eda`, `pytest` (2 test pass).
- **Dữ liệu có trên máy:** `data/raw/german_credit.csv` (1000 dòng, 30% bad). **Chưa có** `data/raw/application_train.csv` (Home Credit).
- **Chưa cài:** train/eval/app (CLI báo "chưa cài đặt").

## Quyết định đã chốt
| Ngày | Quyết định | Lý do |
|---|---|---|
| 22/11 | Gốc repo = thư mục `...\CDNC_UngDungCongNgheTriThuc\src`, code ở `src/src/` | Thư mục người dùng mở trong VS Code |
| 22/11 | Dataset chính dự kiến **Home Credit** (`application_train.csv`), German Credit làm phụ | EDA: `job` của German Credit có Cramér's V ≈ 0 với vỡ nợ và không có biến thu nhập → không thể hiện được chuỗi Ngành → Thu nhập |
| 22/11 | Không có code FICO cũ → cài lại tối giản trong `src/baselines/fico.py`, luật trong `configs/fico.yaml`, nhóm xác nhận | Người dùng xác nhận không còn code |
| 22/11 | Hạn nộp 02/12; lộ trình G2 24/11 · G3 26/11 · G4 29/11 · G5 01/12; ưu tiên MUST/SHOULD/COULD trong TASKS.md | 10 ngày, làm song song |
| 22/11 | Vai trò: Mạnh=TV1, Nam=TV2, Khôi=TV3, Phúc=TV4 (mặc định, có thể đổi) | Theo thứ tự tên nhóm cung cấp |

## Kết quả đã có
- EDA German Credit: `reports/eda/german_credit.md`. Liên hệ mạnh nhất với vỡ nợ: `checking_status` (V=0.35), `credit_history` (0.24), `duration` (0.21); `job` ≈ 0.

## Vấn đề tồn đọng
- Chờ người dùng tải `application_train.csv` vào `data/raw/` (cách tải tay không cần token – xem README).
- Gói `kaggle` 2.x cần `six` (đã thêm vào requirements); `import kaggle` tự in thông báo xác thực khi không có token – vô hại.

## Tiếp theo
1. Khi có Home Credit: `src/data/eda_home_credit.py` → tỷ lệ vỡ nợ theo `OCCUPATION_TYPE`/`ORGANIZATION_TYPE`, tỷ lệ thiếu.
2. `knowledge_base/occupation_mapping.csv` (58+18 giá trị → 6–10 nhóm ngành, cột `rationale`).
3. `src/data/discretize.py` + `configs/discretize.yaml`.
4. Knowledge base vĩ mô (World Bank CPI/thất nghiệp qua `wbgapi`, GSO thu nhập theo ngành) có nguồn.
5. FICO baseline tối giản.
6. Vẽ DAG BN-Expert → ⏸ nhóm duyệt (tối 24/11).

## Nhật ký
- 22/11 – Khởi tạo repo (commit `9d038ab`, `fc70414`), German Credit + EDA, TASKS.md; thêm CLAUDE.md/Progress.md, hỗ trợ token Kaggle kiểu mới, gán tên thành viên + lộ trình đến 02/12.

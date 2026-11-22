# 1. Tổng quan dự án

## 1.1. Đề bài yêu cầu gì
Đề bài là Project 6 trong `docs/De tai mon Cong nghe tri thuc 2026.pdf` (trang 5–6; file không commit). Đề yêu cầu:
1. Một **Mạng Bayes (BN)** mô hình hóa chuỗi `Ngành → Thu nhập → Biến cố → Khả năng vỡ nợ`.
2. **Suy luận xuôi**: từ hồ sơ một người, tính xác suất vỡ nợ rồi quy đổi ra điểm 300–850.
3. **Suy luận ngược**: từ mục tiêu (ví dụ điểm 700, hay "có nhà") suy ra điều kiện cần về thu nhập và chi tiêu.
4. **LLM diễn giải**: biến bảng xác suất (CPT) và kết quả của BN thành lời khuyên tiếng Việt. LLM *không tự tính
   xác suất*.
5. **Demo** Streamlit có đồ thị nhân quả.
6. **Báo cáo thực nghiệm BN so với ML hộp đen** (phần quan trọng nhất), về: phân biệt, hiệu chỉnh, kiểm định thống
   kê, thiếu thông tin, dữ liệu ít, dịch chuyển theo ngành, nhất quán tri thức, ổn định giải thích, chi phí.
7. Nêu rõ khác biệt so với đề tài cũ "tính điểm tín dụng giả lập theo luật FICO". Nhóm không còn code cũ nên đã
   tái hiện lại luật FICO làm mốc so sánh.

## 1.2. Ý tưởng chính (một đoạn)
Dùng dữ liệu thật (Home Credit, 307.511 hồ sơ vay) để **học** quan hệ giữa ngành, nghề, thu nhập, gánh nặng nợ, lịch
sử tín dụng và vỡ nợ. Cấu trúc đồ thị do **chuyên gia (nhóm) thiết kế**, mỗi cạnh có lý do. Vì dữ liệu không có biến
cố (mất việc, ốm đau, lạm phát), nhóm thêm một **lớp tri thức**: các nút có xác suất lấy từ số liệu chính thức
(World Bank, WHO, Tổng cục Thống kê). Lớp này được nối vào mô hình sao cho *gần như không làm sai* phần đã học từ dữ liệu
(gọi là calibrated noisy-OR). Sau đó mô hình được so sánh trung thực với 8 mô hình ML và 4 biến thể Bayes trên 9
tiêu chí.

## 1.3. Kiến trúc tổng thể
```
           ┌──────────────── NGUỒN ────────────────┐
           │ Home Credit (Kaggle)  German Credit   │   World Bank · WHO · GSO KSMS 2024 · FICO · ISIC/ISCO
           └───────────┬───────────────────────────┘                    │
                       ▼                                                ▼
   src/data/home_credit.py  (13 nhóm đặc trưng)              src/knowledge/*.py → knowledge_base/*.csv
                       ▼                                                │
   src/data/discretize.py  (trạng thái rời rạc; ngưỡng ở configs/discretize.yaml)
                       ▼                                                ▼
   ┌──────────── src/bn/ ─────────────────────────────────────────────────────────┐
   │ core.py      DiscreteBN: học CPT (m-estimate), suy luận chính xác theo lô    │
   │ expert_cpt.py  CPT nút tri thức sinh từ knowledge_base/                      │
   │ model.py     BN-Expert(+Mono), calibrated noisy-OR, điểm 300–850             │
   │ backward.py  hậu nghiệm ngược, MAP, phản thực do()                           │
   │ variants.py  Naive Bayes, TAN, BN-Learned, BN-Hybrid                         │
   └──────────────────────────────────────────────────────────────────────────────┘
        │                         │                                   │
        ▼                         ▼                                   ▼
 src/evaluation/  (thí nghiệm)   models/*.json (mô hình cho demo)    src/llm/ (dữ kiện → LLM → kiểm tra)
 src/baselines/ (FICO, ML)        │                                   │
        ▼                         └────────────► src/app/streamlit_app.py ◄────┘
 experiments/*/results.csv → reports/results/*.md, reports/figures/ → reports/report.md
```

## 1.4. Luồng của một hồ sơ trong demo
1. Người dùng nhập: ngành, nghề, tuổi, thu nhập (VND), trả góp, dư nợ… Trường nào không biết thì để "Không rõ".
2. `src/app/convert.py` quy đổi sang trạng thái của BN. Ví dụ thu nhập bình quân đầu người được đổi sang nhóm 1–5
   theo GSO; DSTI = trả góp/thu nhập.
3. BN-Expert-Mono tính P(vỡ nợ | thông tin đã biết) bằng suy luận chính xác, rồi quy đổi ra điểm.
4. Demo hiển thị:
   - đóng góp từng yếu tố;
   - đồ thị nhân quả;
   - kế hoạch cải thiện điểm (phản thực);
   - what-if biến cố.
5. `src/llm/facts.py` gom các con số trên thành "dữ kiện". LLM chỉ diễn đạt lại dữ kiện. `faithfulness.py` kiểm tra
   xem LLM có bịa số hay không.

## 1.5. Cấu trúc repo
Thư mục trên máy tên là `src`, nên code nằm ở `src/src/`. Đây là gốc repo, không phải lỗi.

| Đường dẫn | Nội dung | Ai được sửa |
|---|---|---|
| `src/data/` | đọc dữ liệu, tạo đặc trưng, rời rạc hóa, EDA | Mạnh |
| `src/knowledge/` | tải World Bank/WHO/GSO | Mạnh |
| `src/bn/` | Mạng Bayes | Mạnh |
| `src/baselines/` | FICO, ML (LR, XGBoost…) | Mạnh |
| `src/evaluation/` | CV, chỉ số, thí nghiệm, bảng, hình, ghép báo cáo | Mạnh |
| `src/llm/` | dữ kiện, prompt, client, kiểm tra trung thành | Mạnh |
| `src/app/` | demo Streamlit | Mạnh |
| `configs/*.yaml` | **mọi tham số** (ngưỡng, cấu trúc DAG, λ, chi phí đòn bẩy…) | Mạnh |
| `knowledge_base/` | tri thức đã mã hóa, có cột nguồn | Mạnh (Nam góp ý) |
| `models/*.json` | mô hình đã học cho demo | sinh tự động |
| `experiments/<tên>/results.csv` | kết quả thô từng thí nghiệm | sinh tự động |
| `reports/results/`, `reports/figures/`, `reports/results_summary.md` | bảng, hình | sinh tự động |
| `reports/chapters/*.md` | văn bản báo cáo | người viết từng chương |
| `reports/report.md` | báo cáo ghép | sinh tự động, **không sửa tay** |
| `docs/` | tài liệu, bàn giao | cả nhóm |
| `tests/` | kiểm thử pytest | Mạnh |
| `data/raw/`, `data/interim/` | dữ liệu thô, tạm (không commit) | – |

## 1.6. Các lệnh
Windows không có `make`, nên gọi `.venv\Scripts\python -m src.cli <bước>`.

| Lệnh | Làm gì | Thời gian |
|---|---|---|
| `data` | tải German Credit; hướng dẫn tải Home Credit | 1 phút |
| `eda` | thống kê mô tả → `reports/eda/` | 1 phút |
| `knowledge` | tải World Bank, WHO, GSO → `knowledge_base/` | 1 phút |
| `dag` | kiểm tra và vẽ DAG, đo mức ủng hộ của dữ liệu cho từng cạnh | < 1 phút |
| `train` | học BN-Expert, BN-Expert-Mono, XGBoost demo trên toàn bộ dữ liệu → `models/` | ~25 giây |
| `tune` | Optuna tinh chỉnh XGBoost (25 trial, chỉ dùng train) | ~3 phút |
| `eval [tên…]` | toàn bộ hoặc một số thí nghiệm | ~1 giờ toàn bộ |
| `llm` | đánh giá lời khuyên LLM trên 50 hồ sơ | 1–5 phút |
| `report` | ghép chương + bảng → `reports/report.md` | vài giây |
| `app` | chạy demo | – |
| `python -m pytest -q` | chạy toàn bộ test | ~1 phút |

## 1.7. Những quyết định quan trọng (và lý do)
Bảng đầy đủ nằm trong `Progress.md`, mục "Quyết định đã chốt". Tóm tắt:

| Quyết định | Lý do |
|---|---|
| Home Credit là dữ liệu chính | Có ngành, nghề, thu nhập, khoản vay. German Credit không có thu nhập, và biến nghề gần như không liên hệ với vỡ nợ |
| Ngành gộp 10 nhóm theo ISIC, nghề gộp 5 nhóm theo ISCO-08 | Theo chuẩn quốc tế có nguồn, đồng thời giữ CPT nhỏ |
| Không dùng giới tính, hôn nhân | Thuộc tính nhạy cảm, có thể phân biệt đối xử |
| Thu nhập dùng ngũ phân vị | Home Credit không công bố đơn vị tiền tệ |
| Tri thức vĩ mô Việt Nam chỉ dùng cho lớp what-if | Dữ liệu không có biến vĩ mô, nên không thể kiểm chứng định lượng |
| Calibrated noisy-OR, λ = 0,3 (giả định) | Lớp tri thức giữ đúng xác suất học từ dữ liệu, trừ các ô phải cắt p0. Thí nghiệm độ nhạy cho thấy AUC giảm nhẹ khi λ tăng |
| Xây cả BN-Expert và BN-Expert-Mono; Mono là mô hình của demo | Mono không bao giờ cho lời khuyên ngược tri thức |
| Ước lượng CPT bằng m-estimate thay cho BDeu | BDeu cho P(vỡ nợ) = 50% ở tổ hợp chưa gặp, trong khi tỷ lệ nền là 8% |
| Tự viết bộ suy luận theo lô | Thí nghiệm cần hàng triệu truy vấn; kết quả khớp pgmpy tới 1e-8 |
| ML dùng cùng 13 nhóm biến như BN | So sánh công bằng thông tin |
| Mạnh làm toàn bộ code và số liệu | Các thành viên dùng AI khác nhau, cách này tránh lệch |

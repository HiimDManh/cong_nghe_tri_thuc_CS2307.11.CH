# Progress

> File trạng thái cho mỗi phiên mới. Claude tự cập nhật trước mỗi commit (quy tắc trong CLAUDE.md). Chi tiết việc: `docs/TASKS.md`.

## Hiện tại (cập nhật 22/11/2026)
- **Giai đoạn:** G2 ✅ (DAG + FICO được duyệt 22/11) · G3: **phần BN xong**; còn pipeline CV + baseline ML (hạn 26/11).
- **Chạy được:** `python -m src.cli data|eda|knowledge|dag|train`, `pytest` (**24 test pass**, gồm đối chiếu suy luận với pgmpy).
- **Mô hình cho demo:** `models/bn_expert.json`, `models/bn_expert_mono.json`, `models/discretizer.json` (học trên toàn bộ 307.511 dòng, ~6 s).
- **Phân công mới:** Mạnh (+Claude) làm toàn bộ code/số liệu; Nam/Khôi/Phúc làm việc không sinh code (xem TASKS.md).

## Quyết định đã chốt
| Ngày | Quyết định | Lý do |
|---|---|---|
| 22/11 | Home Credit chính, German Credit phụ | German: `job` V≈0, không có thu nhập |
| 22/11 | Ngành → 10 nhóm ISIC, nghề → 5 nhóm ISCO-08; không dùng giới tính/hôn nhân | Chuẩn có nguồn; thuộc tính nhạy cảm |
| 22/11 | Thu nhập, ext_score: ngũ phân vị (fit train); còn lại ngưỡng nghiệp vụ | Không rõ đơn vị tiền tệ |
| 22/11 | Tri thức vĩ mô VN (WB, WHO, GSO) chỉ cho nút expert/what-if | Dữ liệu không có biến vĩ mô |
| 22/11 | BN-Expert 2 lớp; nối bằng calibrated noisy-OR, λ=0.3 (giả định, sẽ phân tích độ nhạy) | Nhóm chấp nhận |
| 22/11 | Xây **cả** BN-Expert (học thuần) và **BN-Expert-Mono** (ràng buộc DSTI↑ rủi ro↑, ext_score↑ rủi ro↓); Mono là mô hình chính của demo | Nhóm chấp nhận; Mono tốt hơn & không cho lời khuyên ngược tri thức |
| 22/11 | FICO: trọng số myFICO 35/30/15/10/10 với proxy trong `configs/fico.yaml` | Nhóm xác nhận |
| 22/11 | Ước lượng CPT bằng **m-estimate (prior = phân phối biên), m=10** thay BDeu | BDeu cho P(vỡ nợ)=0.5 ở tổ hợp cha chưa gặp; m chọn trên validation tách từ train |
| 22/11 | Tự cài suy luận chính xác theo lô (gather + einsum biến ẩn) thay VE từng dòng | VE quá chậm cho thí nghiệm; kiểm chứng khớp pgmpy 1e-8 |
| 22/11 | Counterfactual dùng do() (graph surgery) trên 7 đòn bẩy: thu nhập, DSTI, LTI, chi phí sinh hoạt, tra cứu tín dụng + 2 đòn bẩy dài hạn (lịch sử tín dụng, thâm niên) | Chỉ thu nhập/chi tiêu không đủ đạt mục tiêu (xem Kết quả) |
| 22/11 | Bằng chứng bất khả (vd. mất việc khi không đi làm) → NaN tường minh; demo phải chặn | Đúng ngữ nghĩa xác suất |
| 22/11 | Phân công: Mạnh làm toàn bộ code/số liệu; các bạn khác việc không sinh code | Thành viên dùng AI khác nhau → tránh lệch |

## Kết quả đã có
- EDA: ext_score V=0.213 ≫ years_employed 0.088 > age 0.077 > occupation 0.076 > sector 0.062; income/DSTI/LTI ≈ 0.02 và không đơn điệu (nghi thiên lệch chọn mẫu).
- **Sơ bộ, 1 lần chia 80/20 seed 42 (CHƯA phải kết quả chính thức):** AUC – TAN 0.730, BN-Expert-Mono 0.716, BN-Hybrid 0.714, BN-Expert 0.713, NB 0.708, BN-Learned 0.704, FICO 0.692. Log-loss tốt nhất TAN 0.2558, Mono 0.2580.
- BN-Learned (HC+BIC) chỉ nối `ext_score → default` và đảo nhiều cạnh nhân quả (vd. income → sector) → minh họa giá trị của tri thức chuyên gia.
- Counterfactual (hồ sơ mẫu 585 điểm): mục tiêu 620 đạt bằng "DSTI <10% + trả nợ đúng hạn (ext fair→good)" (chi phí 5); mục tiêu 700 không đạt, tối đa ~659 → thu nhập/chi tiêu tác động yếu, lịch sử tín dụng quyết định.
- Tham số lớp tri thức + nguồn: `reports/bn/expert_params.md` (π(shock)=6.2%; thất nghiệp nền 1.75%; sức khỏe 8.8%/13.4%; đệm GSO Q1..Q5 = 1.0/0.77/0.64/0.57/0.42).
- KB mới: `vn_income_spending_quintiles_2024.csv` (GSO KSMS 2024: thu nhập Q1 1.59 – Q5 11.81 triệu/người/tháng; chi tiêu/thu nhập 92% → 38.5%), `debt_threshold_sources.csv`.

## Vấn đề tồn đọng
- Nguồn ngưỡng nợ & mục tiêu lạm phát cần đối chiếu bản gốc (Nam).
- Thu nhập theo ngành VN (GSO lao động 2024) chưa trích được (PDF nén) – COULD.
- Demo: quy đổi thu nhập hộ VND → ngũ phân vị bằng trung điểm (giả định); chặn what-if "mất việc" khi không đi làm.

## Tiếp theo
1. `src/evaluation/cv.py`: stratified 5-fold × 3 seed, lưu split `experiments/splits/`; mỗi fold fit Discretizer trên train.
2. Baseline ML (LR, XGBoost trước) trên đặc trưng liên tục & rời rạc; cùng cách xử lý mất cân bằng (không resample, đánh giá bằng xác suất).
3. Thí nghiệm (1)(2)(3)(4)(5)(7) → `experiments/`; độ nhạy λ.
4. LLMClient + Streamlit (sau khi có số liệu thí nghiệm chính).

## Nhật ký
- 22/11 – G1 khởi tạo (`9d038ab`, `fc70414`, `d69f56a`).
- 22/11 – G2 tri thức & dữ liệu, DAG đề xuất (`3c08196`).
- 22/11 – Nhóm duyệt DAG/FICO; GSO KSMS 2024 + nguồn ngưỡng nợ; G3-BN: core/expert/mono/backward/variants, 24 test, models/*.json; phân công lại.

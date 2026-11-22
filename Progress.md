# Progress

> File trạng thái cho mỗi phiên mới. Claude tự cập nhật trước mỗi commit (xem quy tắc trong CLAUDE.md). Chi tiết việc: `docs/TASKS.md`.

## Hiện tại (cập nhật 22/11/2026)
- **Giai đoạn:** G2 Tri thức & dữ liệu – gần xong · **⏸ ĐANG CHỜ NHÓM DUYỆT DAG BN-Expert + luật FICO** (hạn 24/11).
- **Chạy được:** `python -m src.cli data|eda|knowledge|dag`, `pytest` (8 test pass).
- **Dữ liệu trên máy:** `data/raw/application_train.csv` (307.511 × 122, 8.07% vỡ nợ, 0.34 GB RAM, đọc ~10 s), `data/raw/german_credit.csv`.
- **Chưa cài:** train/eval/app.

## Quyết định đã chốt
| Ngày | Quyết định | Lý do |
|---|---|---|
| 22/11 | Gốc repo = `...\CDNC_UngDungCongNgheTriThuc\src`, code ở `src/src/` | Thư mục mở trong VS Code |
| 22/11 | **Home Credit = dataset chính**, German Credit = phụ (thí nghiệm dữ liệu ít) | German: `job` V≈0, không có thu nhập |
| 22/11 | Hạn 02/12; G2 24/11 · G3 26/11 · G4 29/11 · G5 01/12; ưu tiên MUST/SHOULD/COULD | 10 ngày |
| 22/11 | Vai trò: Mạnh=Tri thức&Dữ liệu, Nam=BN, Khôi=ML&thực nghiệm, Phúc=LLM&demo | Mặc định theo thứ tự tên |
| 22/11 | Ngành: `ORGANIZATION_TYPE` → 10 nhóm theo ISIC Rev.4; Nghề: `OCCUPATION_TYPE` → 5 nhóm ISCO-08 (thiếu = `unknown`) | Chuẩn quốc tế có nguồn; `XNA` ≡ hưu trí/thất nghiệp ≡ `DAYS_EMPLOYED=365243` |
| 22/11 | Không dùng giới tính/hôn nhân làm đặc trưng | Thuộc tính nhạy cảm |
| 22/11 | Thu nhập & ext_score rời rạc theo ngũ phân vị (fit trên train); tuổi/thâm niên/DSTI/LTI/số con/tra cứu theo ngưỡng nghiệp vụ (`configs/discretize.yaml`) | Home Credit không công bố đơn vị tiền tệ |
| 22/11 | Tri thức vĩ mô lấy của **Việt Nam** (World Bank, WHO) – chỉ cho nút expert/what-if, không vào so sánh định lượng | Demo cho người dùng VN; dữ liệu không có biến vĩ mô |
| 22/11 | BN-Expert 2 lớp (data + expert); nối bằng **calibrated noisy-OR** (λ=0.3 giả định) để không làm sai phần học từ dữ liệu | Xem `configs/bn_expert.yaml` |
| 22/11 | LTI là nút `indicator` (lá) | Tránh phình CPT của `default`; vẫn là bằng chứng |

## Kết quả đã có
- EDA Home Credit: `reports/eda/home_credit.md`. Cramér's V với vỡ nợ: ext_score 0.213 ≫ years_employed 0.088 > age 0.077 > occupation 0.076 > sector 0.062 > region 0.061; income 0.025, DSTI 0.019, LTI 0.024.
- Vỡ nợ theo ngành: 5.4% (not_working) … 6.2% (nhà nước) … 10.2% (tự kinh doanh).
- **Phát hiện quan trọng:** thu nhập liên hệ yếu và không đơn điệu (chỉ Q5 thấp hơn); DSTI/LTI gần như không có tín hiệu, LTI ≥7x còn rủi ro thấp hơn → nghi **thiên lệch chọn mẫu** (chỉ có khoản vay đã duyệt). Mâu thuẫn tri thức chuyên gia ↔ dữ liệu → cần bàn trong báo cáo và thí nghiệm (7).
- FICO (sơ bộ, 1 lần chia 80/20, seed 42): AUC 0.692 < chỉ payment_history 0.704; amounts_owed AUC 0.504. Chưa phải kết quả chính thức (G4 làm CV).
- Tri thức: `knowledge_base/macro_vn_worldbank.csv` (CPI, thất nghiệp, GDP, chi y tế tự trả 2000–2024), `health_catastrophic_vn_who.csv` (SDG 3.8.2: 2018 – 8.83% <60 tuổi, 13.37% ≥60).
- DAG đề xuất: `configs/bn_expert.yaml`, hình `reports/figures/bn_expert_dag.png` (20 nút, 35 cạnh), mức ủng hộ từng cạnh `reports/eda/bn_expert_edge_support.md`.

## Vấn đề tồn đọng
- ⏸ Nhóm duyệt: DAG BN-Expert, luật FICO (`configs/fico.yaml`), λ & hệ số giả định của nút expert.
- CPT `default` có 5×5×5×5×3 = 1875 cấu hình cha (+ cashflow_shock) – có thể thưa ở đuôi; cân nhắc bớt `region_rating` nếu học kém.
- Chưa có nguồn: ngưỡng DSTI/LTI cụ thể; GSO thu nhập theo ngành & ngũ phân vị thu nhập VN (cho demo quy đổi VND).
- `import kaggle` tự in thông báo xác thực khi không có token – vô hại.

## Tiếp theo
1. Sau khi nhóm duyệt DAG: `configs/bn_expert_cpt.yaml` (CPT nút expert có nguồn/giả định) + `src/bn/model.py` (học MLE/BDeu, calibrated noisy-OR, suy luận xuôi, điểm 300–850 bằng log-odds).
2. Pipeline CV chung `src/evaluation/cv.py` (stratified 5-fold × 3 seed, lưu split) – Khôi.
3. Baseline ML (LR, XGBoost trước; RF, MLP sau) trên đặc trưng liên tục và rời rạc.
4. Phúc bắt đầu `LLMClient` + khung Streamlit song song.

## Nhật ký
- 22/11 – G1: khởi tạo repo, German Credit + EDA, TASKS.md, CLAUDE.md/Progress.md (`9d038ab`, `fc70414`, `d69f56a`).
- 22/11 – G2: Home Credit EDA, mapping ngành/nghề, rời rạc hóa, KB vĩ mô (WB+WHO), FICO baseline, DAG BN-Expert đề xuất, test G2; quy tắc tự cập nhật tài liệu trong CLAUDE.md.

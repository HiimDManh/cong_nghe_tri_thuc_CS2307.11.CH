# TASKS – Project 6: Dự báo khả năng tài chính cá nhân theo ngành nghề

Quy ước: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong. Mỗi việc ghi **Người phụ trách · Phụ thuộc · Tiêu chí hoàn thành (DoD)**.
Mỗi thành viên làm trên nhánh `feat/<module>`, merge qua PR, cần 1 người khác review.

| Ký hiệu | Thành viên | Vai trò |
|---|---|---|
| TV1 | **Mạnh** | Tri thức & Dữ liệu |
| TV2 | **Nam** | Mạng Bayes |
| TV3 | **Khôi** | Baseline ML & Khung thực nghiệm |
| TV4 | **Phúc** | LLM & Ứng dụng |

> Gán vai trò theo thứ tự tên nhóm cung cấp (mặc định) – nhóm có thể đổi, chỉ cần sửa bảng này.

**Ngày nộp & báo cáo: 02/12/2026.** Còn ~10 ngày → các giai đoạn chạy gối đầu; TV4 làm LLM/demo song song từ G2 (dùng BN tạm trên German Credit, thay bằng BN thật khi G3 xong).

| Giai đoạn | Nội dung | Hạn | Điểm dừng xin xác nhận |
|---|---|---|---|
| G1 | Khởi tạo | 22/11 ✅ | Cấu trúc repo + chốt dataset chính |
| G2 | Tri thức & dữ liệu | 24/11 | Duyệt DAG BN-Expert (tối 24/11) |
| G3 | Mô hình | 26/11 | – |
| G4 | Thực nghiệm | 29/11 | Bảng kết quả sơ bộ (tối 29/11) |
| G5 | LLM + demo + báo cáo | 01/12 | Đóng băng code trưa 01/12; slide + tập dượt tối 01/12 |

### Ưu tiên khi thiếu thời gian
- **Bắt buộc (MUST):** FICO baseline, BN-Expert, Naive Bayes, Logistic Regression, XGBoost; suy luận xuôi + ngược; thí nghiệm (1)(2)(3)(4)(5)(7); demo Streamlit chạy local với LLM (template + ít nhất 1 provider); báo cáo.
- **Nên có (SHOULD):** BN-Learned/Hybrid, TAN, RF, MLP; thí nghiệm (6)(8)(9); faithfulness tự động; deploy.
- **Nếu còn thời gian (COULD):** chấm thủ công LLM, EM cho biến ẩn, Give Me Some Credit.

---

## G1 – Khởi tạo

- [x] **Repo, `.gitignore`, `.env.example`, cấu trúc thư mục, `requirements.txt`, CLI/Makefile** — Khôi · – · PDF/PPT không bị track; `python -m src.cli data` chạy được.
- [x] **Tải German Credit + EDA nhanh** — Mạnh · repo · `reports/eda/german_credit.md` sinh từ script.
- [x] **Tải Home Credit `application_train.csv`** — Mạnh · tải tay từ Kaggle hoặc token API (xem README) · file nằm ở `data/raw/`, không bị commit.
- [x] **Chốt dataset chính** — cả nhóm · 2 việc trên · ghi quyết định vào README. _→ Home Credit (chính), German Credit (phụ)_

## G2 – Tri thức & dữ liệu

- [x] **EDA Home Credit** (`src/data/eda_home_credit.py`) — Mạnh · Home Credit · phân phối, tỷ lệ thiếu, tỷ lệ vỡ nợ theo `OCCUPATION_TYPE`/`ORGANIZATION_TYPE`. _→ reports/eda/home_credit.md_
- [x] **Bảng mapping ngành nghề → 6–10 nhóm ngành** (`knowledge_base/occupation_mapping.csv` + giải thích) — Mạnh · EDA · mọi giá trị gốc được ánh xạ; có cột `rationale`; nhóm có ≥ 1% mẫu. _→ 10 nhóm ngành (ISIC) + 5 nhóm nghề (ISCO-08)_
- [x] **Rời rạc hóa** (`src/data/discretize.py`, ngưỡng trong `configs/discretize.yaml`) — Mạnh + Nam · mapping · mỗi nút ≤ 5 trạng thái; mỗi ngưỡng có lý do (quantile hay nghiệp vụ); fit ngưỡng chỉ trên tập train.
- [~] **Knowledge base vĩ mô** (`knowledge_base/*.csv`: CPI/lạm phát, thất nghiệp – World Bank `wbgapi`; thu nhập theo ngành – GSO; rủi ro sức khỏe) — Mạnh · – · mỗi dòng có `source_url`, `year`; chỗ nào là giả định ghi rõ `assumption=true`. _WB + WHO xong; còn GSO thu nhập theo ngành & ngũ phân vị thu nhập VN_
- [~] **Baseline FICO rule-based** (`src/baselines/fico.py`) — Mạnh · rời rạc hóa · tái hiện 5 nhóm yếu tố (35/30/15/10/10) với bảng ánh xạ sang biến của dataset; **không còn mã đề tài cũ → cài lại tối giản**, luật ghi trong `configs/fico.yaml`, nhóm xác nhận luật. _đã cài; chờ nhóm xác nhận luật_
- [~] **Thiết kế DAG BN-Expert** (`configs/bn_expert.yaml` + hình `reports/figures/bn_expert_dag.png`) — Nam · mapping, knowledge base · có tối thiểu các cạnh trong đề; mỗi cạnh có lý do/nguồn. ⏸ **Nhóm duyệt trước khi học tham số.** _đề xuất xong; ⏸ chờ duyệt_

## G3 – Mô hình

- [ ] **Học tham số BN-Expert** (MLE + BDeu; EM cho biến ẩn) — Nam · DAG duyệt · CPT lưu được, nạp lại được.
- [ ] **BN-Learned (Hill-Climb + BIC) & BN-Hybrid (white/blacklist)** — Nam · rời rạc hóa · cấu trúc lưu `experiments/bn_structures/`.
- [ ] **Naive Bayes, TAN** — Nam · rời rạc hóa · cùng API `fit/predict_proba` với các mô hình khác.
- [ ] **Suy luận xuôi + ánh xạ điểm 300–850** (log-odds, công thức trong báo cáo) — Nam · BN · hàm `score(p_default)` đơn điệu giảm, có test.
- [ ] **Suy luận ngược: MAP query + counterfactual** trên biến điều khiển được — Nam · suy luận xuôi · trả về danh sách điều kiện cần + xác suất đạt mục tiêu; có ràng buộc thực tế.
- [ ] **Unit test BN** (DAG không chu trình, CPT tổng = 1, suy luận hợp lệ, đơn điệu) — Nam · các mục trên · `pytest` xanh.
- [ ] **Pipeline CV chung** (stratified 5-fold × 3 seed, cùng split cho mọi mô hình, cùng cách xử lý mất cân bằng) — Khôi · rời rạc hóa · split lưu ra file để tái lập.
- [ ] **Baseline ML: LR, RF, XGBoost/LightGBM, MLP** trên (a) đặc trưng liên tục và (b) đặc trưng rời rạc như BN — Khôi · pipeline CV · tuning ≤ 30 trial Optuna.

## G4 – Thực nghiệm (mỗi thí nghiệm → `experiments/<tên>/results.csv` + hình)

- [ ] **(1) Phân biệt: ROC-AUC, PR-AUC, Gini, KS** — Khôi · G3.
- [ ] **(2) Hiệu chỉnh: Brier, Log-loss, ECE + reliability diagram** — Khôi · G3.
- [ ] **(3) Ý nghĩa thống kê: DeLong / paired bootstrap 1.000 lần, CI 95%** — Khôi · (1).
- [ ] **(4) Thiếu thông tin: ẩn 10–50% đặc trưng lúc suy luận** — Nam · G3 · đường suy giảm AUC/Brier cho BN và ML (imputation).
- [ ] **(5) Dữ liệu ít: learning curve 1/5/10/25/100%** (+ German Credit) — Khôi · G3.
- [ ] **(6) Dịch chuyển theo ngành: train trên một số nhóm ngành, test nhóm còn lại** — Mạnh · mapping, G3.
- [ ] **(7) Nhất quán tri thức: tỷ lệ vi phạm đơn điệu/hướng tác động, BN vs SHAP XGBoost** — Nam · G3.
- [ ] **(8) Ổn định giải thích: Spearman/Kendall xếp hạng yếu tố giữa các fold, BN vs SHAP** — Phúc · G3.
- [ ] **(9) Chi phí: thời gian train/suy luận, bộ nhớ** — Khôi · G3.
- [ ] **Bảng tổng hợp + thảo luận trung thực** — Khôi · (1)–(9). ⏸ **Gửi nhóm bảng sơ bộ trước khi viết báo cáo.**

## G5 – LLM, demo, báo cáo

- [ ] **`LLMClient`** (Gemini / Groq / Ollama / template fallback, cache) — Phúc · – · đổi provider bằng `LLM_PROVIDER`; không key → vẫn chạy bằng template.
- [ ] **Prompt diễn giải từ dữ liệu có cấu trúc** (bằng chứng, hậu nghiệm, top yếu tố, kết quả suy luận ngược) — Phúc · suy luận ngược · đầu ra tiếng Việt, có câu miễn trừ.
- [ ] **Kiểm tra faithfulness tự động trên ~50 hồ sơ** + chấm thủ công (mỗi TV 10–15 mẫu, rubric 1–5) — Phúc (cả nhóm chấm) · prompt · tỷ lệ khớp số liệu/hướng tác động được báo cáo.
- [ ] **Streamlit demo**: form nhập, điểm 300–850, so sánh FICO/XGBoost, đồ thị nhân quả tô màu hậu nghiệm, tab suy luận ngược, tab what-if, tab lời khuyên LLM — Phúc · G3 · chạy từ model lưu sẵn, không train lại.
- [ ] **Deploy** Streamlit Community Cloud hoặc HF Spaces — Phúc · demo · link trong README.
- [ ] **Báo cáo `reports/report.md`** — mỗi TV viết chương của mình (Mạnh: Thu thập tri thức · Nam: Biểu diễn & thuật giải · Khôi: Thực nghiệm & thảo luận · Phúc: Hệ thống & demo) · G4 · mọi số liệu sinh từ script; có bảng "Điểm khác biệt so với đề tài FICO trước".
- [ ] **Slide + tập dượt** — cả nhóm · báo cáo · mỗi người trình bày phần mình.

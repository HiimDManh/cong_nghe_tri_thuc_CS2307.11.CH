# TASKS – Project 6: Dự báo khả năng tài chính cá nhân theo ngành nghề

Quy ước: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong. Mỗi việc ghi **Người phụ trách · Phụ thuộc · Tiêu chí hoàn thành (DoD)**.
Mỗi thành viên làm trên nhánh `feat/<module>`, merge qua PR, cần 1 người khác review.

| Ký hiệu | Vai trò |
|---|---|
| TV1 | Tri thức & Dữ liệu |
| TV2 | Mạng Bayes |
| TV3 | Baseline ML & Khung thực nghiệm |
| TV4 | LLM & Ứng dụng |

> **Mốc thời gian:** chờ nhóm xác nhận ngày nộp / ngày báo cáo → điền cột "Hạn" cho từng giai đoạn.

| Giai đoạn | Nội dung | Hạn | Điểm dừng xin xác nhận |
|---|---|---|---|
| G1 | Khởi tạo | _TBD_ | Cấu trúc repo + chốt dataset chính |
| G2 | Tri thức & dữ liệu | _TBD_ | Duyệt DAG BN-Expert |
| G3 | Mô hình | _TBD_ | – |
| G4 | Thực nghiệm | _TBD_ | Bảng kết quả sơ bộ |
| G5 | LLM + demo + báo cáo | _TBD_ | – |

---

## G1 – Khởi tạo

- [x] **Repo, `.gitignore`, `.env.example`, cấu trúc thư mục, `requirements.txt`, CLI/Makefile** — TV3 · – · PDF/PPT không bị track; `python -m src.cli data` chạy được.
- [x] **Tải German Credit + EDA nhanh** — TV1 · repo · `reports/eda/german_credit.md` sinh từ script.
- [ ] **Tải Home Credit `application_train.csv`** — TV1 · cần `kaggle.json` của một thành viên · file nằm ở `data/raw/`, không bị commit.
- [ ] **Chốt dataset chính** — cả nhóm · 2 việc trên · ghi quyết định vào README.

## G2 – Tri thức & dữ liệu

- [ ] **EDA Home Credit** (`src/data/eda_home_credit.py`) — TV1 · Home Credit · phân phối, tỷ lệ thiếu, tỷ lệ vỡ nợ theo `OCCUPATION_TYPE`/`ORGANIZATION_TYPE`.
- [ ] **Bảng mapping ngành nghề → 6–10 nhóm ngành** (`knowledge_base/occupation_mapping.csv` + giải thích) — TV1 · EDA · mọi giá trị gốc được ánh xạ; có cột `rationale`; nhóm có ≥ 1% mẫu.
- [ ] **Rời rạc hóa** (`src/data/discretize.py`, ngưỡng trong `configs/discretize.yaml`) — TV1 + TV2 · mapping · mỗi nút ≤ 5 trạng thái; mỗi ngưỡng có lý do (quantile hay nghiệp vụ); fit ngưỡng chỉ trên tập train.
- [ ] **Knowledge base vĩ mô** (`knowledge_base/*.csv`: CPI/lạm phát, thất nghiệp – World Bank `wbgapi`; thu nhập theo ngành – GSO; rủi ro sức khỏe) — TV1 · – · mỗi dòng có `source_url`, `year`; chỗ nào là giả định ghi rõ `assumption=true`.
- [ ] **Baseline FICO rule-based** (`src/baselines/fico.py`) — TV1 · rời rạc hóa · tái hiện 5 nhóm yếu tố (35/30/15/10/10) với bảng ánh xạ sang biến của dataset; nếu còn mã đề tài cũ thì tái sử dụng; nhóm xác nhận luật.
- [ ] **Thiết kế DAG BN-Expert** (`configs/bn_expert.yaml` + hình `reports/figures/bn_expert_dag.png`) — TV2 · mapping, knowledge base · có tối thiểu các cạnh trong đề; mỗi cạnh có lý do/nguồn. ⏸ **Nhóm duyệt trước khi học tham số.**

## G3 – Mô hình

- [ ] **Học tham số BN-Expert** (MLE + BDeu; EM cho biến ẩn) — TV2 · DAG duyệt · CPT lưu được, nạp lại được.
- [ ] **BN-Learned (Hill-Climb + BIC) & BN-Hybrid (white/blacklist)** — TV2 · rời rạc hóa · cấu trúc lưu `experiments/bn_structures/`.
- [ ] **Naive Bayes, TAN** — TV2 · rời rạc hóa · cùng API `fit/predict_proba` với các mô hình khác.
- [ ] **Suy luận xuôi + ánh xạ điểm 300–850** (log-odds, công thức trong báo cáo) — TV2 · BN · hàm `score(p_default)` đơn điệu giảm, có test.
- [ ] **Suy luận ngược: MAP query + counterfactual** trên biến điều khiển được — TV2 · suy luận xuôi · trả về danh sách điều kiện cần + xác suất đạt mục tiêu; có ràng buộc thực tế.
- [ ] **Unit test BN** (DAG không chu trình, CPT tổng = 1, suy luận hợp lệ, đơn điệu) — TV2 · các mục trên · `pytest` xanh.
- [ ] **Pipeline CV chung** (stratified 5-fold × 3 seed, cùng split cho mọi mô hình, cùng cách xử lý mất cân bằng) — TV3 · rời rạc hóa · split lưu ra file để tái lập.
- [ ] **Baseline ML: LR, RF, XGBoost/LightGBM, MLP** trên (a) đặc trưng liên tục và (b) đặc trưng rời rạc như BN — TV3 · pipeline CV · tuning ≤ 30 trial Optuna.

## G4 – Thực nghiệm (mỗi thí nghiệm → `experiments/<tên>/results.csv` + hình)

- [ ] **(1) Phân biệt: ROC-AUC, PR-AUC, Gini, KS** — TV3 · G3.
- [ ] **(2) Hiệu chỉnh: Brier, Log-loss, ECE + reliability diagram** — TV3 · G3.
- [ ] **(3) Ý nghĩa thống kê: DeLong / paired bootstrap 1.000 lần, CI 95%** — TV3 · (1).
- [ ] **(4) Thiếu thông tin: ẩn 10–50% đặc trưng lúc suy luận** — TV2 · G3 · đường suy giảm AUC/Brier cho BN và ML (imputation).
- [ ] **(5) Dữ liệu ít: learning curve 1/5/10/25/100%** (+ German Credit) — TV3 · G3.
- [ ] **(6) Dịch chuyển theo ngành: train trên một số nhóm ngành, test nhóm còn lại** — TV1 · mapping, G3.
- [ ] **(7) Nhất quán tri thức: tỷ lệ vi phạm đơn điệu/hướng tác động, BN vs SHAP XGBoost** — TV2 · G3.
- [ ] **(8) Ổn định giải thích: Spearman/Kendall xếp hạng yếu tố giữa các fold, BN vs SHAP** — TV4 · G3.
- [ ] **(9) Chi phí: thời gian train/suy luận, bộ nhớ** — TV3 · G3.
- [ ] **Bảng tổng hợp + thảo luận trung thực** — TV3 · (1)–(9). ⏸ **Gửi nhóm bảng sơ bộ trước khi viết báo cáo.**

## G5 – LLM, demo, báo cáo

- [ ] **`LLMClient`** (Gemini / Groq / Ollama / template fallback, cache) — TV4 · – · đổi provider bằng `LLM_PROVIDER`; không key → vẫn chạy bằng template.
- [ ] **Prompt diễn giải từ dữ liệu có cấu trúc** (bằng chứng, hậu nghiệm, top yếu tố, kết quả suy luận ngược) — TV4 · suy luận ngược · đầu ra tiếng Việt, có câu miễn trừ.
- [ ] **Kiểm tra faithfulness tự động trên ~50 hồ sơ** + chấm thủ công (mỗi TV 10–15 mẫu, rubric 1–5) — TV4 (cả nhóm chấm) · prompt · tỷ lệ khớp số liệu/hướng tác động được báo cáo.
- [ ] **Streamlit demo**: form nhập, điểm 300–850, so sánh FICO/XGBoost, đồ thị nhân quả tô màu hậu nghiệm, tab suy luận ngược, tab what-if, tab lời khuyên LLM — TV4 · G3 · chạy từ model lưu sẵn, không train lại.
- [ ] **Deploy** Streamlit Community Cloud hoặc HF Spaces — TV4 · demo · link trong README.
- [ ] **Báo cáo `reports/report.md`** — mỗi TV viết chương của mình (TV1: Thu thập tri thức · TV2: Biểu diễn & thuật giải · TV3: Thực nghiệm & thảo luận · TV4: Hệ thống & demo) · G4 · mọi số liệu sinh từ script; có bảng "Điểm khác biệt so với đề tài FICO trước".
- [ ] **Slide + tập dượt** — cả nhóm · báo cáo · mỗi người trình bày phần mình.

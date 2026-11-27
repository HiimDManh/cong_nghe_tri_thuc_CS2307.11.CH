# TASKS – Project 6: Dự báo khả năng tài chính cá nhân theo ngành nghề

> Rà soát lần cuối: **24/11/2026**. Còn 8 ngày tới hạn nộp (02/12).

Quy ước: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong. Mỗi việc ghi **Người phụ trách · Phụ thuộc · Tiêu chí hoàn thành (DoD)**.

## Nguyên tắc phân công (cập nhật 22/11)
Các thành viên dùng công cụ AI khác nhau (Claude, Gemini, Codex…) → để **tránh lệch code/mô hình/số liệu**:
- **Mạnh (+ Claude Code)** làm *toàn bộ* phần chạm vào code, dữ liệu, mô hình, thí nghiệm và mọi con số trong báo cáo.
- **Nam, Khôi, Phúc** làm việc *không sinh ra code hay số liệu mới*: đối chiếu nguồn, kiểm thử demo, chấm LLM thủ công, viết văn bản/slide **từ artefact đã sinh** (`reports/`, `experiments/`), chuẩn bị tài khoản deploy. Không sửa file trong `src/`, `configs/`, `knowledge_base/*.csv`; góp ý qua Issue/tin nhắn để Mạnh cập nhật.

| Thành viên | Vai trò |
|---|---|
| **Mạnh** | Chủ trì kỹ thuật: dữ liệu, tri thức, BN, ML, thí nghiệm, LLM, demo, số liệu báo cáo |
| **Nam** | Kiểm chứng tri thức & nguồn; viết chương "Thu thập & biểu diễn tri thức" từ artefact |
| **Khôi** | Kiểm thử demo (QA), viết chương "Thực nghiệm" từ bảng kết quả; slide |
| **Phúc** | Bộ hồ sơ mẫu + chấm LLM; tài khoản deploy; viết chương "Hệ thống & demo"; slide |

**Ngày nộp & báo cáo: 02/12/2026.**

| Giai đoạn | Nội dung | Hạn | Điểm dừng xin xác nhận |
|---|---|---|---|
| G1 | Khởi tạo | 22/11 ✅ | – |
| G2 | Tri thức & dữ liệu | 22/11 ✅ | DAG đã duyệt 22/11 |
| G3 | Mô hình | 26/11 → ✅ 22/11 | – |
| G4 | Thực nghiệm | 29/11 (chạy xong 22/11) | Bảng kết quả sơ bộ (tối 29/11) ⏸ |
| G5 | LLM + demo + báo cáo | 01/12 (đang làm: LLM thật ✅ 24/11, còn chấm tay/QA/deploy/chương 2, 5/slide) | Đóng băng code trưa 01/12; slide + tập dượt tối 01/12 |

### Ưu tiên khi thiếu thời gian
- **MUST:** FICO, BN-Expert(+Mono), Naive Bayes, LR, XGBoost; suy luận xuôi + ngược; thí nghiệm (1)(2)(3)(4)(5)(7); demo Streamlit chạy local + LLM (template + ≥1 provider); báo cáo.
- **SHOULD:** TAN, BN-Learned/Hybrid, RF, MLP; thí nghiệm (6)(8)(9); faithfulness tự động; deploy.
- **COULD:** chấm thủ công LLM mở rộng, EM cho biến ẩn, Give Me Some Credit.

---

## G1 – Khởi tạo ✅
- [x] Repo, `.gitignore`, `.env.example`, cấu trúc, `requirements.txt`, CLI/Makefile — Mạnh
- [x] German Credit + EDA — Mạnh
- [x] Home Credit `application_train.csv` — Mạnh
- [x] Chốt dataset chính: Home Credit (chính), German Credit (phụ)

## G2 – Tri thức & dữ liệu ✅
- [x] EDA Home Credit → `reports/eda/home_credit.md` — Mạnh
- [x] Mapping ngành (10 nhóm ISIC) + nghề (5 nhóm ISCO-08) → `knowledge_base/*_mapping.csv` — Mạnh
- [x] Rời rạc hóa → `configs/discretize.yaml`, `src/data/discretize.py` — Mạnh
- [x] KB vĩ mô (World Bank), sức khỏe (WHO), thu nhập/chi tiêu theo ngũ phân vị (GSO KSMS 2024), ngưỡng nợ — Mạnh
- [x] FICO rule-based → `configs/fico.yaml` (nhóm xác nhận 22/11) — Mạnh
- [x] DAG BN-Expert (nhóm duyệt 22/11) — Mạnh
- [x] **Đối chiếu bản gốc các nguồn còn ghi "cần đối chiếu"** trong `knowledge_base/debt_threshold_sources.csv` (FCA FG14/8 LTI 4.5; HCSF Pháp DSTI 35%; Estonia DSTI 50%) + mục tiêu lạm phát ~4% của VN — **Nam** · xong 25/11 trên branch `Nam` (merge vào `main` 27/11), kết quả ở `docs/handoff/nam_source_verification.csv`; Mạnh đã cập nhật `debt_threshold_sources.csv` + `knowledge_base/README.md` theo bản gốc. UK/Pháp/Estonia đúng; **mục tiêu lạm phát VN 2026 là ~4,5% (NQ 244/2025/QH15, Điều 2 khoản 4), không phải 4%** → 27/11 Mạnh chốt: giữ 4% làm ngưỡng rời rạc hóa (không gọi là mục tiêu; đổi 4,5% chỉ chuyển năm 2014), ghi rõ ở Ch.2.4.
- [x] (COULD) Thu nhập bình quân theo ngành kinh tế VN 2024 (GSO – Báo cáo lao động việc làm 2024, bảng thu nhập theo ngành) — **Nam** · đã trích Biểu 3.4/3.5 (25/11), nằm trong dòng 5 của `nam_source_verification.csv`; việc ánh xạ A–U → 10 nhóm ngành và nhập vào `knowledge_base` là của Mạnh.

## G3 – Mô hình
- [x] BN-Expert 2 lớp: CPT data (m-estimate, m=10), CPT expert sinh từ KB, calibrated noisy-OR — Mạnh · `src/bn/{core,expert_cpt,model}.py`
- [x] BN-Expert-Mono (ràng buộc đơn điệu DSTI↑ & ext_score↓, isotonic/POCS) — Mạnh
- [x] Suy luận xuôi theo lô (khớp pgmpy) + điểm 300–850 (log-odds, PDO≈52) — Mạnh
- [x] Suy luận ngược: posterior ngược, MAP (pgmpy), counterfactual do() trên 7 đòn bẩy — Mạnh · `src/bn/backward.py`, `configs/backward.yaml`
- [x] Naive Bayes, TAN, BN-Learned (HC+BIC), BN-Hybrid (HC + cạnh bắt buộc + thứ tự tầng) — Mạnh · `src/bn/variants.py`
- [x] Unit test BN (24 test, gồm đối chiếu pgmpy) — Mạnh
- [x] `python -m src.cli train` → `models/*.json` — Mạnh
- [x] Pipeline CV chung (stratified 5-fold × 3 seed, lưu split `experiments/splits/`) — Mạnh · `src/evaluation/cv.py`
- [x] Baseline ML: LR, XGBoost (Optuna 25 trial), XGBoost-Mono, LightGBM, RF, MLP; LR-disc, XGBoost-disc — Mạnh · `src/baselines/ml.py`

## G4 – Thực nghiệm (Mạnh chạy; mỗi thí nghiệm → `experiments/<tên>/results.csv` + hình)
- [x] (1) Phân biệt: ROC-AUC, PR-AUC, Gini, KS
- [x] (2) Hiệu chỉnh: Brier, Log-loss, ECE + reliability diagram
- [x] (3) Ý nghĩa thống kê: DeLong + Holm, paired bootstrap 1.000 lần, t-test Nadeau–Bengio
- [x] (4) Thiếu thông tin: MCAR 10–50% + 3 kịch bản có cấu trúc
- [x] (5) Dữ liệu ít: learning curve 1/5/10/25/100% · German Credit ✅
- [x] (6) Dịch chuyển theo ngành (leave-one-sector-out)
- [x] (7) Nhất quán tri thức: ICE vi phạm hướng tác động (6 biến)
- [x] (8) Ổn định giải thích giữa các fold, BN vs TreeSHAP/linear SHAP
- [x] (9) Chi phí: thời gian học/dự báo, số tham số, kích thước mô hình
- [x] Độ nhạy λ (0–0.5) + what-if
- [x] Bảng tổng hợp (`reports/results_summary.md`, Chương 4 phần kết quả) ⏸ **nhóm duyệt tối 29/11**
- [x] (Mạnh) Chẩn đoán XGBoost-disc @1% AUC≈0.5 – 27/11: early stopping bị bác bỏ; nguyên nhân là `min_child_weight`≈37 (tinh chỉnh trên dữ liệu đầy đủ) chặn mọi phép tách trên ext_score → `eval xgb_disc_diag`, bảng 5b, Ch.4.5. Bảng chính thức giữ nguyên.
- [ ] **Đọc bảng sơ bộ, đặt câu hỏi phản biện** (như hội đồng sẽ hỏi) — **Khôi, Nam** · bảng sơ bộ · danh sách câu hỏi gửi Mạnh trước 30/11.

## G5 – LLM, demo, báo cáo
- [x] Bộ tài liệu hướng dẫn dự án `docs/guide/` + bàn giao `docs/HANDOFF.md`, `docs/handoff/` — Mạnh
- [x] Khung báo cáo `reports/chapters/` + ghép tự động `python -m src.cli report` — Mạnh
- [x] `LLMClient` (Gemini/Groq/Ollama/template, cache) + prompt diễn giải + faithfulness tự động + đối chứng âm — Mạnh · `src/llm/` · Groq gpt-oss-120b + qwen3.8-27b chạy thật 24/11
- [x] Streamlit demo 6 tab (form VND, điểm, so sánh FICO/XGBoost, đồ thị nhân quả, suy luận ngược, what-if, LLM, CPT) — Mạnh · `src/app/`
- [ ] **Bộ ~50 hồ sơ mẫu đa dạng** (ngành, tuổi, thu nhập VND, chi tiêu, nợ…) dạng bảng CSV theo mẫu Mạnh gửi — **Phúc** · – · trước 27/11. _(24/11: `data/samples/profiles.csv` mới có 6 mẫu Mạnh tạo; chờ ~45 mẫu của Phúc theo `docs/handoff/phuc_profiles_spec.md`.)_
- [x] **Tạo API key Gemini (free) / Groq (free)** để test; **tài khoản Streamlit Community Cloud hoặc HF Spaces** — **Phúc** · – · key chỉ gửi riêng cho Mạnh, KHÔNG dán vào repo/chat nhóm. _(24/11: Groq ✅ trong `.env`; Gemini chưa có – không bắt buộc.)_
- [ ] **Chấm thủ công lời khuyên LLM** (rubric 1–5: đúng, dễ hiểu, hữu ích; mỗi người 15 hồ sơ riêng + 5 hồ sơ chung × 3 nguồn) — **Nam, Khôi, Phúc** · file sẵn 24/11: `experiments/llm_faithfulness/samples_for_rating.csv` (150 dòng: template, gpt-oss-120b, qwen3.8-27b) + `docs/handoff/llm_rating_rubric.md` · gửi Mạnh trước 30/11.
- [ ] (Mạnh) Gửi file chấm cho nhóm (24/11); nhận lại → tính điểm TB mỗi nguồn + độ đồng thuận → bảng trong Chương 4 · 30/11.
- [x] (Mạnh) Chọn model LLM mặc định cho demo: **qwen3.8-27b** (faithful 94% vs gpt-oss-120b 72%) – chốt 27/11 trong `configs/llm.yaml`; không chạy lại `cli llm` để giữ nguyên file chấm tay.
- [ ] **Kiểm thử demo (QA)** theo checklist: nhập liệu biên, thông báo lỗi, tốc độ, hiển thị tiếng Việt — **Khôi** · demo · danh sách lỗi gửi Mạnh trước 30/11.
- [ ] Deploy (Streamlit Cloud / HF Spaces) — Mạnh (+ Phúc hỗ trợ tài khoản) · repo đã push GitHub; cần tài khoản + đặt `GROQ_API_KEY` trong Secrets (`docs/DEPLOY.md`) · 28/11.
- [~] Báo cáo `reports/report.md`: Mạnh soạn khung + mọi bảng/số/hình; chương văn bản: **Nam** (Thu thập & biểu diễn tri thức), **Khôi** (Thực nghiệm & thảo luận), **Phúc** (Hệ thống & demo), Mạnh (Giới thiệu, thuật giải, kết luận). Văn bản chỉ trích số từ `reports/`/`experiments/`, không tự tính lại. _(24/11: Ch.1, 3, 4-kết quả (kể cả 4.11 LLM thật), 6, 7 xong; Ch.2 (Nam), Ch.5 + ảnh demo `reports/figures/demo_*.png` (Phúc), thảo luận Ch.4 (Khôi) còn khung gợi ý; ghép tự động 0 placeholder thiếu.)_
- [ ] Slide + tập dượt — cả nhóm (Khôi, Phúc dựng slide từ hình đã sinh) · mỗi người trình bày phần mình.

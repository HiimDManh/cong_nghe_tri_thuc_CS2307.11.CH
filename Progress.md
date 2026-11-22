# Progress

> File trạng thái cho mỗi phiên mới. Claude tự cập nhật trước mỗi commit (quy tắc trong CLAUDE.md). Chi tiết việc: `docs/TASKS.md`.
> Bàn giao nhóm: `docs/HANDOFF.md`. Tài liệu hiểu dự án: `docs/guide/`. Kết quả: `reports/results_summary.md`.

## Hiện tại (cập nhật 22/11/2026, tối)
- **Giai đoạn:** G3 ✅, G4 ✅ (đủ 9 thí nghiệm + độ nhạy λ + German), G5: LLM/demo/khung báo cáo ✅, còn việc phụ thuộc nhóm.
- **Chạy được:** `python -m src.cli data|eda|knowledge|dag|train|tune|eval|llm|report|app`; `pytest` **32 test pass**.
- **Báo cáo:** `reports/report.md` ghép tự động (0 placeholder thiếu). Mạnh đã viết Chương 1, 3, 4 (phần kết quả), 6, 7; Chương 2 (Nam), 5 (Phúc), thảo luận Chương 4 (Khôi) có khung + gợi ý.
- **Chờ từ nhóm:** API key Gemini/Groq (Phúc, 24/11) → chạy `python -m src.cli llm` với LLM thật + gửi file chấm tay; đối chiếu nguồn (Nam, 25/11); ~45 hồ sơ mẫu + lỗi QA (27/11); deploy (28/11).

## Quyết định đã chốt
| Ngày | Quyết định | Lý do |
|---|---|---|
| 22/11 | Home Credit chính, German Credit phụ (thí nghiệm dữ liệu ít) | German: `job` V≈0, không có thu nhập |
| 22/11 | Ngành 10 nhóm ISIC, nghề 5 nhóm ISCO-08; không dùng giới tính/hôn nhân | Chuẩn có nguồn; thuộc tính nhạy cảm |
| 22/11 | Thu nhập, ext_score: ngũ phân vị (fit train); còn lại ngưỡng nghiệp vụ | Không rõ đơn vị tiền tệ |
| 22/11 | BN-Expert 2 lớp, calibrated noisy-OR λ=0.3 (giả định); BN-Expert-Mono là mô hình chính | Nhóm chấp nhận; Mono tốt hơn & nhất quán tri thức |
| 22/11 | CPT: m-estimate (prior biên), m=10; suy luận chính xác theo lô tự cài (khớp pgmpy 1e-8) | BDeu cho 0.5 ở ô chưa gặp; VE quá chậm |
| 22/11 | Counterfactual do() trên 7 đòn bẩy (+2 dài hạn) | Thu nhập/chi tiêu không đủ đạt mục tiêu |
| 22/11 | ML dùng cùng 13 nhóm biến (cont + disc); không resample; XGBoost tinh chỉnh Optuna 25 trial trên train fold 0 | Công bằng thông tin, không rò rỉ |
| 22/11 | Thêm XGBoost-Mono (cùng ràng buộc như BN-Mono) | So sánh công bằng về nhúng tri thức |
| 22/11 | Giải thích BN/FICO = đóng góp **so với mức phổ biến** (baseline biên), không dùng "che bằng chứng" | Che bằng chứng cho kết quả khó hiểu ("lịch sử kém giúp tăng điểm") |
| 22/11 | Thí nghiệm 7 bỏ biến tuổi; thêm cột "biến phẳng" | Tri thức về tuổi mâu thuẫn; 0% vi phạm ở biến không tác động là vô nghĩa |
| 22/11 | Báo cáo: chương ở `reports/chapters/`, số chỉ qua `{{num:…}}` từ `key_numbers.json` | Thành viên dùng AI khác nhau → không gõ số tay |
| 22/11 | Phân công: Mạnh làm toàn bộ code/số liệu; Nam/Khôi/Phúc việc không sinh code | Tránh lệch |

## Kết quả đã có (chính thức, 5-fold × 3 seed; chi tiết `reports/results_summary.md`)
- AUC: XGBoost 0.740 > LightGBM 0.739 > … > TAN 0.727 > **BN-Expert-Mono 0.715** > BN-Expert 0.711 > FICO 0.692. Mọi khác biệt có ý nghĩa (DeLong+Holm, Nadeau–Bengio). Mono > Expert 15/15 fold. ECE Mono 0.0047 (XGBoost 0.0031).
- Thiếu thông tin (MCAR 50%): Bayes giảm ít nhất (Mono −0.049 vs XGBoost −0.119); từ 20% che Mono > XGBoost. NHƯNG thiếu ext_score: XGBoost > Mono (cấu trúc thưa).
- Dữ liệu ít: BN-Expert yếu (1%: 0.615; Mono 0.661; LR 0.715); German: BN-Expert kém nhất, NB ≈ LR. XGBoost-disc 1% AUC≈0.5 (nghi early stopping – chưa kiểm).
- Ngành mới: ~0 với mọi mô hình trừ BN-Expert ở nhóm not_working (−0.17: trạng thái cha chưa gặp → CPT về tỷ lệ nền); NB/TAN mất hiệu chỉnh.
- Nhất quán tri thức: Mono vi phạm TB 11.3% (thấp nhất trong mô hình học; chỉ ở thâm niên 67.5%; LTI/tra cứu phẳng) vs XGBoost 53.9%, LR 32.2%.
- Ổn định giải thích: NB 0.987, LR 0.978 > Mono 0.943 > XGBoost 0.888, LightGBM 0.864.
- λ: AUC 0.7168 (λ=0) → 0.7146 (0.3) → 0.7105 (0.5) do cắt p0 – **không hoàn toàn trung lập**; what-if λ=0.3: mất việc −72, sức khỏe −48 điểm.
- LLM: template faithful 100%, đối chứng âm 0% (bộ kiểm tra bắt được lỗi). Chưa chạy LLM thật (chưa có key).

## Vấn đề tồn đọng
- Chưa có API key → chưa có kết quả LLM thật + chấm tay.
- Nguồn ngưỡng nợ & mục tiêu lạm phát cần đối chiếu (Nam). Thu nhập theo ngành VN – COULD.
- XGBoost-disc @1% AUC≈0.5 – giả thuyết early stopping, chưa kiểm chứng.
- Hướng cải tiến đã ghi trong Chương 6 (CPT tham số hóa, ràng buộc thâm niên) – KHÔNG làm thêm để "thắng" trước khi nhóm duyệt bảng (29/11).
- Demo chưa deploy (cần tài khoản – Phúc; repo push – Mạnh).

## Tiếp theo
1. Khi có key: `.env` → `python -m src.cli llm` → `python -m src.cli eval tables` → `report`; gửi `experiments/llm_faithfulness/samples_for_rating.csv` cho nhóm chấm.
2. Nhận phản hồi nhóm (nguồn, hồ sơ mẫu, lỗi QA) → sửa → chạy lại phần liên quan.
3. Push GitHub + deploy Streamlit Cloud (`docs/DEPLOY.md`).
4. Tối 29/11: nhóm duyệt bảng kết quả; 01/12 đóng băng code.

## Nhật ký
- 22/11 – G1 khởi tạo (`9d038ab`, `fc70414`, `d69f56a`); G2 tri thức & dữ liệu, DAG (`3c08196`).
- 22/11 – G3-BN: core/expert/mono/backward/variants, models/*.json, phân công lại (`74a2e44`).
- 22/11 – G4: CV, 15 mô hình, 9 thí nghiệm + λ + German (~100 phút CPU); G5: LLM, demo Streamlit, khung báo cáo, tài liệu `docs/guide/`, bàn giao `docs/HANDOFF.md`.

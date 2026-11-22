# Dàn ý slide (~15–18 slide, 15 phút) – Khôi & Phúc dựng, cả nhóm trình bày

Nguyên tắc: **mọi con số lấy từ `reports/results_summary.md` hoặc `reports/results/key_numbers.json`** (không gõ lại
từ trí nhớ, không để AI tự điền). Hình lấy nguyên từ `reports/figures/`. Slide nộp là PDF/PPT – **không commit vào repo**.

| # | Nội dung | Hình / nguồn | Người nói |
|---|---|---|---|
| 1 | Tên đề tài, nhóm | – | Mạnh |
| 2 | Bài toán & chuỗi nhân quả Ngành → Thu nhập → Biến cố → Vỡ nợ | `01_gioi_thieu.md` §1.1 | Mạnh |
| 3 | Khác biệt so với FICO rule-based cũ (bảng) | `01_gioi_thieu.md` §1.3 | Mạnh |
| 4 | Dữ liệu & nguồn tri thức (Home Credit, World Bank, WHO, GSO) | `02_tri_thuc.md` §2.1 | Nam |
| 5 | DAG BN-Expert 2 lớp | `figures/bn_expert_dag.png` | Nam |
| 6 | CPT tri thức sinh từ nguồn + giả định | `reports/bn/expert_params.md` | Nam |
| 7 | Học tham số, calibrated noisy-OR, ràng buộc đơn điệu | `03_mo_hinh.md` §3.3–3.5 | Mạnh |
| 8 | Suy luận xuôi chính xác + điểm 300–850; suy luận ngược do() | `03_mo_hinh.md` §3.6–3.8 | Mạnh |
| 9 | Thiết lập thực nghiệm: 15 mô hình, 5-fold × 3 seed, công bằng thông tin | `03_mo_hinh.md` §3.9 | Khôi |
| 10 | (1)(2)(3) Phân biệt, hiệu chỉnh, kiểm định – **nói thẳng ML phân biệt tốt hơn** | `exp_roc.png`, `exp_reliability.png`, Bảng 1–2 | Khôi |
| 11 | (4) Thiếu thông tin | `exp_missing.png`, Bảng 3 | Khôi |
| 12 | (5) Dữ liệu ít (Home Credit + German) | `exp_learning_curve.png`, Bảng 4 | Khôi |
| 13 | (6) Dịch chuyển theo ngành | `exp_sector_shift.png`, Bảng 5 | Khôi |
| 14 | (7)(8) Nhất quán tri thức & ổn định giải thích | `exp_consistency.png`, `exp_stability.png` | Khôi |
| 15 | (9) Chi phí + độ nhạy λ | Bảng 8, `exp_lambda.png` | Khôi |
| 16 | Demo trực tiếp (hoặc ảnh chụp 6 tab) | `figures/demo_*.png` | Phúc |
| 17 | LLM diễn giải + kiểm tra độ trung thành | Bảng 10 | Phúc |
| 18 | Kết luận, hạn chế, hướng phát triển | `06_ket_luan.md` | Mạnh |

Câu hỏi hội đồng có thể hỏi (chuẩn bị trả lời – Khôi & Nam bổ sung):
- Vì sao BN thua XGBoost về AUC mà vẫn chọn BN? (→ thiếu thông tin, nhất quán, ổn định, suy luận ngược, what-if)
- λ = 0,3 lấy ở đâu? (→ giả định, độ nhạy, không ảnh hưởng độ chính xác khi không có bằng chứng biến cố)
- Dữ liệu Home Credit không phải của Việt Nam thì tri thức vĩ mô VN có hợp lệ không? (→ chỉ dùng cho lớp what-if)
- LLM có bịa số không? Kiểm tra thế nào? (→ faithfulness tự động + đối chứng âm + chấm tay)
- Thiên lệch chọn mẫu ở DSTI là gì? Vì sao cần ràng buộc đơn điệu?

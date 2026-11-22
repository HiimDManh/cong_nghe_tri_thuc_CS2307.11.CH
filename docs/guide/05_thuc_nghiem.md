# 5. Thực nghiệm: Mạng Bayes so với ML hộp đen

Code: `src/evaluation/`. Cấu hình: `configs/eval.yaml`. Kết quả thô: `experiments/<tên>/results.csv`. Bảng đọc nhanh:
`reports/results_summary.md`. Tài liệu này mô tả **thiết kế** và **cách đọc**; số liệu xem các file kết quả.

## 5.1. Nguyên tắc
1. **Không rò rỉ.**
   - Mọi bước học từ dữ liệu (ngưỡng ngũ phân vị, CPT, chuẩn hóa, tinh chỉnh) chỉ dùng train của từng fold.
   - Early stopping của XGBoost/LightGBM dùng 10% tách từ train.
   - Optuna chỉ chạy trên train của fold 0.
2. **Công bằng thông tin.** Mọi mô hình dùng cùng 13 nhóm biến. ML có hai dạng đầu vào:
   - liên tục: giá trị gốc;
   - rời rạc: đúng trạng thái BN, mã hóa one-hot.

   Dạng rời rạc giúp tách hai câu hỏi: "thua vì rời rạc hóa" hay "thua vì cấu trúc".
3. **Không xử lý mất cân bằng bằng resample.** Mọi mô hình xuất xác suất và được chấm bằng chỉ số xác suất.
   Resample làm hỏng hiệu chỉnh.
4. **Trung thực.** Không chỉnh thí nghiệm để BN thắng. Kết quả bất lợi cho BN vẫn được báo cáo. Ví dụ: ML phân biệt
   tốt hơn; BN-Expert yếu trên German Credit.
5. **Tái lập.**
   - Seed cố định (42, 43, 44).
   - Split lưu ở `experiments/splits/home_credit_folds.npz`.
   - Phiên bản thư viện ghim trong `requirements.txt`.

## 5.2. Mười lăm mô hình
| Họ | Mô hình |
|---|---|
| Luật | **FICO** – tái hiện đề tài cũ. Điểm theo luật; chỉ học ánh xạ điểm → xác suất bằng Platt scaling (logistic 1 biến) để so được Brier/ECE |
| Bayes (đề xuất) | **BN-Expert**, **BN-Expert-Mono** |
| Bayes (so sánh cấu trúc) | Naive Bayes, TAN, BN-Learned, BN-Hybrid |
| ML liên tục | LR, XGBoost (tinh chỉnh Optuna), XGBoost-Mono, LightGBM, RF, MLP |
| ML rời rạc | LR-disc, XGBoost-disc |

## 5.3. Quy trình đánh giá chính
- **Stratified 5-fold × 3 seed = 15 lần.** Mỗi lần: học trên 80%, dự báo 20%. Stratified nghĩa là mỗi fold có cùng
  tỷ lệ vỡ nợ.
- Dự báo trên phần test của mọi fold được ghép lại thành dự báo **OOF** (out-of-fold): mỗi hồ sơ có đúng một dự
  báo, từ một mô hình chưa từng thấy hồ sơ đó.
- Mô hình của seed 42 được lưu vào `data/interim/` để các thí nghiệm sau dùng lại, không phải học lại.

## 5.4. Các chỉ số (`src/evaluation/metrics.py`)
| Chỉ số | Đo gì | Tốt khi | Ghi chú |
|---|---|---|---|
| ROC-AUC | Xác suất một người vỡ nợ ngẫu nhiên được xếp rủi ro cao hơn một người không vỡ nợ ngẫu nhiên | Cao (0,5 = đoán bừa) | Chỉ đo thứ hạng |
| Gini | 2·AUC − 1 | Cao | Thuật ngữ quen thuộc trong ngân hàng |
| KS | Khoảng cách lớn nhất giữa hai đường phân phối tích lũy (vỡ nợ / không vỡ nợ) | Cao | |
| PR-AUC | Diện tích dưới đường Precision–Recall | Cao | Nhạy với lớp hiếm (8%) |
| Brier | Trung bình (p − y)² | Thấp | Gồm cả phân biệt lẫn hiệu chỉnh |
| Log-loss | −trung bình [y·ln p + (1−y)·ln(1−p)] | Thấp | Phạt nặng khi tự tin mà sai |
| ECE | Trung bình có trọng số của \|tỷ lệ vỡ nợ thật − xác suất dự báo\| theo bin | Thấp | Dự án dùng 15 bin **cùng số mẫu**, vì đa số dự báo nằm dưới 20% |
| Reliability diagram | Đồ thị xác suất dự báo (trục ngang) với tỷ lệ thật (trục dọc) | Bám đường chéo | `reports/figures/exp_reliability.png` |

## 5.5. Kiểm định thống kê (thí nghiệm 3)
| Phép kiểm định | Dùng cho | Ý tưởng |
|---|---|---|
| **DeLong** | So sánh hai AUC trên cùng tập test | Ước lượng phương sai của AUC từ thống kê U (Mann–Whitney), có tính tương quan giữa hai mô hình. Cài đặt nhanh O(n log n) |
| **Holm–Bonferroni** | Nhiều phép so sánh cùng lúc | Hiệu chỉnh p-value để tránh "may mắn" khi so một mô hình với 14 mô hình |
| **Paired bootstrap 1.000 lần** | Δ Brier, Δ Log-loss, Δ ECE | Lấy mẫu lại hồ sơ có hoàn lại, cùng mẫu cho cả hai mô hình; khoảng 2,5%–97,5% của hiệu số là CI 95% |
| **t-test hiệu chỉnh Nadeau–Bengio** | Hiệu số trên 15 cặp fold | t-test thường đánh giá thấp phương sai vì các fold dùng chung dữ liệu train; hiệu chỉnh nhân thêm (1/k + n_test/n_train) |

Cách đọc:
- p < 0,05 sau hiệu chỉnh nghĩa là khác biệt có ý nghĩa thống kê.
- CI không chứa 0 nghĩa là khác biệt chắc chắn về chiều.
- Có ý nghĩa thống kê chưa chắc đã có ý nghĩa thực tế. Ví dụ ΔAUC 0,002 vẫn có thể có p rất nhỏ khi n = 307k.

## 5.6. Chín thí nghiệm
| # | Tên (thư mục `experiments/`) | Câu hỏi | Thiết kế |
|---|---|---|---|
| 1 | `main_cv` | Mô hình nào phân biệt tốt hơn? | AUC, PR-AUC, Gini, KS trên 15 lần |
| 2 | `main_cv` | Xác suất có đáng tin không? | Brier, Log-loss, ECE, reliability diagram |
| 3 | `significance` | Khác biệt có thật không? | Mục 5.5; hai mô hình tham chiếu là BN-Expert-Mono và XGBoost |
| 4 | `missing` | Khi người dùng không khai đủ thông tin thì sao? | Mô hình học trên dữ liệu **đầy đủ**, chỉ che lúc dự báo. (a) Che ngẫu nhiên 0–50% nhóm biến; (b) ba kịch bản có cấu trúc: không có điểm tín dụng ngoài; không có lịch sử tín dụng; `thin_file` – khách hàng mới chỉ có nhân khẩu, nghề, thu nhập |
| 5 | `learning_curve`, `german_small_data` | Khi ít dữ liệu thì sao? | Học trên 1/5/10/25/100% tập train Home Credit, test trên fold đầy đủ; German Credit 1.000 hồ sơ, 10 × 5-fold, học trên 25/50/100% |
| 6 | `sector_shift` | Mô hình có tổng quát hóa sang ngành **chưa từng thấy**? | Leave-one-sector-out: học trên 9 nhóm ngành, test nhóm còn lại; so với dự báo khi ngành đó có trong train |
| 7 | `consistency` | Mô hình có đi ngược tri thức không? | ICE: với 5.000 hồ sơ, đổi một biến qua mọi mức (giữ nguyên các biến khác), đếm tỷ lệ hồ sơ có bước rủi ro đi ngược hướng tri thức (> 0,1 điểm %). 6 biến có hướng rõ: DSTI ↑, LTI ↑, lịch sử tín dụng ↓, thâm niên ↓, tra cứu ↑, thu nhập ↓. **Tuổi bị loại** vì tri thức mâu thuẫn |
| 8 | `stability` | Giải thích có ổn định khi dữ liệu học thay đổi? | 2.000 hồ sơ cố định, giải thích bởi 5 mô hình học trên 5 fold. Đo tương quan hạng (Spearman) của độ quan trọng, Jaccard top-3, đồng dấu |
| 9 | `cost` | Tốn bao nhiêu? | Thời gian học, thời gian dự báo / 10k hồ sơ, số tham số, kích thước mô hình |
| + | `lambda_sensitivity` | Giả định λ ảnh hưởng thế nào? | λ ∈ {0; 0,1; …; 0,5}: chỉ số dự báo khi không có biến cố; Δ điểm khi bật từng biến cố |
| + | `llm_faithfulness` | LLM có trung thành với dữ kiện? | Xem tài liệu 6 |

**Cách mô hình xử lý dữ liệu thiếu ở thí nghiệm 4.** Đây là điểm hay bị hỏi.
- BN lấy biên chính xác.
- FICO cho điểm thành phần trung tính 0,5.
- XGBoost/LightGBM dùng "nhánh mặc định" học cho NaN; nhánh này gần như không được huấn luyện vì train không thiếu.
- LR/RF/MLP điền trung vị của train.
- ML rời rạc: one-hot toàn 0.
- Không đi làm ≠ thiếu thông tin: cột `not_working` riêng giữ phân biệt này.

**Cách đọc thí nghiệm 7.**
- Tỷ lệ vi phạm của BN-Expert-Mono và XGBoost-Mono bằng 0 ở hai biến được ràng buộc là **do thiết kế**, không phải
  phát hiện. Khi trình bày phải nói rõ điều này.
- Biến được ràng buộc gồm DSTI (`annuity_to_income`) và lịch sử tín dụng (`ext_score_mean`). Các biến khác là kết
  quả thực sự.

## 5.7. Bảng, hình, báo cáo được sinh ra thế nào
- `src/evaluation/tables.py` đọc `experiments/*/results.csv` và sinh:
  - `reports/results/<bảng>.md`;
  - `key_numbers.json` (số chính có tên);
  - `reports/results_summary.md`.
- `src/evaluation/figures.py` sinh `reports/figures/exp_*.png`. Mỗi mô hình có một màu cố định trên mọi hình.
- `src/evaluation/report.py` ghép `reports/chapters/*.md` thành `reports/report.md`, thay `{{num:…}}`, `{{table:…}}`,
  `{{fig:…}}`. Thiếu dữ liệu thì in `⟦THIẾU …⟧` và **không bao giờ tự điền số**.

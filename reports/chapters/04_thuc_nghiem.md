## 4. Thực nghiệm: Mạng Bayes so với Black-box ML

<!-- Phần "Kết quả" do Mạnh viết; mọi số chèn tự động bằng {{num:…}}/{{table:…}}. Ô "Khôi – thảo luận" do Khôi
viết: giải thích VÌ SAO, liên hệ thực tế cho vay, KHÔNG gõ lại số (nếu cần số thì dùng {{num:…}} trong
reports/results/key_numbers.json). -->

### 4.1. Thiết lập
- Dữ liệu: Home Credit 307.511 hồ sơ, cùng 13 nhóm biến cho mọi mô hình. Danh sách 15 mô hình ở mục 3.9.
- Đánh giá: stratified 5-fold × 3 seed (15 lần). Mọi bước học, kể cả ngưỡng rời rạc hóa và tinh chỉnh, chỉ dùng
  train của fold.
- Chi tiết thiết kế từng thí nghiệm: `docs/guide/05_thuc_nghiem.md`.
- Toàn bộ thực nghiệm chạy khoảng 100 phút trên CPU 16 luồng (`python -m src.cli eval`).

### 4.2. Phân biệt và hiệu chỉnh (thí nghiệm 1, 2)
{{table:main_cv}}

{{fig:exp_roc.png|ROC của 4 mô hình đại diện (dự báo OOF, seed 42)}}

{{fig:exp_reliability.png|Biểu đồ hiệu chỉnh}}

**Kết quả.**
- **ML hộp đen phân biệt tốt nhất.** {{num:best_auc_model}} đạt AUC {{num:auc.XGBoost}}. BN-Expert-Mono đạt
  {{num:auc.BN-Expert-Mono}}, thấp hơn {{num:gap_best_vs_bnmono}}. Nhóm không chỉnh thí nghiệm để thu hẹp khoảng
  cách này.
- **BN-Expert-Mono hơn FICO rule-based {{num:gap_bnmono_vs_fico}} AUC.** FICO đạt {{num:auc.FICO}}. Học xác suất từ
  dữ liệu có lợi rõ so với luật cố định.
- **Ràng buộc tri thức không làm giảm độ chính xác.** BN-Expert-Mono ({{num:auc.BN-Expert-Mono}}) tốt hơn BN-Expert
  học thuần ({{num:auc.BN-Expert}}).
- **Trong họ Bayes:**
  - TAN phân biệt tốt nhất ({{num:auc.TAN}}) nhưng hiệu chỉnh kém hơn: ECE {{num:ece.TAN}} so với
    {{num:ece.BN-Expert-Mono}} của BN-Expert-Mono.
  - Naive Bayes hiệu chỉnh kém nhất: ECE {{num:ece.Naive Bayes}}.
  - BN-Learned (máy tự học cấu trúc) đạt {{num:auc.BN-Learned}}. Như đã ghi ở G3, nó còn đảo chiều nhiều cạnh nhân
    quả.
- **Mất mát do rời rạc hóa và do cấu trúc.**
  - XGBoost trên đúng trạng thái BN (XGBoost-disc) đạt {{num:auc.XGBoost-disc}}, LR-disc đạt {{num:auc.LR-disc}}.
  - Như vậy một phần khoảng cách đến từ rời rạc hóa. Phần còn lại đến từ cấu trúc thưa của BN-Expert: nút Vỡ nợ chỉ
    có 5 cha dữ liệu, các biến khác chỉ ảnh hưởng gián tiếp.
- **Hiệu chỉnh.** Mọi mô hình trừ Naive Bayes và TAN có ECE dưới 1%. BN-Expert-Mono có Log-loss
  {{num:logloss.BN-Expert-Mono}}, so với {{num:logloss.XGBoost}} của XGBoost.

<!-- Khôi – thảo luận 4.2: vì sao boosting mạnh trên dữ liệu bảng; khoảng cách AUC này có ý nghĩa thực tế ra sao với
ngân hàng (xếp hạng vs xác suất); vì sao TAN tốt hơn BN-Expert về AUC nhưng không dùng được cho suy luận nhân quả. -->

### 4.3. Ý nghĩa thống kê (thí nghiệm 3)
{{table:significance}}

**Kết quả.**
- Mọi khác biệt AUC giữa BN-Expert-Mono và các mô hình khác đều có ý nghĩa thống kê, theo cả DeLong (sau hiệu chỉnh
  Holm) và t-test Nadeau–Bengio. Lý do: n = 307.511 rất lớn và các chênh lệch nhất quán giữa các fold (cột "Thắng").
- BN-Expert-Mono thắng BN-Expert ở 15/15 cặp fold.
- XGBoost thắng mọi mô hình khác ở 15/15 cặp fold.
- Với n lớn, khác biệt rất nhỏ vẫn có thể "có ý nghĩa thống kê". Vì vậy phải đọc kèm độ lớn hiệu ứng (cột Δ).

<!-- Khôi – thảo luận 4.3: ý nghĩa thống kê vs ý nghĩa thực tế; vì sao cần hiệu chỉnh Holm và t-test hiệu chỉnh. -->

### 4.4. Thiếu thông tin lúc suy luận (thí nghiệm 4)
{{table:missing}}

{{fig:exp_missing.png|AUC và Log-loss khi che ngẫu nhiên một tỷ lệ nhóm biến}}

**Thiếu ngẫu nhiên.**
- Họ Bayes suy giảm **chậm nhất**. Khi che 50% nhóm biến, AUC của BN-Expert-Mono giảm
  {{num:missing_drop50.BN-Expert-Mono}}, trong khi XGBoost giảm {{num:missing_drop50.XGBoost}} và LightGBM giảm
  {{num:missing_drop50.LightGBM}}.
- Ở mức che 10%, XGBoost vẫn hơn ({{num:missing_auc10.XGBoost}} so với {{num:missing_auc10.BN-Expert-Mono}}).
  Từ 20% trở lên, BN-Expert-Mono vượt XGBoost: ở 20% là {{num:missing_auc20.BN-Expert-Mono}} so với
  {{num:missing_auc20.XGBoost}}; ở 30% là {{num:missing_auc30.BN-Expert-Mono}} so với {{num:missing_auc30.XGBoost}}.
  Log-loss của BN cũng tăng chậm hơn nhiều.
- Lý do: BN lấy biên chính xác theo xác suất. XGBoost đi theo "nhánh mặc định" cho NaN, nhánh mà nó gần như chưa
  được học, vì dữ liệu train không thiếu.

**Thiếu có cấu trúc** — kết quả trái chiều, báo cáo trung thực:
- Khi thiếu điểm tín dụng ngoài (`no_ext_score`), XGBoost ({{num:missing_no_ext_score.XGBoost}}) **tốt hơn**
  BN-Expert-Mono ({{num:missing_no_ext_score.BN-Expert-Mono}}).
- Với khách hàng mới chỉ có nhân khẩu và nghề nghiệp (`thin_file`), BN-Expert-Mono
  ({{num:missing_thin_file.BN-Expert-Mono}}) hơn XGBoost ({{num:missing_thin_file.XGBoost}}), nhưng thua TAN, RF
  và LR.
- Nguyên nhân: cấu trúc chuyên gia thưa. Khi mất biến mạnh nhất, thông tin từ học vấn, tuổi, ngành chỉ đến nút Vỡ
  nợ qua vài đường gián tiếp. Đây là cái giá của một cấu trúc dễ giải thích.

<!-- Khôi – thảo luận 4.4: ý nghĩa với demo (người dùng hay để trống), với khách hàng chưa có lịch sử tín dụng. -->

### 4.5. Dữ liệu ít (thí nghiệm 5)
{{table:learning_curve}}

{{fig:exp_learning_curve.png|AUC và ECE theo cỡ tập học (Home Credit)}}

**Kết quả.**
- **BN-Expert cần nhiều dữ liệu.** CPT của nút Vỡ nợ có hàng nghìn ô. Với 1% dữ liệu (~2.460 hồ sơ), BN-Expert chỉ
  đạt {{num:lc_auc_1pct.BN-Expert}}, trong khi LR đạt {{num:lc_auc_1pct.LR}} và Naive Bayes đạt
  {{num:lc_auc_1pct.Naive Bayes}}. Trên German Credit (bảng c), BN chuyên gia nhỏ cũng kém nhất.
- **Ràng buộc đơn điệu giúp rõ khi ít dữ liệu.** Ở 1%, BN-Expert-Mono đạt {{num:lc_auc_1pct.BN-Expert-Mono}} so
  với {{num:lc_auc_1pct.BN-Expert}} của BN-Expert. Tri thức chuyên gia bù một phần cho dữ liệu thiếu.
  BN-Expert-Mono cũng giữ ECE thấp ở mọi cỡ mẫu ({{num:lc_ece_1pct.BN-Expert-Mono}} ở 1%).
- **Mô hình ít tham số học nhanh nhất.** Naive Bayes và LR gần như bão hòa từ 5–10% dữ liệu.
- **Một bất thường và nguyên nhân.** XGBoost-disc ở 1% có AUC ≈ 0,5 ({{num:xgbd_auc.disc_1%_asis}}). Chúng tôi
  chẩn đoán riêng (`python -m src.cli eval xgb_disc_diag`, bảng 5b) hai giả thuyết:
  - *Early stopping dừng sớm* (tập validation nội bộ chỉ có {{num:xgbd_val_pos_1pct}} ca vỡ nợ): **bị bác bỏ**.
    Mô hình vẫn chạy đến vòng {{num:xgbd_iter.disc_1%_asis}} (trung vị). Tắt early stopping (500 cây) vẫn chỉ đạt
    {{num:xgbd_auc.disc_1%_noes}}.
  - *`min_child_weight` đã tinh chỉnh quá lớn so với dữ liệu nhỏ*: **được xác nhận**. Optuna chọn
    `min_child_weight` = {{num:xgbd_mcw_tuned}} trên toàn bộ train fold 0 (~246 nghìn hồ sơ). Tham số này là ngưỡng
    *tổng hessian* của mỗi lá, nên không co giãn theo cỡ mẫu. Ở tỷ lệ vỡ nợ ≈ 8%, mỗi hồ sơ đóng góp hessian
    ≈ 0,074, nên mỗi lá cần khoảng 500 hồ sơ. Với {{num:xgbd_n_train_1pct}} hồ sơ train nội bộ, chỉ
    {{num:xgbd_feasible.disc_1%_asis}}/{{num:xgbd_nfeat.disc_1%_asis}} cột one-hot còn tách được. Cả 5 trạng thái
    của điểm lịch sử tín dụng (mỗi ngũ phân vị ~440 hồ sơ) đều không tách được, mà đây là biến mạnh nhất. Cây chỉ tách
    trên các biến yếu nên dự đoán gần như hằng số. Đặt `min_child_weight` = 1 thì AUC lên {{num:xgbd_auc.disc_1%_mcw1}}
    (tham số chưa tinh chỉnh, `min_child_weight` = 10: {{num:xgbd_auc.disc_1%_untuned}}). XGBoost liên tục không bị
    ảnh hưởng ({{num:xgbd_auc.cont_1%_asis}}) vì ngưỡng liên tục luôn chọn được điểm cắt đủ cân bằng.
  - *Hệ quả.* Đây là lỗi chuyển tham số từ dữ liệu lớn sang dữ liệu nhỏ, không phải giới hạn của XGBoost. Bảng
    learning curve chính thức giữ nguyên để minh bạch, nhưng khi so ở 1% nên dùng mốc đã sửa
    ({{num:xgbd_auc.disc_1%_mcw1}}). Mốc này vẫn cao hơn BN-Expert ({{num:lc_auc_1pct.BN-Expert}}) và
    BN-Expert-Mono ({{num:lc_auc_1pct.BN-Expert-Mono}}), nên kết luận "BN-Expert cần nhiều dữ liệu" không đổi.

{{table:xgb_disc_diag}}

<!-- Khôi – thảo luận 4.5: đánh đổi số tham số – dữ liệu; gợi ý CPT tham số hóa (noisy-OR/logistic) cho nút nhiều cha. -->

### 4.6. Dịch chuyển theo ngành (thí nghiệm 6)
{{table:sector_shift}}

{{fig:exp_sector_shift.png|Δ AUC khi ngành không có trong dữ liệu học}}

**Kết quả.**
- **Ngành mới (9 nhóm):** hầu hết mô hình gần như không suy giảm. BN-Expert-Mono thay đổi
  {{num:sector_dauc_excl.BN-Expert-Mono}} AUC, XGBoost thay đổi {{num:sector_dauc_excl.XGBoost}}. Lý do là ngành có
  tác động trực tiếp yếu tới vỡ nợ.
- **Nhóm "không đi làm" là thất bại rõ của BN-Expert.**
  - ΔAUC = {{num:sector_dauc_notworking.BN-Expert-Mono}}.
  - Khi nhóm này bị loại khỏi train, trạng thái thâm niên `not_working` (một cha của nút Vỡ nợ) chưa từng xuất hiện.
    CPT dạng bảng khi đó lùi về tỷ lệ nền và mất toàn bộ thông tin từ các cha khác.
  - Các mô hình cộng tính (LR, cây) vẫn dùng được các biến còn lại.
- **Naive Bayes và TAN mất hiệu chỉnh khi gặp trạng thái mới.** Sai lệch \|p̄ − ȳ\| là {{num:sector_citl.Naive Bayes}}
  với Naive Bayes, so với {{num:sector_citl.BN-Expert-Mono}} của BN-Expert-Mono. Trạng thái chưa gặp ở nút con làm
  méo tỷ số hợp lý.

<!-- Khôi – thảo luận 4.6: hạn chế của CPT dạng bảng khi ngoại suy; cách khắc phục (chia sẻ tham số, prior theo
cấu trúc ngành); ý nghĩa với người dùng thuộc nhóm ít dữ liệu. -->

### 4.7. Nhất quán với tri thức chuyên gia (thí nghiệm 7)
{{table:consistency}}

{{fig:exp_consistency.png|Tỷ lệ hồ sơ có dự báo đi ngược hướng tri thức}}

**Kết quả.**
- **BN-Expert-Mono có tỷ lệ vi phạm trung bình thấp nhất trong các mô hình học từ dữ liệu:**
  {{num:violation.BN-Expert-Mono}}, so với XGBoost {{num:violation.XGBoost}}, LightGBM {{num:violation.LightGBM}},
  LR {{num:violation.LR}}. FICO bằng 0 vì là luật viết tay.
- Cần đọc đúng con số của BN-Expert-Mono:
  - 0% ở DSTI và lịch sử tín dụng là **do thiết kế** (ràng buộc).
  - LTI và số lần tra cứu **không có tác động** (cột "phẳng") do d-separation, nên 0% ở đó không chứng minh điều gì.
  - Chỉ có thu nhập là tuân thủ đúng nghĩa; thu nhập tác động qua nút đệm tài chính của lớp tri thức.
  - Thâm niên vẫn vi phạm ở {{num:violation_feat.BN-Expert-Mono.years_employed}} hồ sơ. Thâm niên không nằm trong
    ràng buộc đơn điệu, nên đây là ứng viên tự nhiên cho ràng buộc tiếp theo.
- **Chính dữ liệu chứa quan hệ ngược tri thức.**
  - LR, một mô hình đơn giản, vi phạm ở {{num:violation_feat.LR.income}} hồ sơ với thu nhập và
    {{num:violation_feat.LR.credit_to_income}} với LTI.
  - Lý do: khi giữ nguyên DSTI, thu nhập cao hơn lại đi kèm rủi ro cao hơn. Đây là dấu hiệu của thiên lệch chọn mẫu.
  - Ngay cả XGBoost-Mono ({{num:violation.XGBoost-Mono}}) vẫn vi phạm ở các biến không ràng buộc.
- Tri thức trong cấu trúc BN chặn được các quan hệ ngược này. Đó là điều kiện cần để tư vấn "nên giảm nợ" một cách
  nhất quán.

<!-- Khôi – thảo luận 4.7: vì sao vi phạm tri thức nguy hiểm khi dùng mô hình để TƯ VẤN (khác với chỉ xếp hạng). -->

### 4.8. Ổn định giải thích (thí nghiệm 8)
{{table:stability}}

{{fig:exp_stability.png|Ổn định giải thích giữa 5 fold}}

**Kết quả.**
- Giải thích cục bộ của BN-Expert-Mono ổn định hơn các mô hình boosting: Spearman {{num:stab_local.BN-Expert-Mono}}
  so với XGBoost {{num:stab_local.XGBoost}} và LightGBM {{num:stab_local.LightGBM}}.
- Tuy nhiên BN-Expert-Mono vẫn kém các mô hình rất đơn giản như Naive Bayes và LR.
- Mọi mô hình đều xếp lịch sử tín dụng là yếu tố quan trọng nhất.
- Thứ hạng độ quan trọng toàn cục giữa BN-Expert-Mono và XGBoost chỉ tương quan ρ = {{num:importance_rho_bnmono_xgb}}.
  Hai mô hình "giải thích" cùng dữ liệu theo cách khác nhau: BN theo cấu trúc nhân quả, XGBoost theo tương quan.

### 4.9. Chi phí (thí nghiệm 9)
{{table:cost}}

BN học trong vài giây và có kích thước khoảng 116 KB. Mô hình demo lưu dạng JSON, chạy được trên máy chủ miễn phí. Mô
hình boosting và RF lớn hơn 1–2 bậc độ lớn.

### 4.10. Độ nhạy tham số giả định λ
{{table:lambda}}

{{fig:exp_lambda.png|Ảnh hưởng của λ}}

**Kết quả.**
- **Calibrated noisy-OR không hoàn toàn trung lập.** AUC giảm từ {{num:lambda_auc_0}} (λ = 0) xuống
  {{num:lambda_auc_03}} (λ = 0,3) và {{num:lambda_auc_05}} (λ = 0,5).
  - Nguyên nhân: ở các ô có P_data < λπ, p0 phải bị cắt (cột "Ô p0 bị cắt").
  - Với λ = 0,3 đang dùng, chi phí này nhỏ. Nó tăng nhanh khi λ lớn hơn.
- **What-if ở λ = 0,3**, thay đổi điểm trung bình của người đang đi làm:
  - mất việc: {{num:whatif_job}} điểm;
  - biến cố sức khỏe: {{num:whatif_health}} điểm;
  - lạm phát cao và suy thoái: tác động rất nhỏ, vì chỉ đi qua chi phí sinh hoạt và rủi ro mất việc.

  Các mức này tăng theo λ (bảng trên). Vì vậy demo luôn ghi rõ "λ là giả định".

### 4.11. Độ trung thành của lời khuyên LLM
{{table:llm}}

- Lời khuyên template trung thành 100% theo bộ kiểm tra.
- Đối chứng âm (lời khuyên bị cố ý sửa số và đảo hướng) bị phát hiện 100%, nên bộ kiểm tra có tác dụng.
- LLM thật (Groq, gói miễn phí, chạy 24/11/2026, temperature 0.2, cùng prompt và 50 hồ sơ):
  - `qwen3.8-27b` trung thành {{num:llm_faithful.groq:qwen3.8-27b}}: không có số nào ngoài dữ kiện; có
    {{num:llm_n_wrong_dir.groq:qwen3.8-27b}} lời khuyên bị bộ kiểm tra đánh dấu sai hướng.
  - `gpt-oss-120b` (mô hình lớn hơn) chỉ trung thành {{num:llm_faithful.groq:gpt-oss-120b}}. Lý do chính:
    {{num:llm_n_bad_numbers.groq:gpt-oss-120b}}/50 lời khuyên có con số **tự tính** (ví dụ "còn thiếu … điểm để đạt
    mục tiêu", cộng gộp đóng góp của nhiều yếu tố), dù prompt đã cấm. Phép tính có thể đúng, nhưng vi phạm nguyên
    tắc "mọi con số do BN tính" và không kiểm chứng được tự động. Có trường hợp mô hình gọi `chi_phi` của kế hoạch là
    "%", trong khi đây là đơn vị nỗ lực tương đối.
  - Hệ quả thiết kế: mô hình lớn hơn không đồng nghĩa trung thành hơn. Cần bộ kiểm tra tự động đứng sau LLM, và dự
    phòng bằng template khi lời khuyên không đạt. Từ kết quả này, demo dùng `qwen3.8-27b` làm model Groq mặc định
    (`configs/llm.yaml`), còn `gpt-oss-120b` chỉ giữ để so sánh.
  - Hạn chế: bộ kiểm tra hướng là heuristic. Ngoài ra, sau khi đọc lỗi, nhóm sửa một lỗi bắt nhầm: số thứ tự
    "kế hoạch 2" không còn bị tính là số bịa. Sửa này áp dụng cho mọi nguồn lời khuyên; chấm tay của nhóm sẽ bổ sung
    đánh giá chất lượng.

### 4.12. Tổng hợp
| Tiêu chí | Tốt hơn | Ghi chú |
|---|---|---|
| Phân biệt (AUC) | ML (XGBoost, LightGBM) | BN-Expert-Mono kém {{num:gap_best_vs_bnmono}}; hơn FICO {{num:gap_bnmono_vs_fico}} |
| Hiệu chỉnh | ML ≈ BN-Expert-Mono | Naive Bayes và TAN kém |
| Thiếu thông tin ngẫu nhiên | **Họ Bayes** | XGBoost suy giảm mạnh nhất |
| Thiếu biến mạnh nhất | ML/TAN | Cấu trúc BN-Expert thưa |
| Dữ liệu ít | LR, Naive Bayes | BN-Expert cần nhiều dữ liệu; ràng buộc đơn điệu giúp đáng kể |
| Ngành mới | Hầu hết ngang nhau | BN-Expert thất bại với trạng thái cha chưa gặp ("không đi làm") |
| Nhất quán tri thức | **BN-Expert-Mono** (trong các mô hình học) | Có lưu ý về biến phẳng và thâm niên |
| Ổn định giải thích | NB, LR > **BN** > boosting | |
| Chi phí | **BN**, LR | |
| Suy luận ngược, what-if biến cố, giải thích nhân quả | **Chỉ BN** | Không có ở ML hộp đen (định tính) |

<!-- Khôi – thảo luận tổng hợp (≤ 1 trang): khi nào nên dùng BN, khi nào nên dùng ML; kết hợp (ví dụ ML để xếp
hạng, BN để tư vấn/what-if). -->

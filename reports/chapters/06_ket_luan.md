## 6. Kết luận, hạn chế và hướng phát triển

### 6.1. Kết luận
1. **Đáp ứng đề bài.**
   - Xây dựng được Mạng Bayes cho chuỗi `Ngành → Thu nhập → Biến cố → Khả năng vỡ nợ` trên 307.511 hồ sơ thật.
     Lớp tri thức được sinh từ số liệu chính thức của Việt Nam và quốc tế.
   - Suy luận xuôi ra điểm 300–850.
   - Suy luận ngược bằng ba công cụ: hậu nghiệm ngược, MAP, phản thực do() có chi phí.
   - LLM diễn giải có kiểm tra độ trung thành tự động.
   - Demo Streamlit có đồ thị nhân quả.
2. **So với ML hộp đen** (Chương 4). BN-Expert-Mono *không* thắng về phân biệt: kém XGBoost
   {{num:gap_best_vs_bnmono}} AUC, khác biệt có ý nghĩa thống kê. BN có lợi thế rõ ở:
   - chịu thiếu thông tin ngẫu nhiên;
   - nhất quán với tri thức chuyên gia;
   - ổn định giải thích (so với boosting);
   - chi phí;
   - các chức năng ML hộp đen không có: suy luận ngược, what-if biến cố, giải thích theo cấu trúc nhân quả.

   BN thua ở ba điểm: dữ liệu ít, ngoại suy sang trạng thái chưa gặp, và thiếu biến mạnh nhất.
3. **So với đề tài FICO rule-based cũ.** BN-Expert-Mono hơn {{num:gap_bnmono_vs_fico}} AUC và hiệu chỉnh tốt hơn.
   BN giữ được điểm mạnh của luật là tính nhất quán tri thức nhờ ràng buộc đơn điệu, đồng thời thêm ngành nghề, biến
   cố, xử lý thiếu thông tin và suy luận ngược.
4. **Bài học về tri thức.**
   - Dữ liệu tín dụng chứa quan hệ ngược tri thức do thiên lệch chọn mẫu: DSTI và thu nhập liên hệ yếu, không đơn
     điệu.
   - Mô hình học thuần (kể cả LR) hấp thụ các quan hệ này. Tri thức chuyên gia đưa vào cấu trúc và ràng buộc giúp
     chặn chúng mà không làm giảm độ chính xác (BN-Expert-Mono tốt hơn BN-Expert).
   - Lịch sử tín dụng chi phối rủi ro. Vì vậy lời khuyên thực tế nhất từ suy luận ngược thường là cải thiện lịch sử
     trả nợ và gắn bó công việc, hơn là chỉ tăng thu nhập hay giảm chi tiêu.

### 6.2. Hạn chế
- **Dữ liệu.**
  - Home Credit không phải dữ liệu Việt Nam, không công bố đơn vị tiền tệ, và ẩn danh một phần ngành.
  - Quy đổi VND sang ngũ phân vị trong demo là xấp xỉ (*giả định*).
- **Giả định của lớp tri thức.** Các hệ số noisy-OR, đệm tài sản, hệ số thâm niên, λ và chi phí đòn bẩy không có dữ
  liệu kiểm chứng. Calibrated noisy-OR làm AUC giảm nhẹ ({{num:lambda_auc_0}} → {{num:lambda_auc_03}}) do phải cắt
  p0.
- **CPT dạng bảng.** Nút Vỡ nợ nhiều cha nên cần nhiều dữ liệu và không ngoại suy được sang trạng thái chưa gặp. Ví
  dụ: nhóm "không đi làm" khi bị loại khỏi dữ liệu học.
- **Cấu trúc thưa.** Khi thiếu điểm tín dụng ngoài, BN kém ML vì các biến khác chỉ tác động gián tiếp.
- **Ràng buộc đơn điệu chưa đủ.** Chỉ áp cho DSTI và lịch sử tín dụng; thâm niên vẫn còn vi phạm. Một số biến không có
  tác động trong BN do d-separation (LTI, tra cứu tín dụng).
- **LLM.** Bộ kiểm tra hướng tác động là heuristic. Kết quả với LLM thật và chấm tay đang chờ API key.
- **Công bằng.** Không dùng giới tính hay hôn nhân, nhưng ngành, nghề và vùng có thể tương quan với thuộc tính nhạy
  cảm. Nhóm chưa đo các chỉ số công bằng.

### 6.3. Hướng phát triển
1. **CPT tham số hóa** (noisy-OR/noisy-MAX, logistic CPD) cho nút nhiều cha: giảm số tham số, ngoại suy tốt hơn, hợp
   với dữ liệu ít.
2. **Mở rộng ràng buộc đơn điệu** (thâm niên, thu nhập) và học cấu trúc có ràng buộc tri thức chặt hơn.
3. **Học tham số lớp tri thức (λ, noisy-OR)** từ dữ liệu có biến cố thật, ví dụ dữ liệu vay theo thời gian hoặc dữ
   liệu khảo sát hộ gia đình.
4. **Dữ liệu tín dụng Việt Nam và thu nhập theo ngành của GSO** để thay các xấp xỉ.
5. **Kết hợp:** ML để xếp hạng, BN để tư vấn, what-if và suy luận ngược. Kiểm tra nhất quán giữa hai mô hình.
6. **Đánh giá công bằng** (demographic parity, equalized odds) theo vùng, ngành, nhóm tuổi.

# 8. Thuật ngữ và câu hỏi hay gặp khi bảo vệ

## 8.1. Thuật ngữ Việt – Anh
| Tiếng Việt | Tiếng Anh | Giải thích ngắn |
|---|---|---|
| Mạng Bayes | Bayesian Network (BN) | DAG cùng các CPT |
| Đồ thị có hướng không chu trình | Directed Acyclic Graph (DAG) | |
| Bảng xác suất có điều kiện | Conditional Probability Table (CPT) | P(nút \| cha) |
| Suy luận xuôi / ngược | Predictive / diagnostic inference | Từ nguyên nhân → hệ quả / từ hệ quả → nguyên nhân |
| Lấy biên | Marginalization | Cộng xác suất trên các biến không biết |
| Khử biến | Variable elimination | Thuật giải suy luận chính xác |
| Hậu nghiệm cực đại | Maximum a posteriori (MAP) | Tổ hợp khả dĩ nhất |
| Can thiệp | Intervention, do-operator | P(Y \| do(X)) |
| Phản thực | Counterfactual | "Nếu thay đổi X thì sao?" |
| Phẫu thuật đồ thị | Graph surgery | Cắt cạnh đi vào nút bị can thiệp |
| Noisy-OR | Noisy-OR | Mô hình nhiều nguyên nhân độc lập |
| Hồi quy đơn điệu | Isotonic regression | Dãy đơn điệu gần dữ liệu nhất |
| Xác suất vỡ nợ | Probability of default (PD) | |
| Trả nợ / thu nhập | Debt service to income (DSTI) | `annuity_to_income` |
| Dư nợ / thu nhập | Loan to income (LTI) | `credit_to_income` |
| Thiên lệch chọn mẫu | Selection bias, reject inference | Dữ liệu chỉ có người đã được duyệt vay |
| Hiệu chỉnh xác suất | Calibration | Xác suất dự báo khớp tần suất thật |
| Sai số hiệu chỉnh kỳ vọng | Expected Calibration Error (ECE) | |
| Dự báo ngoài fold | Out-of-fold (OOF) | Dự báo từ mô hình chưa thấy hồ sơ đó |
| Kiểm định chéo phân tầng | Stratified k-fold CV | |
| Đường phụ thuộc từng cá thể | Individual Conditional Expectation (ICE) | Thay một biến, xem dự báo của một hồ sơ |
| Đường phụ thuộc riêng phần | Partial Dependence Plot (PDP) | Trung bình các ICE |
| Ảo giác (LLM) | Hallucination | LLM bịa thông tin |
| Độ trung thành | Faithfulness | Lời khuyên khớp dữ kiện |

## 8.2. Câu hỏi hội đồng có thể hỏi và hướng trả lời
Khi trả lời, dẫn số từ `reports/results_summary.md`. Không dẫn từ trí nhớ.

**1. ML (XGBoost) có AUC cao hơn, vậy dùng BN làm gì?**
Đề bài không chỉ cần dự báo. Đề cần (a) suy luận ngược ra điều kiện cần, (b) what-if biến cố không có trong dữ liệu,
(c) giải thích theo nhân quả, (d) LLM diễn giải từ CPT. ML hộp đen không làm được (a), (b), (d) một cách tự nhiên.
Về định lượng, xem thí nghiệm 4 (thiếu thông tin), 7 (nhất quán tri thức), 8 (ổn định giải thích): đây là các tiêu
chí quan trọng khi tư vấn cho người dùng. Nhóm báo cáo trung thực khoảng cách AUC.

**2. λ = 0,3 lấy ở đâu?**
Đây là giả định, vì không có dữ liệu về "hụt dòng tiền". Nhờ calibrated noisy-OR, khi không có bằng chứng biến cố thì
dự báo **gần như không phụ thuộc** λ. Bảng độ nhạy λ cho thấy AUC chỉ giảm nhẹ, do một số ô phải cắt p0;
mức giảm tăng khi λ lớn, và nhóm báo cáo trung thực điều này. λ chỉ quyết định độ mạnh của what-if, và
bảng độ nhạy cho thấy what-if thay đổi theo λ ra sao.

**3. Dữ liệu Home Credit không phải của Việt Nam, sao dùng tri thức vĩ mô Việt Nam?**
Phần học từ dữ liệu (lớp dữ liệu) chỉ dùng Home Credit. Tri thức Việt Nam chỉ nằm ở lớp what-if và ở bước quy đổi
VND trong demo, và đều được ghi là xấp xỉ. Hướng phát triển là học lại khi có dữ liệu tín dụng Việt Nam.

**4. Vì sao thu nhập, DSTI ảnh hưởng yếu? Có mâu thuẫn tri thức không?**
Có, đây là thiên lệch chọn mẫu: ngân hàng chỉ duyệt DSTI cao cho người an toàn. Vì vậy BN-Expert-Mono áp ràng
buộc đơn điệu. Ràng buộc đổi lại một chút độ khớp dữ liệu để có lời khuyên đúng tri thức; xem so sánh BN-Expert với
BN-Expert-Mono ở Bảng 1 và Bảng 6.

**5. LLM có bịa số không? Kiểm soát thế nào?**
- LLM không tính gì; mọi số đến từ BN.
- Có kiểm tra tự động (số, bao phủ, hướng), cộng đối chứng âm để chứng minh bộ kiểm tra bắt được lỗi, cộng chấm tay.
- Lời khuyên vi phạm thì demo gắn nhãn ⚠️.

**6. Cấu trúc DAG do ai quyết định? Có kiểm chứng không?**
Nhóm thiết kế, mỗi cạnh có lý do (`configs/bn_expert.yaml`). Mức ủng hộ của dữ liệu cho từng cạnh được đo bằng
Cramér's V (`reports/eda/bn_expert_edge_support.md`). Nhóm cũng so với cấu trúc máy học (BN-Learned, BN-Hybrid):
cấu trúc máy học có cạnh ngược nhân quả, ví dụ thu nhập → ngành.

**7. Suy luận ngược "điều kiện cần" nghĩa là gì chính xác?**
Có hai nghĩa:
- *Xác suất*: trong những người giống bạn mà đạt mục tiêu, mức nào phổ biến hơn (lift).
- *Can thiệp*: thay đổi rẻ nhất để mô hình dự báo đạt mục tiêu, tính bằng do() để không nhầm tương quan với nhân
  quả.

Cả hai đều là "theo mô hình", không phải cam kết.

**8. Có rò rỉ dữ liệu không?**
Không. Ngưỡng rời rạc hóa, CPT, chuẩn hóa, early stopping và tinh chỉnh đều chỉ dùng train của fold. Split được cố
định và lưu lại.

**9. Bộ suy luận tự viết có đúng không?**
Có test đối chiếu với pgmpy tới 1e-8, trên mạng ngẫu nhiên và trên BN-Expert thật, kể cả thiếu bằng chứng và truy
vấn ngược chiều.

**10. Khác đề tài FICO cũ ở đâu?**
Xem bảng khác biệt ở Chương 1 của báo cáo và tab "Tri thức & CPT" của demo. Ý chính: luật cố định → xác suất học từ
dữ liệu + tri thức; có ngành nghề, biến cố, thiếu thông tin, suy luận ngược và kiểm chứng thực nghiệm.

**11. Vì sao BN-Expert kém trên German Credit?**
Nút vỡ nợ có nhiều cha nên CPT có hàng trăm ô, trong khi chỉ có ~800 hồ sơ học. Đây là giới hạn đã biết của CPT dạng
bảng. Naive Bayes ít tham số hơn nên làm tốt hơn. Hướng cải tiến là CPT tham số hóa, ví dụ noisy-OR hoặc logistic.

**12. Có dùng thuộc tính nhạy cảm không?**
Không dùng giới tính hay hôn nhân. Ngành, nghề và vùng có thể tương quan với thuộc tính nhạy cảm; đây là hạn chế
được nêu ở phần kết luận.

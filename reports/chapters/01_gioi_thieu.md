## 1. Giới thiệu

### 1.1. Bài toán
Đánh giá khả năng tài chính cá nhân (rủi ro vỡ nợ) không chỉ phụ thuộc vào các con số hiện tại của người vay mà
còn vào **bối cảnh nghề nghiệp** – ngành nghề quyết định mức và độ ổn định thu nhập – và vào **biến cố** có thể
xảy ra (mất việc, chi phí y tế, lạm phát). Đề tài mô hình hóa chuỗi nhân quả

`Ngành → Thu nhập → Biến cố → Khả năng vỡ nợ`

bằng **Mạng Bayes (BN)** để: (i) suy luận xuôi – dự báo xác suất vỡ nợ và quy đổi sang điểm 300–850;
(ii) suy luận ngược – từ một mục tiêu (điểm tín dụng, sở hữu tài sản) suy ra điều kiện cần về thu nhập/chi tiêu;
(iii) dùng LLM diễn giải kết quả thành lời khuyên tiếng Việt; (iv) kiểm chứng thực nghiệm độ đúng và độ tin cậy
của BN so với các mô hình học máy "hộp đen".

### 1.2. Dữ liệu
- **Home Credit Default Risk** (`application_train.csv`, 307.511 hồ sơ, tỷ lệ vỡ nợ 8,07%) – dữ liệu chính, có
  ngành (58 loại tổ chức), nghề, thu nhập, khoản vay, thâm niên, điểm tín dụng ngoài.
- **German Credit** (1.000 hồ sơ) – bộ phụ cho thí nghiệm dữ liệu ít.
- **Tri thức vĩ mô Việt Nam**: World Bank (lạm phát, thất nghiệp, tăng trưởng GDP), WHO (chi y tế thảm họa theo
  tuổi), GSO – Khảo sát mức sống dân cư 2024 (thu nhập, chi tiêu theo ngũ phân vị).

### 1.3. Khác biệt so với đề tài trước (FICO rule-based)
Đề tài trước xây hệ thống chấm điểm giả lập theo luật FICO cơ bản (5 nhóm yếu tố với trọng số cố định). Nhóm
không còn mã nguồn cũ nên đã **tái hiện tối giản** hệ luật này (`configs/fico.yaml`, `src/baselines/fico.py`)
làm mốc so sánh trực tiếp.

| Khía cạnh | FICO rule-based (đề tài cũ) | Mạng Bayes (đề tài này) |
|---|---|---|
| Biểu diễn tri thức | Luật + trọng số cố định 35/30/15/10/10 | Đồ thị nhân quả 20 nút, 35 cạnh có lý do; CPT học từ dữ liệu + tri thức vĩ mô |
| Đầu ra | Điểm tất định | Xác suất vỡ nợ (có độ bất định) → điểm 300–850 |
| Ngành nghề | Không dùng | Ngành → Nghề → Thu nhập, Ổn định việc làm, Rủi ro mất việc |
| Biến cố | Không mô hình hóa | Nút tri thức: mất việc, sức khỏe, lạm phát, chu kỳ kinh tế, chi phí sinh hoạt → hụt dòng tiền |
| Thiếu thông tin | Gán điểm trung tính | Lấy biên chính xác theo xác suất (không cần điền giá trị) |
| Suy luận ngược | Không | Hậu nghiệm ngược, MAP, phản thực do() có chi phí |
| Học từ dữ liệu | Không (chỉ hiệu chỉnh Platt để so sánh) | Có (CPT m-estimate; ràng buộc đơn điệu chuyên gia) |
| Giải thích | Điểm thành phần | Đóng góp từng yếu tố (suy luận chính xác) + đồ thị nhân quả + LLM |
| Kiểm chứng | Không có | 9 thí nghiệm so với 8 mô hình ML và 4 biến thể Bayes |

Kết quả so sánh định lượng với FICO nằm ở Chương 4 (BN-Expert-Mono hơn FICO {{num:gap_bnmono_vs_fico}} AUC).

### 1.4. Đóng góp
1. BN-Expert hai lớp: lớp dữ liệu (CPT học) + lớp tri thức (CPT sinh tự động từ nguồn có trích dẫn), nối bằng
   **calibrated noisy-OR** để lớp tri thức phục vụ what-if mà gần như không làm sai phần đã học từ dữ liệu (xem độ nhạy λ, mục 4.10).
2. Biến thể **BN-Expert-Mono** chiếu CPT lên ràng buộc đơn điệu chuyên gia (isotonic/POCS) – không bao giờ cho
   lời khuyên ngược tri thức ở các biến được ràng buộc.
3. Bộ suy luận chính xác theo lô (khớp pgmpy tới 1e-8), đủ nhanh cho hàng triệu truy vấn trong thực nghiệm.
4. Suy luận ngược bằng phản thực do() có chi phí trên 7 đòn bẩy người dùng điều khiển được.
5. Báo cáo thực nghiệm trung thực trên 9 tiêu chí (phân biệt, hiệu chỉnh, kiểm định, thiếu thông tin, dữ liệu ít,
   dịch chuyển theo ngành, nhất quán tri thức, ổn định giải thích, chi phí).

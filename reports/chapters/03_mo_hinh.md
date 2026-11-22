## 3. Mô hình Mạng Bayes và thuật giải suy luận

### 3.1. Biến và rời rạc hóa
Mười ba biến đầu vào được tạo từ Home Credit (`src/data/home_credit.py`) và rời rạc hóa theo
`configs/discretize.yaml`:
- **Ngưỡng nghiệp vụ cố định**: tuổi (30/40/50/60), thâm niên (1/3/7 năm; *không đi làm* là một trạng thái riêng),
  DSTI = trả góp/thu nhập (10/20/30/40%), LTI = dư nợ/thu nhập năm (1,5/3/4,5/7 lần), số con, số lần tra cứu.
- **Ngũ phân vị**: thu nhập và điểm tín dụng ngoài (đơn vị không được công bố). Ngưỡng **được học lại trên tập
  train của từng fold** để không rò rỉ thông tin.
- **Nhóm theo chuẩn**: ngành (10 nhóm ISIC Rev.4), nghề (5 nhóm ISCO-08), học vấn (3 mức), vùng (1–3).
- Không dùng thuộc tính nhạy cảm (giới tính, hôn nhân).

### 3.2. Cấu trúc BN-Expert (hai lớp)
{{fig:bn_expert_dag.png|DAG BN-Expert (nhóm duyệt 22/11/2026)}}

- **Lớp dữ liệu** (14 nút): mỗi cạnh có lý do và bằng chứng (`configs/bn_expert.yaml`). Nút `default` có 5 cha
  dữ liệu: lịch sử tín dụng, thâm niên, nhóm nghề, DSTI, vùng.
- **Lớp tri thức** (6 nút): Lạm phát, Chu kỳ kinh tế, Mất việc, Biến cố sức khỏe, Chi phí sinh hoạt, Hụt dòng
  tiền. Các nút này không có trong dữ liệu; CPT được **sinh tự động** từ `knowledge_base/` (`src/bn/expert_cpt.py`):
  - P(lạm phát) và P(suy giảm) là tần suất năm của Việt Nam 2000–2024.
  - P(mất việc) = tỷ lệ thất nghiệp nền × hệ số chu kỳ × hệ số ngành × hệ số thâm niên × kỳ hạn.
  - P(biến cố sức khỏe | tuổi) lấy theo WHO.
  - Hụt dòng tiền là noisy-OR có leak, nhân với hệ số đệm theo thu nhập (GSO) và theo tài sản.

  Các hệ số không có nguồn được ghi rõ là **giả định** (Chương 2).

### 3.3. Học tham số
CPT của nút dữ liệu được ước lượng bằng **m-estimate** với prior là phân phối biên:
θ_ijk = (N_ijk + m·P(k)) / (N_ij + m), m = 10.
- m được chọn trên một tập validation tách ra **từ train**.
- Lý do bỏ BDeu: BDeu chuẩn gán P(vỡ nợ) = 0,5 cho tổ hợp cha chưa gặp, trong khi tỷ lệ nền chỉ là 8%. m-estimate
  lùi về tỷ lệ nền.

### 3.4. Nối lớp tri thức vào nút đích: calibrated noisy-OR
Gọi P_data(D | pa) là CPT học từ dữ liệu và π = P(hụt dòng tiền) tiên nghiệm của quần thể. Khi đó:

- P(D=1 | pa, shock=no) = p0
- P(D=1 | pa, shock=yes) = 1 − (1 − p0)(1 − λ)
- p0 = (P_data − λπ) / (1 − λπ)

Cách nối này cho **đúng** P_data khi không có bằng chứng về biến cố, trừ các ô có P_data < λπ, nơi p0 phải bị cắt
ở 1e-4. Vì vậy lớp tri thức gần như không làm thay đổi độ chính xác đã học (AUC {{num:lambda_auc_0}} khi λ = 0 so
với {{num:lambda_auc_03}} khi λ = 0,3), và chủ yếu hoạt động trong các phân tích what-if. λ = 0,3 là **giả định**;
độ nhạy theo λ được phân tích ở mục 4.10.

### 3.5. BN-Expert-Mono: ràng buộc đơn điệu chuyên gia
Theo tri thức chuyên gia, DSTI tăng thì rủi ro không được giảm, và lịch sử tín dụng tốt hơn thì rủi ro không được
tăng. Dữ liệu lại cho thấy DSTI có liên hệ yếu và không đơn điệu với vỡ nợ (nhiều khả năng do thiên lệch chọn mẫu:
ngân hàng chỉ duyệt DSTI cao cho người an toàn).
- **Cách làm:** chiếu P_data(D=1 | pa) lên giao của các ràng buộc đơn điệu. Mỗi bước là một isotonic regression có
  trọng số theo số mẫu N_ij, lặp luân phiên (POCS). Sau đó một bước đóng cummax/cummin bảo đảm thỏa *chính xác*
  mọi ràng buộc (có kiểm tra bằng test).
- **Vì sao chọn làm mô hình chính:** đây là mô hình chính của demo, vì nó không bao giờ khuyên "tăng nợ để giảm
  rủi ro".

### 3.6. Suy luận xuôi chính xác theo lô
- **Thuật giải:** các truy vấn P(D | bằng chứng) được gom theo *mẫu biến quan sát*. Với mỗi mẫu, bộ suy luận
  bỏ các nút cằn (barren) không liên quan. Lát CPT của biến quan sát được lấy theo từng dòng (gather), còn biến ẩn
  được cộng bằng `numpy.einsum` với thứ tự khử tham lam. Thuật giải này là suy luận chính xác (tương đương
  variable elimination), không phải xấp xỉ.
- **Kiểm chứng:** kết quả khớp `pgmpy.VariableElimination` tới 1e-8 (`tests/test_bn.py`). Tốc độ đạt khoảng
  61.000 hồ sơ trong 0,2 giây, đủ cho các thí nghiệm thiếu thông tin và ICE.
- **Bằng chứng bất khả:** khi bằng chứng không thể xảy ra (ví dụ "mất việc" với người không đi làm), P(e) = 0 nên
  kết quả trả về NaN tường minh. Demo chặn trường hợp này.

### 3.7. Quy đổi điểm 300–850
Điểm = A + B·ln((1 − p)/p), cắt về đoạn [300, 850]. Hai điểm neo là p = 50% → 400 điểm và p = 0,5% → 800 điểm,
tức B = 400/ln 199 ≈ 75,6 (≈ 52 điểm mỗi lần odds tốt gấp đôi). Các mức rủi ro: ≥ 740 Rất tốt; ≥ 670 Tốt;
≥ 580 Trung bình; ≥ 500 Kém; còn lại Rất kém.

### 3.8. Suy luận ngược
1. **Hậu nghiệm ngược.** So sánh P(đòn bẩy | hồ sơ) với P(đòn bẩy | hồ sơ, mục tiêu đạt), trong đó mục tiêu
   là không vỡ nợ hoặc sở hữu nhà/xe. Hệ số nâng (lift) cho biết mức nào là *điều kiện cần* thường gặp ở những
   người đạt mục tiêu.
2. **MAP.** argmax của tổ hợp đòn bẩy, tính bằng pgmpy.
3. **Phản thực do() có chi phí.**
   - Đòn bẩy gồm 7 yếu tố người dùng điều khiển được: thu nhập ↑, DSTI ↓, LTI ↓, chi phí sinh hoạt ↓, tra cứu
     tín dụng ↓, và 2 đòn bẩy dài hạn là lịch sử tín dụng ↑ và thâm niên ↑.
   - Mỗi thay đổi là một can thiệp do(): cắt các cạnh đi vào nút (graph surgery), để không suy diễn ngược sai
     chiều nhân quả.
   - Thuật toán duyệt toàn bộ lưới tổ hợp (vài nghìn tổ hợp, suy luận theo lô) và trả về các kế hoạch không bị
     trội (chi phí thấp nhất, P(vỡ nợ) thấp nhất) đạt điểm mục tiêu.
   - Chi phí mỗi bậc là **giả định** (`configs/backward.yaml`).
   - Phát hiện trung thực: chỉ thay đổi thu nhập và chi tiêu thường không đủ để tăng nhiều điểm. Lịch sử tín dụng
     chi phối, nên các đòn bẩy dài hạn được bổ sung.

### 3.9. Các mô hình so sánh
| Họ | Mô hình | Ghi chú |
|---|---|---|
| Luật | FICO | Tái hiện đề tài cũ; chỉ hiệu chỉnh Platt (điểm → xác suất) |
| Bayes | BN-Expert, BN-Expert-Mono | Mô hình đề xuất |
| Bayes | Naive Bayes, TAN, BN-Learned (Hill-Climb + BIC), BN-Hybrid (Hill-Climb + cạnh bắt buộc + thứ tự tầng) | Cùng nút và cùng ước lượng tham số; chỉ khác cấu trúc |
| ML hộp đen | LR, XGBoost, LightGBM, RF, MLP trên đặc trưng liên tục; LR-disc, XGBoost-disc trên đúng trạng thái BN; XGBoost-Mono có cùng ràng buộc đơn điệu với BN-Expert-Mono | Cùng 13 nhóm biến (công bằng thông tin); XGBoost tinh chỉnh bằng Optuna (25 trial, chỉ trên train) |

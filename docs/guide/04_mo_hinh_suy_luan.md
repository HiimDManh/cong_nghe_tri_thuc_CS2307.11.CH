# 4. Mô hình và suy luận

Code: `src/bn/core.py`, `model.py`, `expert_cpt.py`, `backward.py`, `variants.py`. Cấu trúc nằm ở
`configs/bn_expert.yaml` (20 nút, 35 cạnh, mỗi cạnh có lý do và bằng chứng). Hình DAG:
`reports/figures/bn_expert_dag.png`.

## 4.1. Hai lớp của BN-Expert
- **Lớp dữ liệu (14 nút)** gồm 13 biến đầu vào và nút Vỡ nợ. CPT học từ Home Credit.
  - Chuỗi chính của đề: Ngành → Nhóm nghề → Thu nhập; Ngành → Ổn định việc làm; Thu nhập → Tài sản, DSTI, LTI;
    Tuổi → Thâm niên, Số con, Lịch sử tín dụng…
  - Nút **Vỡ nợ** có 5 cha dữ liệu: Lịch sử tín dụng, Ổn định việc làm, Nhóm nghề, DSTI, Vùng. Đây là những biến có
    liên hệ trực tiếp mạnh trong EDA.
  - LTI là **nút chỉ báo** (lá): nó không gây ra vỡ nợ, nhưng khi quan sát được thì giúp suy ngược về DSTI và thu
    nhập.
- **Lớp tri thức (6 nút)**: Lạm phát, Chu kỳ kinh tế, Mất việc, Biến cố sức khỏe, Chi phí sinh hoạt, Hụt dòng tiền.
  - Chuỗi: (Chu kỳ, Ngành, Thâm niên) → Mất việc; Tuổi → Sức khỏe; (Lạm phát, Số con) → Chi phí sinh hoạt;
    (Mất việc, Sức khỏe, Chi phí, Thu nhập, Tài sản) → **Hụt dòng tiền → Vỡ nợ**.
  - Đây chính là phần "Biến cố" trong chuỗi `Ngành → Thu nhập → Biến cố → Vỡ nợ` của đề.

## 4.2. Học tham số
- Nút dữ liệu: m-estimate với m = 10 (xem 2.4). Gọi `DiscreteBN.fit_node`.
- Nút tri thức: CPT sinh từ `expert_cpt.build` (xem 3.6).
- Nút Vỡ nợ: CPT được nối theo mục 4.3.

## 4.3. Calibrated noisy-OR – nối lớp tri thức mà (gần như) không làm sai dữ liệu
**Vấn đề.** Dữ liệu không có cột "hụt dòng tiền". Nếu ghép tùy tiện nút này vào Vỡ nợ, xác suất dự báo sẽ lệch
khỏi những gì dữ liệu cho thấy.

**Lời giải.**
1. Học P_data(D=1 | cha dữ liệu) như bình thường.
2. Tính π = P(hụt dòng tiền = có) tiên nghiệm của quần thể bằng suy luận trên lớp tri thức.
3. Đặt
   - P(D=1 | cha, shock = không) = p0
   - P(D=1 | cha, shock = có) = 1 − (1 − p0)(1 − λ)

   và chọn p0 sao cho **trung bình theo π bằng đúng P_data**: p0 + (1 − p0)·λ·π = P_data, suy ra
   p0 = (P_data − λπ)/(1 − λπ). Nếu P_data < λπ thì p0 được cắt ở 1e-4. Số ô bị cắt được báo cáo trong
   `n_p0_clipped`.

**Ví dụ minh họa.** λ = 0,3, π = 0,062, P_data = 8%:
- λπ = 0,0186 nên p0 = (0,08 − 0,0186)/(1 − 0,0186) ≈ 6,26%.
- Kiểm tra: 0,0626 + 0,9374·0,0186 ≈ 8,0%. ✓
- Khi bật "hụt dòng tiền = có": 1 − 0,9374·0,7 ≈ 34,4%.

**Ý nghĩa.** Không có bằng chứng biến cố thì mô hình cho **đúng** xác suất học từ dữ liệu, *trừ các ô bị cắt p0*
(ô có P_data < λπ). Thí nghiệm độ nhạy cho thấy AUC giảm nhẹ vì lý do này, và mức giảm tăng theo λ. Có bằng chứng (what-if)
thì rủi ro tăng theo λ. λ = 0 thì lớp tri thức không có tác dụng; điều này được kiểm chứng bằng test
`test_lambda_zero_recovers_data_cpt`.

## 4.4. BN-Expert-Mono – ràng buộc đơn điệu
**Ràng buộc** (`MONOTONE_CONSTRAINTS` trong `model.py`):
- DSTI tăng thì P(vỡ nợ) không giảm.
- Lịch sử tín dụng tốt hơn thì P(vỡ nợ) không tăng.

Ràng buộc áp dụng cho từng tổ hợp của các cha còn lại.

**Thuật toán** (`isotonic_project`):
1. Lần lượt theo từng trục ràng buộc, chạy isotonic regression có trọng số N_ij (số mẫu của ô). Ô nhiều dữ liệu
   gần như giữ nguyên, ô ít dữ liệu bị kéo theo ràng buộc.
2. Lặp luân phiên (POCS) tối đa 30 vòng.
3. Bước đóng cummax/cummin bảo đảm thỏa **chính xác**. Code có assert vi phạm ≤ 1e-12, và test
   `test_monotone_variant_respects_constraints` kiểm tra lại.

**Vì sao cần.**
- Do thiên lệch chọn mẫu, CPT học thuần có thể cho "DSTI 30–40% an toàn hơn 20–30%". Lời khuyên "vay thêm cho an
  toàn" là sai.
- Mono loại bỏ điều này, nên được chọn làm mô hình chính của demo.
- So sánh công bằng: phía ML cũng có **XGBoost-Mono** với đúng hai ràng buộc này.

## 4.5. Suy luận xuôi chính xác theo lô (`DiscreteBN.query`)
- **Mục tiêu:** tính P(Vỡ nợ | bằng chứng) cho hàng chục nghìn hồ sơ, mỗi hồ sơ có thể thiếu một tập biến khác
  nhau. pgmpy chạy từng hồ sơ một nên quá chậm cho các thí nghiệm.
- **Thuật giải:**
  1. Gom hồ sơ theo **mẫu biến quan sát**: các hồ sơ thiếu cùng tập biến nằm chung một nhóm.
  2. Với mỗi nhóm, bỏ các nút **cằn** (barren). Đó là các nút không quan sát và không có hậu duệ nào được quan sát.
     Tổng CPT của chúng bằng 1 nên bỏ đi không đổi kết quả.
  3. Biến **quan sát**: lấy đúng lát CPT theo giá trị của từng hồ sơ (gather). Ta được một mảng có trục "hồ sơ".
  4. Biến **ẩn**: nhân và cộng bằng `numpy.einsum`, với thứ tự khử được chọn tham lam (`einsum_path`). Đây chính là
     variable elimination, viết dưới dạng tensor.
  5. Chuẩn hóa theo P(bằng chứng). Nếu P(bằng chứng) = 0, ví dụ "mất việc" khi đang "không đi làm", kết quả trả về
     NaN tường minh và demo chặn trường hợp này.
- **Kiểm chứng:** khớp `pgmpy.VariableElimination` tới 1e-8, kể cả khi thiếu bằng chứng và khi truy vấn ngược
  chiều cạnh (`tests/test_bn.py`).
- **Tốc độ:** khoảng 61.000 hồ sơ trong 0,2 giây khi đủ thông tin.

## 4.6. Điểm 300–850 và mức rủi ro
- Công thức: điểm = A + B·ln((1−p)/p), cắt về [300, 850]. Neo: p = 50% → 400, p = 0,5% → 800 (`configs/bn_expert_cpt.yaml`).
- Mức rủi ro:

  | Điểm | Mức |
  |---|---|
  | ≥ 740 | Rất tốt |
  | 670–739 | Tốt |
  | 580–669 | Trung bình |
  | 500–579 | Kém |
  | < 500 | Rất kém |

- Điểm là hàm **đơn điệu giảm** theo p, nên mọi so sánh thứ hạng (AUC) theo điểm và theo xác suất là như nhau.

## 4.7. Giải thích "đóng góp từng yếu tố" (demo, LLM, thí nghiệm 8)
**Định nghĩa.** Đóng góp của yếu tố g = điểm(hồ sơ) − Σ_s P(g = s)·điểm(hồ sơ với g = s), trong đó P(g = s) là
phân phối của quần thể. Nói cách khác, ta so với một người **giống hệt mọi mặt** nhưng yếu tố g ở mức phổ biến.
Mọi đại lượng được tính chính xác bằng BN, không lấy mẫu.

**Vì sao không dùng cách "bỏ bằng chứng"** (so với P(hồ sơ khi không biết g)):
- Cách này đúng về xác suất, nhưng so với kỳ vọng *có điều kiện*.
- Ví dụ: người trẻ, hỏi vay nhiều lần thường có lịch sử "rất kém". Khi đó lịch sử "kém" lại bị tính là "giúp tăng
  điểm". Điều này khó hiểu với người dùng, nên nhóm đã đổi cách.
- Hàm cũ vẫn giữ (`occlusion`) để đối chiếu.

**Mô hình ML.** Dùng TreeSHAP (XGBoost, LightGBM) hoặc SHAP tuyến tính (LR), cộng các cột one-hot về đúng nhóm biến.

## 4.8. Suy luận ngược (`src/bn/backward.py`)
Có ba công cụ, trả lời ba câu hỏi khác nhau:
1. **Hậu nghiệm ngược** (`backward_posterior`): "Trong những người giống tôi, ai đạt mục tiêu thì thường có mức
   thu nhập / DSTI / chi tiêu nào?"
   - So sánh P(đòn bẩy | hồ sơ) với P(đòn bẩy | hồ sơ, mục tiêu). Mục tiêu có thể là không vỡ nợ, có nhà, hoặc có
     nhà và xe.
   - Lift > 1 nghĩa là mức đó phổ biến hơn ở nhóm đạt mục tiêu, tức là "điều kiện cần" theo nghĩa xác suất.
2. **MAP** (`map_conditions`, pgmpy): tổ hợp đòn bẩy khả dĩ nhất khi biết mục tiêu đã đạt.
3. **Phản thực do() có chi phí** (`counterfactual_search`): "Tôi phải thay đổi gì, ít tốn kém nhất, để đạt X điểm?"
   - 7 đòn bẩy (`configs/backward.yaml`), mỗi đòn bẩy có hướng, số bậc tối đa và chi phí/bậc. Chi phí là **giả
     định**, thể hiện độ khó.

     | Đòn bẩy | Hướng | Số bậc tối đa | Chi phí/bậc |
     |---|---|---|---|
     | Thu nhập | ↑ | 2 | 3 |
     | DSTI | ↓ | 3 | 1 |
     | LTI | ↓ | 3 | 1 |
     | Chi phí sinh hoạt | ↓ | 2 | 1,5 |
     | Tra cứu tín dụng | ↓ | 3 | 0,5 |
     | Lịch sử tín dụng (dài hạn) | ↑ | 2 | 4 |
     | Thâm niên (dài hạn) | ↑ | 1 | 4 |

   - Mỗi tổ hợp thay đổi là một can thiệp: cắt các cạnh đi vào nút bị thay đổi (`intervene`), rồi suy luận. Ví dụ
     "tăng thu nhập" không được làm thay đổi ngược niềm tin về ngành.
   - Thuật toán duyệt **toàn bộ** lưới (vài nghìn tổ hợp, suy luận theo lô), giữ các kế hoạch đạt mục tiêu và không
     bị trội (không có kế hoạch nào vừa rẻ hơn vừa tốt hơn), rồi sắp theo chi phí.
   - Nếu không có kế hoạch nào đạt mục tiêu, trả về "tốt nhất có thể". Đây là một phát hiện trung thực: chỉ thu nhập
     và chi tiêu thường không đủ, vì lịch sử tín dụng chi phối điểm.

## 4.9. Các biến thể Bayes (`src/bn/variants.py`)
- Tất cả dùng cùng các nút dữ liệu và cùng m-estimate. **Chỉ khác cấu trúc**, nên khác biệt về kết quả đến từ cấu
  trúc.
- Các biến thể: Naive Bayes, TAN, BN-Learned (Hill-Climb + BIC, không ràng buộc), BN-Hybrid (Hill-Climb + cạnh
  chuyên gia bắt buộc + thứ tự tầng `TIERS`).
- Học cấu trúc dùng mẫu con (TAN tối đa 100k dòng, Hill-Climb tối đa 60k dòng) để giữ thời gian chạy. Điều này đã
  ghi rõ.

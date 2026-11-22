# 2. Kiến thức nền

Các ví dụ số trong tài liệu này là **ví dụ minh họa tự đặt** để giải thích công thức, không phải kết quả của dự án.

## 2.1. Tín dụng và chấm điểm tín dụng

**Vỡ nợ (default).** Người vay không trả được nợ theo cam kết.
- Trong Home Credit, `TARGET = 1` nghĩa là khách hàng "gặp khó khăn thanh toán": trễ hạn quá một số ngày ở ít nhất
  một kỳ trong các kỳ trả đầu tiên (định nghĩa của cuộc thi).
- Tỷ lệ vỡ nợ trong dữ liệu là 8,07%.

**Xác suất vỡ nợ (PD – probability of default).** Đây là đầu ra chính của mô hình. Ngân hàng dùng PD để duyệt
vay, định giá lãi suất và trích lập dự phòng.

**Thẻ điểm (scorecard), điểm tín dụng.** PD được quy đổi sang thang điểm cho dễ hiểu. Cách quy đổi chuẩn ngành là
**tuyến tính theo log-odds**: điểm = A + B·ln((1−p)/p).
- **PDO (points to double the odds)**: số điểm tăng thêm khi odds "tốt/xấu" gấp đôi. Dự án dùng PDO ≈ 52.
- Hai điểm neo: p = 50% → 400 điểm, p = 0,5% → 800 điểm. Từ đó B = 400/ln 199 ≈ 75,6.
- Ví dụ: p = 8% → 400 + 75,6·ln(0,92/0,08) ≈ 585 điểm.

**FICO.** Điểm tín dụng phổ biến ở Mỹ (300–850). Theo công bố của myFICO, điểm gồm 5 nhóm yếu tố:

| Nhóm yếu tố | Trọng số |
|---|---|
| Lịch sử thanh toán | 35% |
| Dư nợ | 30% |
| Độ dài lịch sử | 15% |
| Tín dụng mới | 10% |
| Cơ cấu tín dụng | 10% |

Đề tài cũ của nhóm là hệ **luật** theo các trọng số này. Trọng số cố định, không học từ dữ liệu.

**Các tỷ số gánh nặng nợ.**
- **DSTI** (debt service to income) = tiền trả nợ hằng tháng / thu nhập. Trong code là `annuity_to_income`.
  Nhiều nước đặt trần DSTI: Pháp 35%, Estonia 50%.
- **LTI** (loan to income) = dư nợ / thu nhập năm. Trong code là `credit_to_income`. Anh giới hạn tỷ lệ khoản vay
  mua nhà có LTI ≥ 4,5.

**Thiên lệch chọn mẫu (selection bias / reject inference).** Dữ liệu chỉ gồm người **đã được duyệt vay**. Ngân
hàng chỉ cho vay DSTI cao với người họ đánh giá an toàn. Vì vậy, trong dữ liệu, DSTI cao *không* đi kèm rủi ro cao
một cách rõ ràng, dù theo tri thức thì DSTI cao phải rủi ro hơn. Đây là lý do dự án cần ràng buộc đơn điệu
(mục 4.4).

**Hiệu chỉnh (calibration).** Mô hình được gọi là hiệu chỉnh tốt nếu, trong số những người được dự báo 10%, đúng
khoảng 10% vỡ nợ thật. Điều này quan trọng vì ngân hàng dùng **chính con số xác suất**, không chỉ dùng thứ hạng.

## 2.2. Xác suất cần nhớ
| Khái niệm | Công thức / ý nghĩa |
|---|---|
| Xác suất có điều kiện | P(A \| B) = P(A, B) / P(B) |
| Quy tắc nhân | P(A, B) = P(A \| B)·P(B) |
| Xác suất toàn phần (lấy biên) | P(A) = Σ_b P(A \| B=b)·P(B=b) |
| Định lý Bayes | P(B \| A) = P(A \| B)·P(B) / P(A) |
| Độc lập có điều kiện | A ⫫ C \| B ⇔ P(A \| B, C) = P(A \| B) |
| Odds, log-odds (logit) | odds = p/(1−p); logit(p) = ln(p/(1−p)) |

**Ví dụ minh họa.** Cho P(mất việc) = 10%, P(vỡ nợ | mất việc) = 30%, P(vỡ nợ | không mất việc) = 5%.
- Suy luận **xuôi** (lấy biên): P(vỡ nợ) = 0,1·0,3 + 0,9·0,05 = 7,5%.
- Suy luận **ngược** (Bayes): P(mất việc | vỡ nợ) = 0,1·0,3 / 0,075 = 40%. Nghĩa là trong những người vỡ nợ, 40%
  đã mất việc, dù chỉ 10% dân số mất việc.

## 2.3. Mạng Bayes (Bayesian Network)
- **Định nghĩa.** BN gồm (1) một đồ thị có hướng không chu trình (DAG): mỗi nút là một biến, cạnh A → B nghĩa là
  A ảnh hưởng trực tiếp tới B; (2) mỗi nút có một **bảng xác suất có điều kiện (CPT)** P(nút | các nút cha).
- **Phân rã.** Xác suất đồng thời của mọi biến = tích các CPT: P(X1..Xn) = Π P(Xi | Cha(Xi)). Nhờ vậy, thay vì một
  bảng khổng lồ, ta chỉ cần nhiều bảng nhỏ.
- **Kích thước CPT.** CPT của nút có r trạng thái và các cha có tổng cộng q tổ hợp có (r−1)·q tham số tự do.
  - Ví dụ: nút Vỡ nợ (2 trạng thái) có 5 cha dữ liệu với 5·5·5·5·3 = 1.875 tổ hợp, cộng nút Hụt dòng tiền (2 trạng
    thái), nên có 3.750 tổ hợp cha.
  - Mỗi tổ hợp cần đủ dữ liệu, nên **càng nhiều cha thì càng cần nhiều dữ liệu**. Thí nghiệm German Credit cho thấy
    rõ điều này.
- **d-separation** (tách theo đồ thị). Quy tắc đọc độc lập có điều kiện từ đồ thị.
  - Chuỗi A → B → C và phân nhánh A ← B → C: A và C bị chặn khi **biết** B.
  - Hội tụ A → B ← C (collider): A và C bị chặn khi **không biết** B và không biết hậu duệ nào của B.
  - Hệ quả trong dự án: khi đã biết mọi cha của nút Vỡ nợ, các biến khác chỉ ảnh hưởng tới vỡ nợ qua các đường còn
    mở (ví dụ qua lớp biến cố).
- **Markov blanket.** Gồm cha, con và cha của con. Khi biết Markov blanket của một nút, nút đó độc lập với mọi nút
  còn lại.
- **Suy luận chính xác.** Muốn tính P(Q | bằng chứng e), ta cộng (lấy biên) các biến ẩn trong tích CPT.
  - Variable Elimination (VE) làm việc này theo một thứ tự khử biến để tránh bảng quá lớn.
  - Bộ suy luận của dự án làm đúng phép toán này bằng `numpy.einsum` cho hàng nghìn hồ sơ cùng lúc (mục 4.5).
- **Thiếu thông tin.** Biến không biết thì **lấy biên** theo xác suất, không cần điền giá trị giả. Đây là lợi thế tự
  nhiên của BN so với đa số mô hình ML.
- **MAP (maximum a posteriori).** Tìm tổ hợp giá trị *khả dĩ nhất* của một nhóm biến khi biết bằng chứng.

## 2.4. Học Mạng Bayes từ dữ liệu
**Học tham số (CPT) khi đã biết cấu trúc.**
- **MLE (đếm):** θ_ijk = N_ijk / N_ij. Ở đây N_ij là số dòng có tổ hợp cha j, còn N_ijk là số dòng trong đó nút ở
  trạng thái k. Nhược điểm: tổ hợp ít hoặc chưa gặp thì ước lượng 0/0 hoặc rất nhiễu.
- **Bayes với prior Dirichlet:** θ_ijk = (N_ijk + α_ijk) / (N_ij + Σ_k α_ijk).
  - **BDeu** dùng α = ESS/(q·r), chia đều. Tổ hợp chưa gặp nhận phân phối **đều**, tức P(vỡ nợ) = 50%. Điều này vô
    lý khi tỷ lệ nền chỉ là 8%.
  - **m-estimate** (Cestnik 1990) dùng α_ijk = m·P(k) với P(k) là phân phối biên. Tổ hợp chưa gặp thì lùi về **tỷ
    lệ nền**. Dự án dùng cách này với m = 10, chọn trên validation tách từ train.
  - Ví dụ m-estimate: tổ hợp có 20 người, 4 vỡ nợ, P(1) = 0,08, m = 10 → (4 + 0,8)/(20 + 10) = 16%. Tổ hợp chưa
    gặp → 0,8/10 = 8%.

**Học cấu trúc** (máy tự tìm DAG). Đây là các biến thể để so sánh với cấu trúc chuyên gia.
- **Naive Bayes:** mọi biến là con của Vỡ nợ và độc lập với nhau khi biết Vỡ nợ. Đơn giản, ít tham số, hợp với dữ
  liệu ít.
- **TAN (Tree-Augmented NB):** NB cộng thêm một cây nối các biến. Cây được chọn theo thông tin tương hỗ có điều
  kiện (Chow–Liu). TAN thường chính xác hơn NB.
- **Hill-Climbing + BIC (BN-Learned):** thêm, bớt hoặc đảo cạnh để tối đa điểm BIC = log-likelihood − (số tham
  số/2)·log N.
  - Nhược điểm: tìm ra các DAG *tương đương Markov*, nên chiều cạnh có thể ngược nhân quả. Ví dụ: "thu nhập →
    ngành".
- **BN-Hybrid:** Hill-Climbing nhưng bắt buộc giữ các cạnh chuyên gia và tuân thứ tự tầng thời gian (biến sau
  không được làm cha biến trước).

## 2.5. Mô hình hóa tri thức chuyên gia trong CPT
- **Noisy-OR.** Mỗi nguyên nhân i (ví dụ mất việc, ốm đau) tự gây ra hệ quả (hụt dòng tiền) với xác suất λ_i, độc
  lập với nhau; leak là xác suất hệ quả xảy ra mà không có nguyên nhân nào.
  - Công thức: P(hệ quả | các nguyên nhân bật) = 1 − (1 − leak)·Π(1 − λ_i).
  - Ưu điểm: chỉ cần một tham số cho mỗi nguyên nhân thay vì cả bảng 2^n.
- **Ràng buộc đơn điệu.** Ví dụ "DSTI tăng thì P(vỡ nợ) không giảm" khi giữ nguyên các cha khác.
  - Cách áp ràng buộc: **isotonic regression**, tức là tìm dãy đơn điệu gần dãy gốc nhất (bình phương có trọng số).
  - Khi có nhiều ràng buộc theo nhiều trục, ta chiếu luân phiên lên từng tập ràng buộc (POCS – projection onto
    convex sets).

## 2.6. Nhân quả: quan sát và can thiệp
- **Quan sát** P(Y | X = x) trả lời "những người *có* X = x thì Y thế nào". Câu trả lời này bị lẫn với nguyên nhân
  chung. Ví dụ người thu nhập cao thường lớn tuổi hơn.
- **Can thiệp** P(Y | do(X = x)) (Pearl) trả lời "nếu *đặt* X = x thì Y thế nào".
  - Cách tính trên BN là **graph surgery**: cắt mọi cạnh đi vào X rồi cố định giá trị X.
  - Lời khuyên "hãy giảm DSTI" là một can thiệp, nên kế hoạch cải thiện điểm của dự án dùng do().
- **Phản thực (counterfactual) trong dự án:** "nếu hồ sơ này thay đổi các yếu tố điều khiển được (đòn bẩy) thì điểm
  thành bao nhiêu?" Ta duyệt mọi tổ hợp thay đổi, chọn những kế hoạch rẻ nhất đạt mục tiêu.

## 2.7. Học máy "hộp đen" dùng để so sánh
| Mô hình | Ý tưởng | Điểm mạnh / yếu |
|---|---|---|
| Hồi quy logistic (LR) | logit(p) = w·x + b | Hiệu chỉnh tốt, dễ hiểu theo hệ số; tuyến tính |
| XGBoost, LightGBM | Gradient boosting: cộng dần nhiều cây quyết định nhỏ, mỗi cây sửa lỗi của tổng trước | Thường chính xác nhất trên dữ liệu bảng; khó giải thích; xử lý NaN bằng "nhánh mặc định" |
| Random Forest (RF) | Trung bình nhiều cây học trên mẫu bootstrap | Ổn định; xác suất thường kém hiệu chỉnh |
| MLP | Mạng nơ-ron nhiều lớp | Linh hoạt; cần chuẩn hóa; khó giải thích |
| XGBoost-Mono | XGBoost có `monotone_constraints` | Cho thấy ML *cũng* có thể nhúng tri thức đơn điệu – so sánh công bằng với BN-Expert-Mono |

**Giải thích mô hình hộp đen: SHAP.**
- Mỗi biến nhận một phần đóng góp sao cho tổng các đóng góp = dự báo − dự báo trung bình. Cách chia dựa trên giá
  trị Shapley trong lý thuyết trò chơi.
- **TreeSHAP** tính chính xác và nhanh cho mô hình cây.

**Tinh chỉnh siêu tham số: Optuna (TPE).** Optuna thử các bộ tham số, học từ các lần thử trước để chọn bộ tiếp
theo. Dự án chỉ tinh chỉnh trên dữ liệu train, không bao giờ chạm vào test.

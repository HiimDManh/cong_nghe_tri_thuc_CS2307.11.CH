## 2. Thu thập và biểu diễn tri thức

### 2.1. Nguồn tri thức

Tri thức đưa vào mạng Bayes gồm hai loại. Loại thứ nhất là tri thức có thể học từ dữ liệu, nằm ở lớp dữ liệu Home Credit. Loại thứ hai là tri thức vĩ mô và biến cố không có trong bộ dữ liệu, nằm ở lớp chuyên gia. Lớp chuyên gia được lấy từ các nguồn công khai, mỗi nguồn có URL và năm truy xuất trong `knowledge_base/`.

| Tri thức | Nguồn | File | Dùng cho |
|---|---|---|---|
| Ngành → 10 nhóm | ISIC Rev.4 (UN), cách gộp của GSO | `knowledge_base/sector_mapping.csv` | nút Ngành |
| Nghề → 5 nhóm | ISCO-08 (ILO) | `knowledge_base/occupation_mapping.csv` | nút Nhóm nghề |
| Lạm phát, thất nghiệp, GDP VN 2000–2024 | World Bank WDI API | `knowledge_base/macro_vn_worldbank.csv` | CPT Lạm phát, Chu kỳ KT, Mất việc |
| Chi y tế thảm họa theo tuổi | WHO GHO (SDG 3.8.2) | `knowledge_base/health_catastrophic_vn_who.csv` | CPT Biến cố sức khỏe |
| Thu nhập & chi tiêu theo ngũ phân vị 2024 | GSO – KSMS 2024 (Biểu 4, 11) | `knowledge_base/vn_income_spending_quintiles_2024.csv` | đệm tài chính; quy đổi VND trong demo |
| Ngưỡng DSTI/LTI | FCA (UK), HCSF (Pháp), Eesti Pank (Estonia) | `knowledge_base/debt_threshold_sources.csv` | ngưỡng rời rạc hóa |
| Thu nhập từ việc làm theo ngành, 2024 (COULD) | GSO – Báo cáo điều tra lao động việc làm 2024, Biểu 3.4 | chưa đưa vào `knowledge_base/` | chưa dùng trong mô hình |
| Trọng số FICO | myFICO | `configs/fico.yaml` | baseline FICO |

Các ngưỡng nợ được đối chiếu với văn bản gốc, không chỉ với nguồn thứ cấp. Kết quả đối chiếu nằm trong `docs/handoff/nam_source_verification.csv`:

- **UK (LTI 4,5 lần, tối đa 15% số khoản vay mới):** khớp với FCA FG17/2 (sửa đổi tháng 02/2017), trang 1, đoạn 1.2, và định nghĩa LTI ở trang 5. FCA giới thiệu mức 4,5 lần từ FG14/8 (có hiệu lực 01/10/2014). Giới hạn tính trên số hợp đồng vay, không phải giá trị vay.
- **Pháp (DSTI 35%):** khớp với Quyết định D-HCSF-2021-7 ngày 29/09/2021, hiệu lực từ 01/01/2022, Điều 1(i). Thu nhập tính là thu nhập ròng trước thuế (Điều 4). Quyết định này có biên linh hoạt 20% số khoản vay mới mỗi quý. ECB (2023) chỉ trích dẫn con số này, nên bài viết dẫn trực tiếp quyết định HCSF.
- **Estonia (DSTI 50%, ngoại lệ 15% mỗi quý):** khớp với Decree No. 17 của Eesti Pank, §4(2) và §6, bản hiện hành có hiệu lực từ 16/06/2025. Đây là văn bản gốc, nguồn thứ cấp của Bank of Finland không còn cần dùng.

Riêng thông tin về mục tiêu lạm phát Việt Nam, văn bản chính thức là Nghị quyết số 244/2025/QH15 (13/11/2025), Điều 2 khoản 4, đặt CPI bình quân năm 2026 khoảng **4,5%**. Repo hiện dùng ngưỡng 4% trong `configs/bn_expert_cpt.yaml`. Vấn đề này được nêu ở mục 2.4.

### 2.2. Biểu diễn tri thức trong mô hình

Tri thức được biểu diễn theo bốn dạng, mỗi dạng có nguồn riêng.

**Tri thức cấu trúc.** Các cạnh của DAG thể hiện quan hệ nhân quả, ví dụ "Ngành → Nhóm nghề" hay "Biến cố → Khả năng vỡ nợ". Mỗi cạnh trong `configs/bn_expert.yaml` có lý do và bằng chứng, hoặc được ghi rõ là giả định. DAG gồm 14 nút dữ liệu và 6 nút chuyên gia (hình dưới).

{{fig:bn_expert_dag.png|DAG BN-Expert: 14 nút dữ liệu (xanh) và 6 nút tri thức (cam)}}

**Tri thức định lượng.** Các bảng xác suất có điều kiện (CPT) của nút chuyên gia được sinh tự động từ dữ liệu nguồn. Ví dụ, xác suất lạm phát ở mức thấp, vừa, cao được tính từ tần suất năm 2000–2024 với ngưỡng 4% và 8%. Các hệ số còn lại như hệ số đệm tài chính theo ngũ phân vị, và hệ số theo thâm niên, được ghi trong bảng dưới đây.

Tham số lớp tri thức (sinh tự động từ nguồn):

{{file:reports/bn/expert_params.md}}

**Tri thức ràng buộc.** Mô hình BN-Expert-Mono áp ràng buộc đơn điệu cho hai quan hệ: DSTI tăng thì rủi ro vỡ nợ không giảm, và điểm lịch sử tín dụng tăng thì rủi ro không tăng. Ràng buộc này là tri thức từ kinh nghiệm tín dụng, không phải từ dữ liệu.

**Tri thức ngưỡng.** Các biến liên tục được rời rạc hóa theo `configs/discretize.yaml`. Thu nhập và điểm lịch sử tín dụng dùng ngũ phân vị, ước lượng chỉ trên tập train. Các biến DSTI và LTI dùng ngưỡng nghiệp vụ lấy từ mục 2.1.

Phân biệt rõ phần có nguồn và phần là giả định. Nguồn gồm: CPT lạm phát, CPT biến cố sức khỏe, ngưỡng DSTI/LTI, thu nhập theo ngũ phân vị. Giả định gồm: ngưỡng suy thoái 5% GDP, hệ số ngành và thâm niên cho mất việc, hệ số đệm tài chính, và λ = 0,3 trong nối noisy-OR.

### 2.3. Kiểm tra tri thức bằng dữ liệu

Để biết tri thức nào được dữ liệu ủng hộ, nhóm tính Cramér's V cho từng cạnh giữa các nút dữ liệu (`reports/eda/bn_expert_edge_support.md`). Giá trị V càng lớn thì liên hệ càng mạnh.

Các cạnh được dữ liệu ủng hộ mạnh gồm: Ngành → Nhóm nghề, Ngành → Ổn định việc làm, Tuổi → Ổn định việc làm, và Điểm lịch sử tín dụng → Vỡ nợ. Điểm lịch sử tín dụng là biến có liên hệ mạnh nhất với vỡ nợ trong số các biến dữ liệu. Liên hệ giữa Thâm niên và Điểm lịch sử tín dụng yếu hơn nhiều.

Một số tri thức không khớp với dữ liệu. Liên hệ giữa gánh nặng trả nợ (DSTI) và vỡ nợ rất yếu, và không đơn điệu. Một giả thuyết cần kiểm chứng là thiên lệch chọn mẫu: Home Credit chỉ gồm các khoản vay đã được cấp, nên người có DSTI cao có thể đã bị từ chối trước khi vào tập dữ liệu. Nhóm chưa kiểm chứng giả thuyết này. Liên hệ giữa Ngành và Thu nhập cũng yếu (V ≈ 0,12), dù tri thức cho rằng ngành quyết định thu nhập. Hai trường hợp này được nêu trong báo cáo kết quả, không điều chỉnh để mô hình khớp hơn.

Các cạnh từ lớp chuyên gia không có dữ liệu để kiểm tra, vì Home Credit không có biến lạm phát, suy thoái hay biến cố sức khỏe. Chúng chỉ được đánh giá bằng nguồn và bằng phân tích độ nhạy.

### 2.4. Hạn chế của tri thức

- **Tiền tệ và quốc gia không rõ.** Home Credit không công bố quốc gia hay đơn vị tiền tệ. Vì vậy thu nhập được rời rạc theo ngũ phân vị, không dùng ngưỡng VND. Tri thức vĩ mô lấy từ Việt Nam vì demo hướng tới người dùng Việt Nam. Điều này làm các nút vĩ mô chỉ dùng cho phân tích what-if, không đưa vào so sánh định lượng với mô hình học máy.
- **Ngành bị ẩn danh.** Home Credit chỉ có loại ngành dạng "Industry: type N" và "Business Entity Type N", nên ánh xạ chỉ đến mức nhóm ISIC. "Business Entity" được xếp vào nhóm không rõ ngành.
- **Thu nhập không khớp đơn vị.** KSMS 2024 cho thu nhập bình quân đầu người trong hộ, còn Home Credit cho thu nhập của người vay. Demo quy đổi bằng thu nhập hộ chia số nhân khẩu, đây là phép xấp xỉ. Ranh giới ngũ phân vị không được công bố, nên dùng trung điểm giữa hai nhóm kề nhau. Đây là giả định.
- **Thu nhập theo ngành chưa đưa vào mô hình.** Biểu 3.4 của GSO cho thu nhập từ việc làm theo mã ngành A–U, đơn vị nghìn đồng/tháng, chỉ áp dụng cho lao động làm công ăn lương. Việc ánh xạ 21 mã ngành sang 10 nhóm của repo chưa được thực hiện. Mục này nằm trong phần COULD.
- **Ngưỡng lạm phát chưa thống nhất.** `configs/bn_expert_cpt.yaml` ghi ngưỡng 4% là "mục tiêu lạm phát ~4%", nhưng văn bản chính thức năm 2026 là khoảng 4,5%. Nhóm cần quyết định giữ ngưỡng 4% như một ngưỡng rời rạc, bỏ cách gọi "mục tiêu", hay đổi sang 4,5%.
- **Hệ số là giả định.** Ngưỡng suy thoái 5%, hệ số ngành và thâm niên cho mất việc, hệ số đệm tài chính và λ = 0,3 đều là giả định. Báo cáo có phân tích độ nhạy theo λ trong Chương 4.

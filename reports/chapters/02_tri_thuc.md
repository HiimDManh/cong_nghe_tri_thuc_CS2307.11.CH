## 2. Thu thập và biểu diễn tri thức

### 2.1. Nguồn tri thức

Mạng Bayes của nhóm dùng hai loại tri thức. Loại thứ nhất học được từ dữ liệu Home Credit. Loại thứ hai là tri thức vĩ mô và các biến cố (lạm phát, suy thoái, mất việc, ốm đau) mà bộ dữ liệu không có, nên phải lấy từ bên ngoài và đặt vào lớp chuyên gia. Mọi nguồn của lớp này đều công khai, và mỗi file trong `knowledge_base/` ghi kèm URL và năm truy xuất.

| Tri thức | Nguồn | File | Dùng cho |
|---|---|---|---|
| Ngành → 10 nhóm | ISIC Rev.4 (UN), cách gộp của GSO | `knowledge_base/sector_mapping.csv` | nút Ngành |
| Nghề → 5 nhóm | ISCO-08 (ILO) | `knowledge_base/occupation_mapping.csv` | nút Nhóm nghề |
| Lạm phát, thất nghiệp, GDP VN 2000–2024 | World Bank WDI API | `knowledge_base/macro_vn_worldbank.csv` | CPT Lạm phát, Chu kỳ KT, Mất việc |
| Chi y tế thảm họa theo tuổi | WHO GHO (SDG 3.8.2) | `knowledge_base/health_catastrophic_vn_who.csv` | CPT Biến cố sức khỏe |
| Thu nhập và chi tiêu theo ngũ phân vị 2024 | GSO, KSMS 2024 (Biểu 4, 11) | `knowledge_base/vn_income_spending_quintiles_2024.csv` | đệm tài chính; quy đổi VND trong demo |
| Ngưỡng DSTI/LTI | FCA (UK), HCSF (Pháp), Eesti Pank (Estonia) | `knowledge_base/debt_threshold_sources.csv` | ngưỡng rời rạc hóa |
| Thu nhập từ việc làm theo ngành, 2024 (COULD) | GSO, Báo cáo điều tra lao động việc làm 2024, Biểu 3.4 | chưa đưa vào `knowledge_base/` | chưa dùng trong mô hình |
| Trọng số FICO | myFICO | `configs/fico.yaml` | baseline FICO |

Ban đầu một số ngưỡng nợ mới chỉ được đọc qua kết quả tìm kiếm hoặc nguồn thứ cấp, nên chúng tôi mở lại văn bản gốc để đối chiếu. Kết quả nằm trong `docs/handoff/nam_source_verification.csv`.

- UK: mức LTI 4,5 lần, tối đa 15% số khoản vay mới, khớp với FCA FG17/2 (sửa đổi tháng 02/2017), trang 1, đoạn 1.2, và định nghĩa LTI ở trang 5. FCA đưa ra mức 4,5 lần từ FG14/8, có hiệu lực ngày 01/10/2014. Giới hạn 15% tính theo số hợp đồng vay chứ không theo giá trị vay.
- Pháp: DSTI 35% khớp với Quyết định D-HCSF-2021-7 ngày 29/09/2021, hiệu lực từ 01/01/2022, Điều 1(i). Thu nhập tính là thu nhập ròng trước thuế (Điều 4), và quyết định cho phép 20% số khoản vay mới mỗi quý vượt ngưỡng. ECB (2023) chỉ nhắc lại con số này, vì vậy báo cáo dẫn thẳng quyết định của HCSF.
- Estonia: DSTI 50%, ngoại lệ 15% mỗi quý, khớp với Decree No. 17 của Eesti Pank, §4(2) và §6, bản hiện hành có hiệu lực từ 16/06/2025. Đây là văn bản gốc nên không cần dùng nguồn thứ cấp của Bank of Finland nữa.
- Việt Nam: Nghị quyết số 244/2025/QH15 (13/11/2025), Điều 2 khoản 4, đặt CPI bình quân năm 2026 ở mức khoảng 4,5%. Repo đang dùng ngưỡng 4% trong `configs/bn_expert_cpt.yaml`, chi tiết ở mục 2.4.

### 2.2. Biểu diễn tri thức trong mô hình

Tri thức đi vào mô hình theo bốn cách, và mỗi cách có nguồn riêng.

Trước hết là cấu trúc. Các cạnh của DAG nói lên quan hệ nhân quả, chẳng hạn Ngành → Nhóm nghề hay Biến cố → Khả năng vỡ nợ. Trong `configs/bn_expert.yaml`, mỗi cạnh đều có lý do và bằng chứng đi kèm, hoặc được ghi thẳng là giả định. DAG có 14 nút dữ liệu và 6 nút chuyên gia (hình dưới).

{{fig:bn_expert_dag.png|DAG BN-Expert: 14 nút dữ liệu (xanh) và 6 nút tri thức (cam)}}

Thứ hai là các con số. Bảng xác suất có điều kiện (CPT) của nút chuyên gia được sinh tự động từ dữ liệu nguồn. Chẳng hạn, xác suất lạm phát thấp, vừa, cao tính từ tần suất các năm 2000–2024 với ngưỡng 4% và 8%. Tỷ lệ thất nghiệp nền, xác suất biến cố sức khỏe theo tuổi và hệ số đệm tài chính theo ngũ phân vị cũng lấy từ nguồn ở mục 2.1. Hệ số ngành của biến cố mất việc là một proxy tính từ chính Home Credit (tỷ lệ người có thâm niên dưới một năm theo ngành), chứ không phải số liệu của Việt Nam. Bảng dưới liệt kê toàn bộ tham số, phần đầu có nguồn, phần cuối là giả định.

{{file:reports/bn/expert_params.md}}

Thứ ba là ràng buộc. Mô hình BN-Expert-Mono bắt hai quan hệ phải đơn điệu: DSTI tăng thì rủi ro vỡ nợ không được giảm, và điểm lịch sử tín dụng tăng thì rủi ro không được tăng. Hai ràng buộc này đến từ kinh nghiệm tín dụng, không phải từ dữ liệu.

Cuối cùng là ngưỡng. Các biến liên tục được rời rạc hóa theo `configs/discretize.yaml`. Thu nhập và điểm lịch sử tín dụng chia theo ngũ phân vị, ước lượng chỉ trên tập train. DSTI và LTI dùng ngưỡng nghiệp vụ ở mục 2.1.

Về ranh giới giữa nguồn và giả định: có nguồn gồm CPT lạm phát, thất nghiệp nền, CPT biến cố sức khỏe, hệ số đệm tài chính theo ngũ phân vị và ngưỡng DSTI/LTI. Phần giả định gồm ngưỡng suy thoái 5% GDP, hệ số thâm niên, hệ số thời hạn, các tham số của chi phí sinh hoạt và hụt dòng tiền (kể cả hệ số theo tài sản), và λ = 0,3 ở nối noisy-OR giữa nút Hụt dòng tiền với Vỡ nợ.

### 2.3. Kiểm tra tri thức bằng dữ liệu

Để biết dữ liệu có ủng hộ tri thức hay không, chúng tôi tính Cramér's V cho từng cạnh giữa các nút dữ liệu (`reports/eda/bn_expert_edge_support.md`). V càng lớn thì liên hệ càng mạnh.

Dữ liệu ủng hộ rõ các cạnh Ngành → Nhóm nghề, Ngành → Ổn định việc làm, Tuổi → Ổn định việc làm và Điểm lịch sử tín dụng → Vỡ nợ. Trong các biến dữ liệu, điểm lịch sử tín dụng liên hệ mạnh nhất với vỡ nợ, trong khi liên hệ giữa Thâm niên và Điểm lịch sử tín dụng yếu hơn nhiều.

Một số tri thức lại không khớp. Liên hệ giữa gánh nặng trả nợ (DSTI) và vỡ nợ rất yếu và không đơn điệu. Có thể là do thiên lệch chọn mẫu: Home Credit chỉ chứa các khoản vay đã được cấp, nên người có DSTI cao có thể đã bị từ chối trước khi vào dữ liệu. Chúng tôi chưa kiểm chứng giả thuyết này. Liên hệ giữa Ngành và Thu nhập cũng yếu (V ≈ 0,12), trong khi tri thức cho rằng ngành quyết định thu nhập. Cả hai trường hợp được nêu nguyên trạng trong báo cáo kết quả, mô hình không được chỉnh để khớp hơn.

Các cạnh của lớp chuyên gia không kiểm tra được bằng dữ liệu, vì Home Credit không có biến lạm phát, suy thoái hay biến cố sức khỏe. Chúng chỉ được đánh giá qua nguồn và qua phân tích độ nhạy.

### 2.4. Hạn chế của tri thức

- Quốc gia và tiền tệ không rõ. Home Credit không công bố hai thông tin này, nên thu nhập được chia theo ngũ phân vị thay vì ngưỡng VND. Tri thức vĩ mô lấy của Việt Nam vì demo hướng tới người dùng Việt Nam. Do đó các nút vĩ mô chỉ dùng cho phân tích what-if và không tham gia so sánh định lượng với học máy.
- Ngành bị ẩn danh. Dữ liệu chỉ ghi "Industry: type N" và "Business Entity Type N", nên ánh xạ chỉ đến được mức nhóm ISIC, và "Business Entity" được xếp vào nhóm không rõ ngành.
- Đơn vị thu nhập lệch nhau. KSMS 2024 cho thu nhập bình quân đầu người trong hộ, còn Home Credit ghi thu nhập của người vay. Demo xấp xỉ bằng thu nhập hộ chia số nhân khẩu. Ranh giới ngũ phân vị của Việt Nam không được công bố, nên demo lấy trung điểm giữa trung bình hai nhóm kề nhau, và đây là một giả định.
- Thu nhập theo ngành chưa vào mô hình. Biểu 3.4 của GSO cho thu nhập từ việc làm theo mã ngành A–U, đơn vị nghìn đồng một tháng, và chỉ áp dụng cho lao động làm công ăn lương. Việc gộp 21 mã này vào 10 nhóm của repo chưa làm, vì mục này thuộc phần COULD.
- Ngưỡng lạm phát là quy ước, không phải mục tiêu chính sách. Văn bản chính thức của năm 2026 đặt CPI bình quân khoảng 4,5%, còn mô hình dùng ngưỡng 4% để chia chuỗi 2000–2024 thành ba mức. Nhóm giữ 4% và không gọi đó là "mục tiêu". Lý do: ngưỡng áp cho cả 25 năm chứ không cho riêng một năm, và trong chuỗi chỉ có năm 2014 (4,09%) nằm giữa 4% và 4,5%. Nếu đổi sang 4,5% thì chỉ năm này chuyển từ mức vừa sang mức thấp (`knowledge_base/macro_vn_worldbank.csv`).
- Nhiều hệ số là giả định. Danh sách đầy đủ nằm ở cuối mục 2.2. Ảnh hưởng của λ được phân tích độ nhạy trong Chương 4.

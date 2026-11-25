## 2. Thu thập và biểu diễn tri thức

### 2.1. Nguồn tri thức

Mạng Bayes của nhóm dùng hai loại tri thức. Loại đầu là những gì có thể học thẳng từ dữ liệu Home Credit, nằm ở lớp dữ liệu. Loại thứ hai là các yếu tố vĩ mô và biến cố mà bộ dữ liệu này không có, ví dụ lạm phát hay mất việc. Những yếu tố này thuộc lớp chuyên gia, và chúng tôi lấy từ các nguồn công khai. Mỗi file trong `knowledge_base/` đều ghi URL và năm truy xuất để ai cũng kiểm tra lại được.

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

Với các ngưỡng nợ, chúng tôi không dừng ở nguồn thứ cấp mà đối chiếu lại với văn bản gốc. Kết quả chi tiết nằm trong `docs/handoff/nam_source_verification.csv`; dưới đây là tóm tắt.

Ở Anh, giới hạn LTI 4,5 lần áp dụng cho tối đa 15% số khoản vay mới. Con số này khớp với hướng dẫn FCA FG17/2 (bản sửa đổi tháng 02/2017), đoạn 1.2 ở trang 1, và phần định nghĩa LTI ở trang 5. Mức 4,5 lần được FCA đưa ra lần đầu trong FG14/8, có hiệu lực từ 01/10/2014. Cần lưu ý giới hạn này tính theo số hợp đồng vay chứ không tính theo giá trị khoản vay.

Ở Pháp, trần DSTI 35% nằm trong Quyết định D-HCSF-2021-7 của HCSF, ký ngày 29/09/2021 và có hiệu lực từ 01/01/2022 (Điều 1(i)). Thu nhập ở đây là thu nhập ròng trước thuế (Điều 4), và quyết định còn cho phép một biên linh hoạt 20% số khoản vay mới mỗi quý. Bài của ECB (2023) chỉ nhắc lại con số này, vì vậy chúng tôi dẫn thẳng quyết định của HCSF.

Ở Estonia, trần DSTI 50% và ngoại lệ 15% mỗi quý nằm ở §4(2) và §6 của Decree No. 17 do Eesti Pank ban hành. Bản hiện hành có hiệu lực từ 16/06/2025 và vẫn giữ nguyên các mức này. Đây là văn bản gốc, nên slide của Bank of Finland mà trước đó nhóm dùng không còn cần thiết.

Riêng mục tiêu lạm phát của Việt Nam thì kết quả đối chiếu khác với những gì repo đang ghi. Nghị quyết số 244/2025/QH15 (ngày 13/11/2025), Điều 2 khoản 4, đặt CPI bình quân năm 2026 ở mức khoảng **4,5%**, trong khi `configs/bn_expert_cpt.yaml` đang dùng ngưỡng 4%. Chúng tôi quay lại vấn đề này ở mục 2.4.

### 2.2. Biểu diễn tri thức trong mô hình

Tri thức đi vào mô hình theo bốn cách, và mỗi cách dựa trên một loại căn cứ khác nhau.

Cách thứ nhất là cấu trúc đồ thị. Mỗi cạnh của DAG diễn tả một quan hệ nhân quả, chẳng hạn từ Ngành sang Nhóm nghề, hay từ Biến cố sang Khả năng vỡ nợ. Trong `configs/bn_expert.yaml`, mỗi cạnh đều đi kèm lý do và bằng chứng, hoặc được ghi thẳng là giả định. Toàn bộ DAG có 14 nút dữ liệu và 6 nút chuyên gia (hình bên dưới).

{{fig:bn_expert_dag.png|DAG BN-Expert: 14 nút dữ liệu (xanh) và 6 nút tri thức (cam)}}

Cách thứ hai là các bảng xác suất có điều kiện (CPT) của nút chuyên gia, được sinh tự động từ số liệu nguồn. Chẳng hạn, xác suất lạm phát ở mức thấp, vừa hay cao được đếm từ tần suất các năm 2000–2024 với hai ngưỡng 4% và 8%. Các hệ số khác, như hệ số đệm tài chính theo ngũ phân vị hay hệ số theo thâm niên, được liệt kê trong bảng sau.

Tham số lớp tri thức (sinh tự động từ nguồn):

{{file:reports/bn/expert_params.md}}

Cách thứ ba là ràng buộc đơn điệu, dùng trong mô hình BN-Expert-Mono. Mô hình bắt buộc rủi ro vỡ nợ không giảm khi DSTI tăng, và không tăng khi điểm lịch sử tín dụng tăng. Hai ràng buộc này đến từ kinh nghiệm cho vay chứ không phải từ dữ liệu.

Cách cuối cùng là ngưỡng rời rạc hóa, khai báo trong `configs/discretize.yaml`. Thu nhập và điểm lịch sử tín dụng được chia theo ngũ phân vị, và ngưỡng chỉ được ước lượng trên tập train. DSTI và LTI dùng các ngưỡng nghiệp vụ ở mục 2.1.

Cần phân biệt rõ phần nào có nguồn và phần nào chỉ là giả định. Có nguồn gồm CPT lạm phát, CPT biến cố sức khỏe, ngưỡng DSTI/LTI và thu nhập theo ngũ phân vị. Còn các giả định gồm ngưỡng suy thoái 5% tăng trưởng GDP, hệ số theo ngành và thâm niên cho biến cố mất việc, hệ số đệm tài chính, và λ = 0,3 trong phép nối noisy-OR.

### 2.3. Kiểm tra tri thức bằng dữ liệu

Có tri thức rồi vẫn phải hỏi dữ liệu có đồng ý hay không. Để làm việc này, chúng tôi tính hệ số Cramér's V cho từng cạnh nối giữa các nút dữ liệu (xem `reports/eda/bn_expert_edge_support.md`). V càng lớn thì hai biến càng liên quan chặt.

Kết quả cho thấy một số cạnh được dữ liệu ủng hộ rõ: Ngành → Nhóm nghề, Ngành → Ổn định việc làm, Tuổi → Ổn định việc làm, và Điểm lịch sử tín dụng → Vỡ nợ. Trong các biến dữ liệu, điểm lịch sử tín dụng là biến liên quan mạnh nhất tới vỡ nợ. Ngược lại, quan hệ giữa thâm niên và điểm lịch sử tín dụng khá yếu.

Cũng có những chỗ dữ liệu không đồng tình với tri thức. Gánh nặng trả nợ (DSTI) liên hệ rất yếu với vỡ nợ, và quan hệ này không đơn điệu như ta kỳ vọng. Chúng tôi nghĩ đến thiên lệch chọn mẫu: Home Credit chỉ chứa những khoản vay đã được cấp, nên người có DSTI cao có thể đã bị từ chối ngay từ đầu. Đây mới là giả thuyết, nhóm chưa kiểm chứng. Quan hệ giữa Ngành và Thu nhập cũng yếu (V ≈ 0,12), dù lý thuyết cho rằng ngành quyết định thu nhập. Cả hai trường hợp này đều được báo cáo đúng như số liệu cho thấy, và chúng tôi không chỉnh mô hình để nó khớp hơn.

Các cạnh thuộc lớp chuyên gia thì không kiểm tra được theo cách này, vì Home Credit không có biến lạm phát, suy thoái hay biến cố sức khỏe. Với chúng, căn cứ duy nhất là nguồn trích dẫn và phân tích độ nhạy.

### 2.4. Hạn chế của tri thức

Hạn chế đầu tiên nằm ở bộ dữ liệu. Home Credit không công bố quốc gia hay đơn vị tiền tệ, nên thu nhập phải rời rạc hóa theo ngũ phân vị chứ không dùng ngưỡng VND được. Tri thức vĩ mô thì lấy của Việt Nam, vì demo hướng tới người dùng Việt Nam. Hệ quả là các nút vĩ mô chỉ phục vụ phân tích what-if, chúng tôi không đưa chúng vào phần so sánh định lượng với mô hình học máy. Loại ngành trong Home Credit cũng bị ẩn danh (dạng "Industry: type N" và "Business Entity Type N"), nên ánh xạ chỉ đi được đến mức nhóm ISIC, và "Business Entity" phải xếp vào nhóm không rõ ngành.

Hạn chế thứ hai là đơn vị thu nhập không khớp nhau. KSMS 2024 báo cáo thu nhập bình quân đầu người trong hộ, còn Home Credit ghi thu nhập của chính người vay. Demo quy đổi bằng cách chia thu nhập hộ cho số nhân khẩu, và đây chỉ là phép xấp xỉ. Ranh giới ngũ phân vị cũng không được công bố, nên chúng tôi lấy trung điểm giữa hai nhóm kề nhau, một giả định cần ghi rõ.

Thứ ba, thu nhập theo ngành chưa được đưa vào mô hình. Biểu 3.4 của GSO có số liệu theo mã ngành A–U (nghìn đồng/tháng) nhưng chỉ áp dụng cho lao động làm công ăn lương. Việc ánh xạ 21 mã ngành sang 10 nhóm của repo chưa làm, và mục này vốn thuộc phần COULD.

Thứ tư, ngưỡng lạm phát chưa thống nhất. `configs/bn_expert_cpt.yaml` đang gọi ngưỡng 4% là "mục tiêu lạm phát ~4%", trong khi văn bản chính thức cho năm 2026 là khoảng 4,5%. Nhóm cần quyết định: giữ 4% như một ngưỡng rời rạc nhưng bỏ cách gọi "mục tiêu", hoặc đổi sang 4,5%.

Cuối cùng, nhiều hệ số trong lớp chuyên gia là giả định: ngưỡng suy thoái 5%, hệ số ngành và thâm niên cho mất việc, hệ số đệm tài chính và λ = 0,3. Vì vậy báo cáo có thêm phần phân tích độ nhạy theo λ ở Chương 4.

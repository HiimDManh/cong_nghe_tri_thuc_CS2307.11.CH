## 2. Thu thập và biểu diễn tri thức

<!-- NGƯỜI VIẾT: Nam. Chỉ viết văn bản; KHÔNG tự gõ số – dùng bảng/số đã chèn sẵn bên dưới hoặc trích từ
knowledge_base/*.csv (ghi tên file). Mỗi đoạn trả lời câu hỏi trong ô "Gợi ý" rồi xóa ô đó. -->

### 2.1. Nguồn tri thức
<!-- Gợi ý: mô tả từng nguồn (tổ chức, năm, chỉ số, cách lấy tự động bằng API/xlsx), vì sao chọn. Tham khảo
knowledge_base/README.md. Kết quả đối chiếu bản gốc các ngưỡng nợ (việc G2 của Nam) ghi vào đây: số văn bản,
ngày, điều khoản/trang. -->

| Tri thức | Nguồn | File | Dùng cho |
|---|---|---|---|
| Ngành → 10 nhóm | ISIC Rev.4 (UN), cách gộp của GSO | `knowledge_base/sector_mapping.csv` | nút Ngành |
| Nghề → 5 nhóm | ISCO-08 (ILO) | `knowledge_base/occupation_mapping.csv` | nút Nhóm nghề |
| Lạm phát, thất nghiệp, GDP VN 2000–2024 | World Bank WDI API | `knowledge_base/macro_vn_worldbank.csv` | CPT Lạm phát, Chu kỳ KT, Mất việc |
| Chi y tế thảm họa theo tuổi | WHO GHO (SDG 3.8.2) | `knowledge_base/health_catastrophic_vn_who.csv` | CPT Biến cố sức khỏe |
| Thu nhập & chi tiêu theo ngũ phân vị 2024 | GSO – KSMS 2024 (Biểu 4, 11) | `knowledge_base/vn_income_spending_quintiles_2024.csv` | đệm tài chính; quy đổi VND trong demo |
| Ngưỡng DSTI/LTI | FCA (UK), HCSF (Pháp), Eesti Pank | `knowledge_base/debt_threshold_sources.csv` | ngưỡng rời rạc hóa |
| Trọng số FICO | myFICO | `configs/fico.yaml` | baseline FICO |

### 2.2. Biểu diễn tri thức trong mô hình
<!-- Gợi ý: (1) tri thức cấu trúc = cạnh của DAG, mỗi cạnh có lý do + bằng chứng (configs/bn_expert.yaml);
(2) tri thức định lượng = CPT nút expert sinh từ số liệu nguồn (bảng dưới); (3) tri thức ràng buộc = đơn điệu
(BN-Expert-Mono); (4) tri thức ngưỡng = rời rạc hóa (configs/discretize.yaml). Phân biệt rõ cái nào có nguồn,
cái nào là GIẢ ĐỊNH. -->

{{fig:bn_expert_dag.png|DAG BN-Expert: 14 nút dữ liệu (xanh) và 6 nút tri thức (cam)}}

Tham số lớp tri thức (sinh tự động từ nguồn):

{{file:reports/bn/expert_params.md}}

### 2.3. Kiểm tra tri thức bằng dữ liệu
<!-- Gợi ý: mức ủng hộ của dữ liệu cho từng cạnh (reports/eda/bn_expert_edge_support.md); những tri thức
KHÔNG khớp dữ liệu (DSTI/thu nhập liên hệ yếu và không đơn điệu – nghi do thiên lệch chọn mẫu của ngân hàng). -->

### 2.4. Hạn chế của tri thức
<!-- Gợi ý: Home Credit không công bố quốc gia/tiền tệ → thu nhập dùng ngũ phân vị; ngành bị ẩn danh;
KSMS là thu nhập bình quân đầu người của hộ; chưa có thu nhập theo ngành của VN; các hệ số giả định. -->

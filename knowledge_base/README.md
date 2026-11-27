# Knowledge base – tri thức đã mã hóa

Mỗi file có cột nguồn (`source_url`, năm/ngày truy xuất). Chỗ nào là giả định của nhóm thì ghi rõ "giả định".

| File | Nội dung | Nguồn | Sinh bởi | Dùng cho |
|---|---|---|---|---|
| `sector_mapping.csv` | 58 `ORGANIZATION_TYPE` → 10 nhóm ngành | ISIC Rev.4 (UN); cách gộp "Công nghiệp và xây dựng" của GSO | `scripts/build_mappings.py` | nút **Ngành** |
| `occupation_mapping.csv` | 18 `OCCUPATION_TYPE` (+ thiếu) → 5 nhóm nghề | ISCO-08 (ILO), major group / skill level | `scripts/build_mappings.py` | nút **Nhóm nghề** |
| `macro_vn_worldbank.csv` | VN 2000–2024: lạm phát CPI, thất nghiệp, tăng trưởng GDP, chi y tế tự trả | World Bank WDI API | `python -m src.cli knowledge` | CPT **Lạm phát**, **Chu kỳ KT**, nền **Mất việc** |
| `vn_income_spending_quintiles_2024.csv` | VN 2024: thu nhập & chi tiêu đời sống bình quân đầu người/tháng theo 5 nhóm thu nhập (cả nước, thành thị, nông thôn) | GSO/NSO – KSMS 2024, Biểu 4 & 11 (file xlsx chính thức) | `python -m src.cli knowledge` | hệ số **đệm tài chính** trong CPT Hụt dòng tiền; demo quy đổi VND → ngũ phân vị |
| `debt_threshold_sources.csv` | Ngưỡng LTI 4.5x (UK FPC), DSTI 35% (Pháp HCSF), 50% (Estonia) | FCA FG17/2, HCSF D-HCSF-2021-7, Eesti Pank Decree No. 17 (bản gốc) | tay (có cột `verification`) | căn cứ ngưỡng rời rạc DSTI/LTI |
| `health_catastrophic_vn_who.csv` | VN: % dân số có chi y tế > 10% / 25% chi tiêu hộ (SDG 3.8.2), theo tuổi, thành thị/nông thôn | WHO GHO API | `python -m src.cli knowledge` | CPT **Biến cố sức khỏe ← Tuổi** |

## Ghi chú trung thực
- Home Credit ẩn danh loại ngành ("Industry: type N", "Business Entity Type N") → chỉ ánh xạ được tới mức section ISIC; "Business Entity" là nhóm "không rõ ngành".
- Home Credit **không** công bố quốc gia/đơn vị tiền tệ → thu nhập rời rạc theo ngũ phân vị; tri thức vĩ mô lấy của Việt Nam vì demo hướng tới người dùng VN. Các nút vĩ mô/biến cố chỉ dùng cho what-if, **không** đưa vào so sánh định lượng với ML.
- Chỉ số World Bank `SH.UHC.OOPC.10.ZS` đã bị lưu trữ → lấy bản gốc từ WHO GHO (`FINPROTECTION_CATA_TOT_10_POP`).
- KSMS 2024 là thu nhập **bình quân đầu người trong hộ**, còn Home Credit là thu nhập của **người vay** → demo quy đổi bằng thu nhập hộ / số nhân khẩu; ghi rõ là xấp xỉ.
- Ranh giới ngũ phân vị VN không được công bố, chỉ có trung bình mỗi nhóm → demo dùng trung điểm giữa trung bình hai nhóm kề nhau làm ranh giới (**giả định**).
- Ngưỡng nợ: cả 3 nguồn đã đối chiếu bản gốc (Nam, 25/11/2026; chi tiết `docs/handoff/nam_source_verification.csv`) – số liệu đúng, nguồn trỏ thẳng văn bản gốc thay vì ECB/Bank of Finland.
- Ngưỡng lạm phát 4% (`configs/bn_expert_cpt.yaml`) là ngưỡng rời rạc hóa, không phải mục tiêu; mục tiêu CPI 2026 là ~4,5% (NQ 244/2025/QH15, Điều 2 khoản 4).
- Chưa đưa vào mô hình (COULD): thu nhập từ việc làm theo ngành VN 2024 – Nam đã trích tay GSO, Báo cáo điều tra lao động việc làm 2024, Biểu 3.4/3.5 (dòng 5 `nam_source_verification.csv`); chưa ánh xạ A–U → 10 nhóm ngành.

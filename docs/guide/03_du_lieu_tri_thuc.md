# 3. Dữ liệu và tri thức

## 3.1. Bộ dữ liệu
| | Home Credit Default Risk | German Credit (credit-g) |
|---|---|---|
| Vai trò | **Chính** – mọi thí nghiệm | Phụ – thí nghiệm "dữ liệu ít" |
| Quy mô | 307.511 hồ sơ × 122 cột (`application_train.csv`) | 1.000 hồ sơ × 20 cột |
| Tỷ lệ vỡ nợ | 8,07% | 30% |
| Nguồn | Kaggle (phải chấp nhận luật cuộc thi) | OpenML / UCI |
| Hạn chế | Không công bố quốc gia/tiền tệ; tên ngành bị ẩn danh một phần | Không có thu nhập; biến nghề gần như không liên hệ với vỡ nợ |

Dữ liệu thô nằm ở `data/raw/` và **không commit**. Cách tải xem trong `README.md`.

## 3.2. Mười ba nhóm biến đầu vào (`src/data/home_credit.py`)
| Nút BN | Từ cột Home Credit | Ý nghĩa |
|---|---|---|
| `sector` – Ngành | `ORGANIZATION_TYPE` (58 loại) → 10 nhóm | Ngành kinh tế (ISIC Rev.4) |
| `occupation_group` – Nhóm nghề | `OCCUPATION_TYPE` (18) → 5 nhóm | Trình độ nghề (ISCO-08) |
| `education` – Học vấn | `NAME_EDUCATION_TYPE` → 3 mức | |
| `age_years` – Tuổi | `DAYS_BIRTH` | |
| `years_employed` – Ổn định việc làm | `DAYS_EMPLOYED`; giá trị 365243 = không đi làm | Thâm niên công việc hiện tại |
| `income` – Thu nhập | `AMT_INCOME_TOTAL` | Chia ngũ phân vị |
| `n_children` – Người phụ thuộc | `CNT_CHILDREN` | |
| `assets` – Tài sản | `FLAG_OWN_REALTY`, `FLAG_OWN_CAR` | none / car / realty / both |
| `annuity_to_income` – DSTI | `AMT_ANNUITY / AMT_INCOME_TOTAL` | Gánh nặng trả góp |
| `credit_to_income` – LTI | `AMT_CREDIT / AMT_INCOME_TOTAL` | Dư nợ so với thu nhập |
| `ext_score_mean` – Lịch sử tín dụng | trung bình `EXT_SOURCE_1..3` | Điểm tín dụng từ nguồn ngoài, là proxy của "lịch sử thanh toán" |
| `bureau_inquiries_year` – Tín dụng mới | `AMT_REQ_CREDIT_BUREAU_YEAR` | Số lần tra cứu tín dụng trong năm |
| `region_rating` – Vùng | `REGION_RATING_CLIENT_W_CITY` | 1 = vùng tốt nhất |

Không dùng giới tính và tình trạng hôn nhân. Mọi mô hình (BN, FICO, ML) dùng **cùng** 13 nhóm này để so sánh công
bằng thông tin.

## 3.3. Rời rạc hóa (`configs/discretize.yaml`, `src/data/discretize.py`)
BN rời rạc cần biến có ít trạng thái (≤ 5, riêng Ngành là 10). Có ba cách:
- **Ngưỡng nghiệp vụ cố định:**
  - Tuổi 30/40/50/60: các giai đoạn vòng đời; 60 ≈ tuổi nghỉ hưu.
  - Thâm niên 1/3/7 năm: < 1 năm ≈ mới vào, thử việc.
  - DSTI 10/20/30/40%: 30–40% là vùng trần DSTI thường gặp.
  - LTI 1,5/3/4,5/7: 4,5 là mốc của Anh.
  - Số con 1/2/3; tra cứu 1/2/4.
- **Ngũ phân vị** cho thu nhập và điểm tín dụng ngoài, vì không có thang chuẩn. Ngưỡng **chỉ học trên tập train**
  của từng fold (`Discretizer.fit`), để thông tin từ tập test không rò rỉ vào mô hình.
- **Trạng thái "thiếu" riêng:**
  - `not_working` cho người không đi làm. Đây là thông tin có thật, không phải dữ liệu thiếu.
  - `unknown` cho số lần tra cứu, vì 13,5% dữ liệu bị thiếu.

## 3.4. Ánh xạ ngành và nghề (`knowledge_base/*_mapping.csv`)
- **10 nhóm ngành:**

  | Mã | Nhóm |
  |---|---|
  | `trade_hospitality` | Thương mại, lưu trú & ăn uống |
  | `education_health` | Giáo dục & y tế |
  | `public_admin_security` | Hành chính công & an ninh–quốc phòng |
  | `finance_professional` | Tài chính & dịch vụ chuyên môn |
  | `industry_construction` | Công nghiệp & xây dựng |
  | `transport_postal` | Vận tải & bưu chính |
  | `self_employed` | Tự kinh doanh |
  | `other_services_agri` | Nông nghiệp & dịch vụ khác |
  | `business_unspecified` | Doanh nghiệp không rõ ngành |
  | `not_working` | Không đi làm |

  Mỗi dòng ánh xạ có mã ISIC, lý do và nguồn. Home Credit ẩn danh nhiều loại hình ("Business Entity Type 1–3"), nên
  phải có nhóm "không rõ ngành".
- **5 nhóm nghề** theo ISCO-08 (major group / skill level):

  | Mã | Nhóm |
  |---|---|
  | `manager_professional` | Quản lý & chuyên môn |
  | `technician_clerical` | Kỹ thuật viên & văn phòng |
  | `service_sales` | Dịch vụ & bán hàng |
  | `manual_elementary` | Lao động phổ thông & lái xe |
  | `unknown` | Không khai báo nghề (31% hồ sơ) |

- Bảng được sinh bởi `scripts/build_mappings.py`.

## 3.5. Nguồn tri thức (`knowledge_base/`, chi tiết ở `knowledge_base/README.md`)
| Tri thức | Nguồn | Cách lấy | Dùng cho |
|---|---|---|---|
| Lạm phát CPI, thất nghiệp, tăng trưởng GDP Việt Nam 2000–2024 | World Bank WDI | API `wbgapi` (`src/knowledge/fetch_macro.py`) | CPT Lạm phát, Chu kỳ kinh tế, Mất việc |
| % dân số có chi y tế > 10% chi tiêu hộ, theo tuổi (SDG 3.8.2) | WHO GHO | REST API | CPT Biến cố sức khỏe |
| Thu nhập & chi tiêu bình quân đầu người theo ngũ phân vị, 2024 | Tổng cục Thống kê – Khảo sát mức sống dân cư (KSMS) 2024, Biểu 4 & 11 | file xlsx chính thức (`src/knowledge/fetch_gso.py`) | Hệ số đệm tài chính; quy đổi VND trong demo |
| Ngưỡng DSTI/LTI | FCA (Anh), HCSF (Pháp), Eesti Pank (Estonia) | tra cứu tay; **Nam đang đối chiếu bản gốc** | Ngưỡng rời rạc hóa |
| Trọng số FICO | myFICO | tra cứu | Baseline FICO |

Mỗi file CSV có cột `source_url` và năm / ngày truy xuất. World Bank đã lưu trữ chỉ số chi y tế của mình, nên dự
án lấy bản gốc từ WHO.

## 3.6. CPT của các nút tri thức (`src/bn/expert_cpt.py`, `configs/bn_expert_cpt.yaml`)
Không có xác suất nào được gõ tay. Mọi CPT đều **sinh bằng code** từ file nguồn và tham số trong YAML. Giá trị
thực tế được in ở `reports/bn/expert_params.md`.

| Nút | Cách sinh | Có nguồn / giả định |
|---|---|---|
| Lạm phát (thấp < 4%, vừa 4–8%, cao ≥ 8%) | Tần suất năm Việt Nam 2000–2024 rơi vào từng mức | Nguồn WB; 4% là ngưỡng rời rạc hóa (mục tiêu CPI 2026 là ~4,5%, NQ 244/2025/QH15) |
| Chu kỳ kinh tế (bình thường / suy giảm) | Tần suất năm có GDP tăng < 5% | Nguồn WB; **ngưỡng 5% là giả định** |
| Mất việc | Tỷ lệ thất nghiệp nền (năm bình thường) × hệ số chu kỳ (tính từ WB) × hệ số ngành × hệ số thâm niên × kỳ hạn 2 năm | Nền và chu kỳ có nguồn. Hệ số ngành là *proxy* từ dữ liệu (tỷ lệ thâm niên < 1 năm của ngành). **Hệ số thâm niên và kỳ hạn là giả định**. Không đi làm → P = 0 |
| Biến cố sức khỏe | P(chi y tế > 10%) theo nhóm tuổi < 60 / ≥ 60, WHO 2018 | Có nguồn |
| Chi phí sinh hoạt (thấp / bình thường / cao) | Softmax theo điểm s = mức lạm phát + số con | **Giả định** (bảng đơn điệu) |
| Hụt dòng tiền | Noisy-OR (mất việc 0,6; sức khỏe 0,35; chi phí cao 0,15; leak 0,01) × hệ số đệm thu nhập × hệ số đệm tài sản | Đệm thu nhập lấy từ GSO (tỷ lệ chi tiêu/thu nhập của nhóm k so với nhóm 1). **Các tham số noisy-OR và đệm tài sản là giả định** |

**Cách nói về giả định khi bảo vệ.** Giả định chỉ nằm ở lớp what-if. Nhờ calibrated noisy-OR (mục 4.3), độ chính xác
dự báo khi *không có* bằng chứng biến cố gần như không phụ thuộc vào các giả định này. Riêng λ làm AUC giảm nhẹ khi
λ lớn, do phải cắt p0. Xem bảng độ nhạy λ trong `reports/results_summary.md`.

## 3.7. Kiểm tra tri thức bằng dữ liệu
- `reports/eda/home_credit.md` cho Cramér's V của từng biến với vỡ nợ và tỷ lệ vỡ nợ theo nhóm.
- `reports/eda/bn_expert_edge_support.md` đo mức ủng hộ của dữ liệu cho từng cạnh của DAG.
- Phát hiện quan trọng:
  - Lịch sử tín dụng liên hệ mạnh nhất với vỡ nợ.
  - Thu nhập, DSTI, LTI liên hệ rất yếu và *không đơn điệu*. Điều này mâu thuẫn với tri thức, và nhiều khả năng do
    thiên lệch chọn mẫu.
  - Vì vậy nhóm (1) giữ tri thức bằng ràng buộc đơn điệu, và (2) báo cáo trung thực rằng đòn bẩy thu nhập/chi tiêu có
    tác động yếu.

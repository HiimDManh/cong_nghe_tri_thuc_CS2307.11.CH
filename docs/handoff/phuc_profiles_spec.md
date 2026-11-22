# Đặc tả bộ hồ sơ mẫu (~50) – Phúc

Thêm dòng vào `data/samples/profiles.csv` (đã có 6 dòng mẫu của Mạnh – giữ nguyên định dạng, UTF-8, dấu phẩy).
Gửi file cho Mạnh trước **27/11**. Hồ sơ là **giả lập** – không dùng thông tin người thật.

| Cột | Ý nghĩa | Giá trị hợp lệ |
|---|---|---|
| `name` | Tên mô tả ngắn, duy nhất | vd. "Điều dưỡng 35 tuổi (Đà Nẵng)" |
| `sector` | Nhóm ngành | `trade_hospitality`, `education_health`, `public_admin_security`, `finance_professional`, `industry_construction`, `transport_postal`, `self_employed`, `other_services_agri`, `business_unspecified` (để trống nếu không đi làm) |
| `occupation_group` | Nhóm nghề | `manager_professional`, `technician_clerical`, `service_sales`, `manual_elementary`, `unknown` |
| `education` | Học vấn | `secondary_or_lower`, `incomplete_higher`, `higher` |
| `age` | Tuổi | số 18–90 |
| `working` | Đang đi làm? | `yes` / `no` |
| `years_employed` | Thâm niên công việc hiện tại (năm) | số ≥ 0; trống nếu `working=no` |
| `household_income_m` | Thu nhập cả hộ / tháng (triệu đồng) | số |
| `household_size` | Số người trong hộ | số nguyên ≥ 1 |
| `personal_income_m` | Thu nhập cá nhân / tháng (triệu đồng) | số |
| `n_children` | Số con | số nguyên |
| `own_house`, `own_car` | Có nhà / có ô tô | `yes` / `no` |
| `monthly_installment_m` | Tổng trả góp / tháng (triệu đồng) | số |
| `total_debt_m` | Tổng dư nợ (triệu đồng) | số |
| `credit_history` | Lịch sử trả nợ (tự đánh giá) | `very_poor`, `poor`, `fair`, `good`, `very_good` |
| `inquiries` | Số lần hỏi vay / tra cứu 12 tháng | `0`, `1`, `2-3`, `>=4` |
| `region` | Khu vực | `1` đô thị lớn, `2` đô thị khác, `3` nông thôn/vùng khó khăn |
| `ghi_chu` | Ghi chú | tự do |

**Ô trống = "không rõ"** (hợp lệ, dùng để kiểm thử khả năng chịu thiếu thông tin).

Yêu cầu đa dạng (đếm lại trước khi gửi):
- ≥ 4 hồ sơ cho **mỗi** nhóm ngành; ≥ 4 hồ sơ không đi làm (hưu trí/thất nghiệp).
- Tuổi trải từ 20 đến 70; thu nhập hộ từ ~5 đến ~80 triệu/tháng.
- Có hồ sơ trả góp nặng (trả góp ≥ 40% thu nhập cá nhân) và hồ sơ không nợ.
- ≥ 10 hồ sơ có 3–6 ô trống.
- Thu nhập nên tham khảo mức thật của VN: GSO KSMS 2024 – thu nhập bình quân đầu người/tháng theo nhóm
  (`knowledge_base/vn_income_spending_quintiles_2024.csv`, đơn vị nghìn đồng).

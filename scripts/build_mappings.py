"""Sinh knowledge_base/sector_mapping.csv và occupation_mapping.csv (chạy 1 lần; CSV là nguồn chính thức).

Căn cứ:
- Ngành (ORGANIZATION_TYPE) -> nhóm theo các section của ISIC Rev.4 (UN), cách GSO Việt Nam cũng dùng
  (khu vực "Công nghiệp và xây dựng" gộp B–F).
- Nghề (OCCUPATION_TYPE) -> nhóm theo major group / skill level của ISCO-08 (ILO).
Home Credit ẩn danh "Industry: type N", "Trade: type N", "Transport: type N", "Business Entity Type N"
nên chỉ gán được tới mức section, không tới phân ngành.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISIC = "https://unstats.un.org/unsd/publication/seriesm/seriesm_4rev4e.pdf"
ISCO = "https://www.ilo.org/public/english/bureau/stat/isco/isco08/"

SECTORS = {  # group: (tên tiếng Việt, ISIC, [giá trị gốc], lý do)
    "public_admin_security": ("Hành chính công & An ninh–Quốc phòng", "O", ["Government", "Military", "Police", "Security Ministries", "Emergency"],
                              "Khu vực nhà nước, lương ngân sách ổn định"),
    "education_health": ("Giáo dục & Y tế", "P, Q", ["School", "Kindergarten", "University", "Medicine"],
                         "Dịch vụ công/xã hội, việc làm ổn định"),
    "finance_professional": ("Tài chính, BĐS, Thông tin & Dịch vụ chuyên môn", "J, K, L, M", ["Bank", "Insurance", "Realtor", "Legal Services", "Advertising", "Telecom", "Mobile"],
                             "Dịch vụ tri thức/tài chính; 'Mobile' không rõ nghĩa -> xếp cùng Telecom (J) – giả định"),
    "industry_construction": ("Công nghiệp, Năng lượng & Xây dựng", "B–F", [f"Industry: type {i}" for i in range(1, 14)] + ["Electricity", "Construction"],
                              "Khu vực 'Công nghiệp và xây dựng' theo GSO; Home Credit ẩn danh loại công nghiệp"),
    "trade_hospitality": ("Thương mại, Lưu trú & Ăn uống", "G, I", [f"Trade: type {i}" for i in range(1, 8)] + ["Restaurant", "Hotel"],
                          "Bán lẻ/dịch vụ tiêu dùng, nhạy cảm với chu kỳ kinh tế"),
    "transport_postal": ("Vận tải & Bưu chính", "H", [f"Transport: type {i}" for i in range(1, 5)] + ["Postal"],
                         "Section H gồm cả bưu chính (H53)"),
    "other_services_agri": ("Nông nghiệp & Dịch vụ khác", "A, N, R, S, khác", ["Agriculture", "Security", "Cleaning", "Services", "Housing", "Culture", "Religion", "Other"],
                            "Các nhóm nhỏ (<1% mỗi nhóm) gộp lại; Agriculture chỉ 0.8% nên không tách riêng"),
    "business_unspecified": ("Doanh nghiệp (không rõ ngành)", "không xác định", ["Business Entity Type 1", "Business Entity Type 2", "Business Entity Type 3"],
                             "Home Credit chỉ ghi loại hình doanh nghiệp, không có ngành"),
    "self_employed": ("Tự kinh doanh", "không xác định", ["Self-employed"], "Thu nhập biến động, không có hợp đồng lao động"),
    "not_working": ("Không đi làm (hưu trí/thất nghiệp)", "–", ["XNA"],
                    "XNA trùng gần như hoàn toàn với NAME_INCOME_TYPE=Pensioner/Unemployed (kiểm tra trong EDA)"),
}
OCCUPATIONS = {
    "manager_professional": ("Quản lý & Chuyên gia", "ISCO 1–2 (skill level 3–4)", ["Managers", "High skill tech staff", "Accountants", "IT staff"],
                             "Công việc đòi hỏi trình độ đại học trở lên"),
    "technician_clerical": ("Kỹ thuật viên & Văn phòng", "ISCO 3–4 (skill level 2–3)", ["Core staff", "Medicine staff", "Secretaries", "HR staff", "Realty agents"],
                            "Medicine staff gồm cả bác sĩ (ISCO 2) lẫn điều dưỡng (ISCO 3) -> xếp mức trung gian – giả định"),
    "service_sales": ("Dịch vụ & Bán hàng", "ISCO 5 (skill level 2)", ["Sales staff", "Cooking staff", "Waiters/barmen staff", "Private service staff", "Security staff"],
                      "Nhân viên dịch vụ cá nhân, bán hàng, bảo vệ (ISCO 5414)"),
    "manual_elementary": ("Lao động phổ thông & Lái xe", "ISCO 7–9 (skill level 1–2)", ["Laborers", "Low-skill Laborers", "Drivers", "Cleaning staff"],
                         "Lao động chân tay; gộp ISCO 7–9 để nút có ≤ 5 trạng thái"),
    "unknown": ("Không khai báo", "–", ["<NA>"], "OCCUPATION_TYPE bị thiếu (31%), phần lớn là người hưu trí – giữ thành trạng thái riêng, không impute"),
}

def write(name, groups, src, col):
    out = ROOT / "knowledge_base" / name
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([col, "group", "group_vi", "standard_code", "rationale", "source_url"])
        for g, (vi, code, vals, why) in groups.items():
            for v in vals:
                w.writerow([v, g, vi, code, why, src])
    print("wrote", out)

write("sector_mapping.csv", SECTORS, ISIC, "ORGANIZATION_TYPE")
write("occupation_mapping.csv", OCCUPATIONS, ISCO, "OCCUPATION_TYPE")

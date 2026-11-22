"""Prompt diễn giải kết quả BN + lời khuyên mẫu (template, không cần LLM)."""
from __future__ import annotations

import json

SYSTEM = """Bạn là trợ lý tư vấn tài chính cá nhân, diễn giải kết quả của một Mạng Bayes chấm điểm tín dụng.
QUY TẮC BẮT BUỘC:
1. Chỉ dùng các con số có trong DỮ KIỆN. Không tự tính, không ước lượng, không làm tròn khác đi, không bịa xác suất mới.
2. Không suy diễn nguyên nhân ngoài các yếu tố được liệt kê. Không nhắc tới giới tính, dân tộc, tôn giáo.
3. Viết tiếng Việt, ngắn gọn (≤ 220 từ), giọng tôn trọng, dễ hiểu với người không chuyên.
4. Cấu trúc đúng 4 mục có tiêu đề in đậm: **Tóm tắt**, **Yếu tố chính**, **Nên làm gì**, **Lưu ý**.
5. Mục "Nên làm gì" chỉ dựa trên `ke_hoach` (hoặc `khong_dat_muc_tieu`) và `what_if` trong dữ kiện.
6. Mục "Lưu ý" nói rõ đây là mô hình minh họa học từ dữ liệu công khai, không phải quyết định cho vay."""


def user_prompt(facts: dict) -> str:
    return ("DỮ KIỆN (do Mạng Bayes tính, JSON):\n" + json.dumps(facts, ensure_ascii=False, indent=1) +
            "\n\nHãy viết lời khuyên theo đúng quy tắc.")


def template_advice(f: dict) -> str:
    """Lời khuyên tất định từ dữ kiện (dự phòng khi không có LLM; cũng là mốc so sánh)."""
    lines = ["**Tóm tắt**",
             f"Điểm tín dụng ước tính của bạn là {f['diem']} (thang {f['thang_diem']}), mức \"{f['muc_rui_ro']}\". "
             f"Xác suất vỡ nợ ước tính {f['xac_suat_vo_no_pct']}%, so với trung bình quần thể "
             f"{f['xac_suat_vo_no_trung_binh_quan_the_pct']}%.", "", "**Yếu tố chính**"]
    for c in f["yeu_to_keo_diem_xuong"]:
        lines.append(f"- {c['label']} ({c['state']}) kéo điểm xuống {abs(c['points'])} điểm.")
    for c in f["yeu_to_giup_diem"]:
        lines.append(f"- {c['label']} ({c['state']}) giúp tăng {c['points']} điểm.")
    if f["bien_chua_biet"]:
        lines.append(f"- Chưa có thông tin: {', '.join(f['bien_chua_biet'])} (mô hình đã tính trung bình theo xác suất).")
    lines += ["", "**Nên làm gì**"]
    if f.get("ke_hoach"):
        k = f["ke_hoach"][0]
        lines.append(f"Để đạt {f['muc_tieu_diem']} điểm, phương án ít thay đổi nhất: " + "; ".join(k["thay_doi"]) +
                     f" (điểm dự kiến {k['diem_dat_duoc']}).")
    elif f.get("khong_dat_muc_tieu"):
        k = f["khong_dat_muc_tieu"]
        lines.append(f"Chưa thể đạt {f['muc_tieu_diem']} điểm chỉ bằng các thay đổi trong tầm tay; tốt nhất đạt "
                     f"{k['diem_toi_da']} điểm khi: " + "; ".join(k["thay_doi"]) + ".")
    else:
        lines.append("Bạn đang ở mức rủi ro thấp nhất; hãy duy trì trả nợ đúng hạn.")
    for lab, w in f.get("what_if", {}).items():
        lines.append(f"- Nếu gặp \"{lab}\", điểm có thể giảm còn {w['diem_moi']} ({w['thay_doi']} điểm): nên có quỹ dự phòng.")
    lines += ["", "**Lưu ý**", "Đây là mô hình minh họa học từ dữ liệu công khai (Home Credit) và tri thức vĩ mô Việt Nam, "
              "không phải quyết định cho vay hay tư vấn tài chính chính thức."]
    return "\n".join(lines)

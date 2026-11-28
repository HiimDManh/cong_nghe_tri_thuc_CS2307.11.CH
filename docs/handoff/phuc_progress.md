# Tiến độ phần việc của Phúc (branch `Phuc`)

> Cập nhật: **28/11/2026**.
> Phạm vi file chạm tới: `data/samples/profiles.csv`, `reports/chapters/05_he_thong.md`, `reports/figures/demo_01..06_*.png`, `docs/handoff/{samples_for_rating_phuc.csv,phuc_slides_draft.md,phuc_progress.md}`.
> Tuân thủ quy tắc: **không** sửa `src/`, `configs/`, `knowledge_base/*.csv`, `models/`, `experiments/`, `reports/report.md`; **không** tự gõ số thực nghiệm vào Chương 5 (100% dùng placeholder `{{num:…}}`, `{{table:llm}}`, `{{fig:demo_…}}`).

## Checklist công việc của Phúc (theo `docs/HANDOFF.md`)
| Việc | File bàn giao | Hạn | Trạng thái |
|---|---|---|---|
| API key Groq / Gemini | gửi tin nhắn riêng cho Mạnh (không đưa vào repo) | 24/11 | ✅ xong (Groq đã gửi 24/11; đã tạo thêm Gemini key 27/11) |
| Bộ ~50 hồ sơ mẫu đa dạng | `data/samples/profiles.csv` | 27/11 | ✅ xong (**54 hồ sơ**: 6 mẫu gốc + 48 mẫu mới; đủ ≥5 mẫu/ngành × 9 ngành, 6 mẫu `working=no`, tuổi 20–70, thu nhập hộ 5–80 triệu, 11 mẫu DSTI ≥40%, 12 mẫu không nợ, 15 mẫu có 3–6 ô trống; đã test chạy qua `BN-Expert-Mono` + `FicoScorer` + `faithfulness` 100% không lỗi) |
| Viết Chương 5 + chụp 6 màn hình demo | `reports/chapters/05_he_thong.md` + `reports/figures/demo_01..06_*.png` | 29/11 | ✅ xong đủ 4 mục (5.1–5.4) + 6 ảnh nền sáng rõ nét; kiểm tra `render()` 0 placeholder thiếu (còn chờ điền link sau khi deploy ở cuối mục 5.4) |
| Chấm tay lời khuyên LLM (`profile` 30–44 + 45–49) | `docs/handoff/samples_for_rating_phuc.csv` | 30/11 | ✅ xong đủ **60 dòng** (`nguoi_cham = Phúc`, mọi dòng có `dung_du_kien_1_5 ≤ 3` đều trích nguyên văn câu sai vào `ghi_chu`) |
| Nội dung Slide 1–3, 16–18 & khung ghép 18 slide | `docs/handoff/phuc_slides_draft.md` | 01/12 | ✅ xong bản thảo chi tiết + lời thoại Slide 16–17; chờ nhận phần của Nam & Khôi để ghép ra `.pptx`/`.pdf` (gửi ngoài Git) |
| Tài khoản Streamlit Cloud & cùng Mạnh deploy | `docs/DEPLOY.md` | 28/11 | ⏳ sẵn sàng phối hợp cùng Mạnh |

## Tóm tắt kết quả chấm tay 60 dòng LLM của Phúc (`profile` 30–49)
- `template`: Đúng dữ kiện **5,00** · Dễ hiểu **4,00** · Hữu ích **4,05** (0/20 bài ≤ 3 điểm).
- `groq:qwen3.8-27b`: Đúng dữ kiện **4,70** · Dễ hiểu **4,95** · Hữu ích **4,75** (chỉ 1/20 bài bị 3 điểm ở `profile 46` do bỏ sót thông tin `khong_dat_muc_tieu` tối đa đạt 667 < 670).
- `groq:gpt-oss-120b`: Đúng dữ kiện **2,30** · Dễ hiểu **3,70** · Hữu ích **3,95** (17/20 bài ≤ 3 điểm: ngoài lỗi tự cộng/trừ điểm ở các `profile` 35, 37, 38, 42, 44, 48 còn phát hiện lỗi ngữ nghĩa tự gắn đơn vị `%` / `% vốn` / `% thu nhập` vào `chi_phi` và nhầm đối tượng so sánh rủi ro nhóm).

## Ghi chú kỹ thuật phát hiện khi chạy Demo (nhờ Mạnh cập nhật trước khi deploy, Phúc không tự sửa `configs/` và `src/`)
1. Trong `configs/llm.yaml`, model `gemini-2.5-flash` hiện trả về **HTTP 404** đối với API key mới tạo (*"This model models/gemini-2.5-flash is no longer available to new users"*). Đổi sang **`gemini-3.5-flash-lite`** chạy rất nhanh (~1,5–2 giây) và đạt `faithful = True` (100% khớp số & bao phủ).
2. Trong `src/llm/client.py` (dòng 110–111), với các model Gemini 3.x có thể trả thêm phần suy nghĩ (`"thought": true`) trong `parts`, nên lọc `"".join(x.get("text", "") for x in parts if not x.get("thought")).strip()` để tránh nối nhầm token suy nghĩ vào lời khuyên.

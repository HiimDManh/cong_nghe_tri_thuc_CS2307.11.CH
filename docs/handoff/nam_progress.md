# Tiến độ phần việc của Nam (branch `Nam`)

> File để mở lại phiên sau: biết đã xong gì, bắt đầu từ đâu. Cập nhật lần cuối: **25/11/2026**.
> Phạm vi được sửa: `reports/chapters/02_tri_thuc.md`, `docs/handoff/*`. Không sửa `src/`, `configs/`, `knowledge_base/*.csv`, `models/`, `experiments/`. Không tự gõ số vào báo cáo.

## Git
- Branch `Nam` (tách từ `main` tại `8090424`). **Chưa push.** Mạnh là owner, quyết định merge.
- Commit `b1509ce`: bản đầu của `nam_source_verification.csv`. Các cập nhật sau đó (dòng 1–5 đầy đủ, `TASKS.md`, file này) **chưa commit** – kiểm tra bằng `git status`.

## Checklist (theo `docs/HANDOFF.md`)
| Việc | Hạn | Trạng thái |
|---|---|---|
| Đối chiếu 4 nguồn (UK LTI, Pháp DSTI, Estonia DSTI, lạm phát VN) → `nam_source_verification.csv` | 25/11 | ✅ xong |
| (COULD) Thu nhập theo ngành VN 2024 (GSO) | 26/11 | ✅ xong (Biểu 3.4, 3.5) |
| Gửi kết quả đối chiếu cho Mạnh (file/PR) | 25/11 | ⬜ chờ commit + push/gửi |
| Viết Chương 2 `reports/chapters/02_tri_thuc.md` (2.1–2.4) | 28/11 | ⬜ chưa bắt đầu |
| ≥ 8 câu hỏi phản biện (cùng Khôi), cuối `docs/handoff/slides_outline.md` hoặc tin nhắn | 29/11 | ⬜ |
| Chấm tay LLM hồ sơ 0–14 và 45–49 (`experiments/llm_faithfulness/samples_for_rating.csv`, rubric `llm_rating_rubric.md`) | 30/11 | ⬜ |
| Slide 4–6 (nguồn tri thức, DAG, CPT tri thức + giả định) | 01/12 | ⬜ |

## Kết quả đối chiếu nguồn (tóm tắt; chi tiết trong CSV)
- UK: LTI ≥ 4,5 tối đa 15% số hợp đồng vay mới – FCA FG14/8 (01/10/2014) và FG17/2 (02/2017). ✅
- Pháp: DSTI ("taux d'effort") ≤ 35% – HCSF D-HCSF-2021-7, 29/09/2021, hiệu lực 01/01/2022, Điều 1(i). ✅
- Estonia: DSTI ≤ 50%, ngoại lệ 15% mỗi quý – Decree No. 17, bản hiện hành hiệu lực 16/06/2025, §4(2), §6. ✅
- Việt Nam: CPI 2026 bình quân khoảng **4,5%** – NQ 244/2025/QH15 (13/11/2025), Điều 2 khoản 4. Repo đang dùng 4% → **báo Mạnh**.
- Thu nhập theo ngành 2024: GSO, Báo cáo điều tra lao động việc làm 2024, Biểu 3.4 (trang 37 sách / trang 38 PDF), nghìn đồng/tháng, lao động làm công ăn lương.

## Lưu ý còn mở
- Chưa mở PDF quyết định HCSF 2023 (D-HCSF-2023-2, 2023-6); không đổi con số 35%/20%.
- File `.doc` nghị quyết là bản sao thuvienphapluat.vn, không phải Công báo.
- ĐỪNG sửa config. Câu hỏi cho Mạnh: giữ ngưỡng lạm phát 4% (bỏ chữ "mục tiêu") hay đổi 4,5%?

## Bắt đầu phiên sau từ đâu
1. `git status` trên branch `Nam`; commit các thay đổi còn lại; hỏi Nam trước khi push.
2. Soạn nháp Chương 2 từ `knowledge_base/README.md`, `reports/bn/expert_params.md`, `reports/eda/bn_expert_edge_support.md`, `configs/bn_expert.yaml` (chỉ đọc) và kết quả CSV ở trên.
3. Máy chưa có Python/venv; poppler đã cài (`winget`, 25/11) – khởi động lại app để công cụ Read đọc PDF theo trang.

# Tiến độ phần việc của Nam (branch `Nam`)

> File để mở lại phiên sau: biết đã xong gì, bắt đầu từ đâu. Cập nhật lần cuối: **25/11/2026**.
> Phạm vi được sửa: `reports/chapters/02_tri_thuc.md`, `docs/handoff/*`. Không sửa `src/`, `configs/`, `knowledge_base/*.csv`, `models/`, `experiments/`. Không tự gõ số vào báo cáo.

## Git
- Branch `Nam` (tách từ `main` tại `8090424`). **Chưa push** (ahead `origin/Nam` 3 commit trước lượt này). Mạnh là owner, quyết định merge.
- Đã commit: đối chiếu nguồn (`b1509ce`, `e577a75`), nháp Chương 2 (`ddd0a29`). Lượt 25/11 viết lại văn phong Chương 2 và sửa file này, **chưa commit**.

## Checklist (theo `docs/HANDOFF.md`)
| Việc | Hạn | Trạng thái |
|---|---|---|
| Đối chiếu 4 nguồn (UK LTI, Pháp DSTI, Estonia DSTI, lạm phát VN) → `nam_source_verification.csv` | 25/11 | ✅ xong |
| (COULD) Thu nhập theo ngành VN 2024 (GSO) | 26/11 | ✅ xong (Biểu 3.4, 3.5) |
| Gửi kết quả đối chiếu cho Mạnh (file/PR) | 25/11 | ⬜ đã commit, chờ push/gửi |
| Viết Chương 2 `reports/chapters/02_tri_thuc.md` (2.1–2.4) | 28/11 | ✅ nháp đủ 4 mục, đã viết lại giọng văn và đối chiếu với `expert_params.md` + `knowledge_base/README.md` (25/11); còn chờ Mạnh duyệt |
| ≥ 8 câu hỏi phản biện (cùng Khôi), cuối `docs/handoff/slides_outline.md` hoặc tin nhắn | 29/11 | ⬜ |
| Chấm tay LLM hồ sơ 0–14 và 45–49 (`experiments/llm_faithfulness/samples_for_rating.csv`, rubric `llm_rating_rubric.md`) | 30/11 | ⬜ |
| Slide 4–6 (nguồn tri thức, DAG, CPT tri thức + giả định) | 01/12 | ⬜ |

## Kết quả đối chiếu nguồn (tóm tắt; chi tiết trong CSV)
- UK: LTI ≥ 4,5 tối đa 15% số hợp đồng vay mới, FCA FG14/8 (01/10/2014) và FG17/2 (02/2017). ✅
- Pháp: DSTI ≤ 35%, HCSF D-HCSF-2021-7, 29/09/2021, hiệu lực 01/01/2022, Điều 1(i). ✅
- Estonia: DSTI ≤ 50%, ngoại lệ 15% mỗi quý, Decree No. 17, bản hiện hành hiệu lực 16/06/2025, §4(2), §6. ✅
- Việt Nam: CPI 2026 bình quân khoảng **4,5%**, NQ 244/2025/QH15 (13/11/2025), Điều 2 khoản 4. Repo đang dùng 4% → **báo Mạnh**.
- Thu nhập theo ngành 2024: GSO, Báo cáo điều tra lao động việc làm 2024, Biểu 3.4 (trang 37 sách / trang 38 PDF), nghìn đồng/tháng, lao động làm công ăn lương.

## Sai lệch phát hiện khi đối chiếu Chương 2 (25/11)
Đã sửa trong Chương 2 (nguồn là `expert_params.md`):
- Hệ số đệm tài chính theo ngũ phân vị có nguồn (GSO KSMS 2024 Biểu 4 & 11); nháp cũ ghi nhầm là giả định. Phần giả định là hệ số tài sản (`none/car/realty/both`).
- Hệ số ngành của mất việc là proxy tính từ Home Credit (thâm niên < 1 năm theo ngành), không phải giả định thuần và không phải số liệu VN. Hệ số thâm niên là giả định.
- Nháp cũ thiếu: thất nghiệp nền (World Bank, có nguồn), hệ số thời hạn, tham số chi phí sinh hoạt và hụt dòng tiền (giả định).

Cần Mạnh xử lý (ngoài phạm vi Nam, không tự sửa):
- `knowledge_base/README.md` dòng 11 vẫn ghi nguồn ngưỡng nợ là "FCA, ECB, Bank of Finland" và dòng 20 "Nam đối chiếu bản gốc"; thực tế đã đối chiếu xong, nguồn gốc là FCA, HCSF, Eesti Pank.
- README dòng 21 nói thu nhập theo ngành "chưa trích được tự động"; Nam đã trích tay Biểu 3.4/3.5.
- `debt_threshold_sources.csv`: cột `verification` cần cập nhật theo `nam_source_verification.csv`.
- Ngưỡng lạm phát: giữ 4% (bỏ chữ "mục tiêu") hay đổi 4,5%?

## Lưu ý còn mở
- Chưa mở PDF quyết định HCSF 2023 (D-HCSF-2023-2, 2023-6); không đổi con số 35%/20%.
- File `.doc` nghị quyết là bản sao thuvienphapluat.vn, không phải Công báo.
- Số nút trong Chương 2 (14 dữ liệu, 6 chuyên gia) đã khớp `configs/bn_expert.yaml`.
- ĐỪNG sửa config.

## Bắt đầu phiên sau từ đâu
1. `git status` trên branch `Nam`; commit; hỏi Nam trước khi push rồi báo Mạnh.
2. Soạn ≥ 8 câu hỏi phản biện (29/11), chấm LLM (30/11), slide 4–6 (01/12).
3. Máy chưa có Python/venv; poppler đã cài (`winget`, 25/11).

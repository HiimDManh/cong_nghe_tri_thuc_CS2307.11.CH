# Bàn giao cho Nam, Khôi, Phúc (22/11/2026)

**Hạn nộp & báo cáo: 02/12/2026.** Phần kỹ thuật (code, dữ liệu, mô hình, thí nghiệm, demo, LLM) đã xong và do Mạnh
giữ. Việc của ba bạn **không sinh code hay số liệu mới** để tránh lệch giữa các công cụ AI khác nhau.

## 1. Quy tắc chung (bắt buộc)
1. **Không sửa** `src/`, `configs/`, `knowledge_base/*.csv`, `models/`, `experiments/`. Thấy sai → ghi lại gửi Mạnh.
2. **Không tự gõ số** vào báo cáo/slide. Số chỉ lấy từ:
   - `reports/results_summary.md` – mọi bảng kết quả (đọc file này trước tiên),
   - `reports/results/key_numbers.json` – số chính có tên; trong chương báo cáo viết `{{num:<tên>}}`,
     ví dụ `{{num:auc.BN-Expert-Mono}}`, script sẽ tự điền,
   - `reports/results/<bảng>.md` – chèn nguyên bảng bằng `{{table:<bảng>}}`, hình bằng `{{fig:<file>.png|chú thích}}`.
3. Dùng AI (Gemini, ChatGPT, Codex…) để **viết văn** thì được, nhưng phải dán kèm nội dung `results_summary.md` và dặn
   AI: *"chỉ dùng số có trong tài liệu, không suy diễn số mới"*. Đọc lại và đối chiếu từng số trước khi gửi.
4. Báo cáo trung thực: ML hộp đen **phân biệt tốt hơn** BN về AUC – không viết né. Giá trị của BN nằm ở các tiêu chí
   khác (xem mục 3).
5. **Bảo mật:** API key chỉ gửi riêng cho Mạnh (tin nhắn riêng), không dán vào chat nhóm, repo, slide, ảnh chụp.
   Không dùng thông tin cá nhân thật trong hồ sơ mẫu.
6. Gửi sản phẩm cho Mạnh (file đính kèm hoặc Pull Request chỉ chạm `reports/chapters/<chương của mình>.md` và
   `docs/handoff/*`). Mạnh commit và chạy `python -m src.cli report` để ghép báo cáo.

## 2. Đọc gì trước (30 phút)
| Thứ tự | File | Để làm gì |
|---|---|---|
| 1 | `reports/results_summary.md` | Toàn bộ kết quả thực nghiệm (bảng + hình) |
| 2 | `reports/chapters/01_gioi_thieu.md`, `03_mo_hinh.md` | Bài toán, khác biệt với FICO, phương pháp (Mạnh đã viết) |
| 3 | `reports/chapters/04_thuc_nghiem.md` | Phần kết quả chính (Mạnh viết sẵn, Khôi viết thảo luận) |
| 4 | `knowledge_base/README.md`, `reports/bn/expert_params.md` | Nguồn tri thức và tham số |
| 5 | Chương của mình (mục 4) | Khung + gợi ý trong các ô `<!-- Gợi ý -->` |

## 3. Kết quả chính (tóm tắt – số đầy đủ ở `reports/results_summary.md`)
Xem mục "Kết quả chính" trong `reports/chapters/04_thuc_nghiem.md` (số được điền tự động từ thí nghiệm).

## 4. Việc của từng người

### Nam – Kiểm chứng tri thức & chương 2
| Việc | File | Hạn |
|---|---|---|
| Đối chiếu **bản gốc** 4 nguồn còn ghi "cần đối chiếu" (FCA LTI 4,5; HCSF DSTI 35%; Estonia DSTI 50%; mục tiêu lạm phát VN ~4%): tìm văn bản gốc, ghi số hiệu, ngày, trang/điều, trích nguyên văn | `docs/handoff/nam_source_verification.csv` | 25/11 |
| (Nếu kịp) Thu nhập bình quân theo ngành kinh tế VN 2024 (GSO, báo cáo lao động việc làm): bảng số + URL + trang | cùng file, dòng 5 | 26/11 |
| Viết **Chương 2 – Thu thập & biểu diễn tri thức** | `reports/chapters/02_tri_thuc.md` | 28/11 |
| Đọc bảng kết quả, đặt ≥ 8 câu hỏi phản biện như hội đồng (cùng Khôi) | gửi tin nhắn / thêm cuối `docs/handoff/slides_outline.md` | 29/11 |
| Chấm tay lời khuyên LLM (hồ sơ 0–14 + 45–49) | `docs/handoff/llm_rating_rubric.md` | 30/11 |
| Trình bày slide 4–6 | `docs/handoff/slides_outline.md` | 01/12 |

### Khôi – QA demo, chương 4 (thảo luận), slide
| Việc | File | Hạn |
|---|---|---|
| Kiểm thử demo theo checklist, ghi lỗi | `docs/handoff/khoi_qa_checklist.md` → `docs/handoff/khoi_qa_bugs.csv` | 27/11 (vòng 1), 30/11 (vòng 2) |
| Viết phần **Thảo luận** của Chương 4 (các ô `<!-- Khôi: … -->`) – giải thích *vì sao* từng kết quả xảy ra, không lặp lại số | `reports/chapters/04_thuc_nghiem.md` | 29/11 |
| Câu hỏi phản biện (cùng Nam) | như trên | 29/11 |
| Dựng slide 9–15 từ hình có sẵn | `docs/handoff/slides_outline.md` | 01/12 |
| Chấm tay LLM (hồ sơ 15–29 + 45–49) | rubric | 30/11 |

### Phúc – Hồ sơ mẫu, tài khoản, chương 5, slide
| Việc | File | Hạn |
|---|---|---|
| Tạo **API key Gemini (miễn phí)** và **Groq (miễn phí)** → gửi riêng Mạnh | (không ghi vào file nào) | **24/11** |
| Tài khoản **Streamlit Community Cloud** (đăng nhập GitHub) hoặc HF Spaces; cùng Mạnh deploy | `docs/DEPLOY.md` | 28/11 |
| Thêm ~45 hồ sơ mẫu đa dạng | `docs/handoff/phuc_profiles_spec.md` → `data/samples/profiles.csv` | 27/11 |
| Viết **Chương 5 – Hệ thống & demo** + chụp ảnh 6 tab demo (`reports/figures/demo_*.png`) | `reports/chapters/05_he_thong.md` | 29/11 |
| Dựng slide 1–3, 16–18; ghép toàn bộ slide | `docs/handoff/slides_outline.md` | 01/12 |
| Chấm tay LLM (hồ sơ 30–44 + 45–49) | rubric | 30/11 |

### Mạnh (+ Claude) – giữ phần kỹ thuật
- Khi có key (24/11): chạy `python -m src.cli llm` với Gemini/Groq → gửi file chấm tay cho cả nhóm.
- Nhận hồ sơ mẫu, lỗi QA, kết quả đối chiếu nguồn → sửa code/tri thức, chạy lại thí nghiệm liên quan.
- Viết Chương 1, 3, 6, phần "Kết quả chính" của Chương 4; ghép báo cáo; đóng băng code trưa 01/12.

## 5. Chạy demo trên máy mình (không bắt buộc; không cần dữ liệu Home Credit)
```bash
git clone <repo> && cd src
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r src/app/requirements.txt
streamlit run src/app/streamlit_app.py
```
Không có key → lời khuyên dùng `template` (vẫn đủ để kiểm thử). Có link deploy thì dùng link.

## 6. Mốc thời gian
| Ngày | Mốc |
|---|---|
| 24/11 | Phúc gửi API key (riêng) |
| 25/11 | Nam gửi kết quả đối chiếu nguồn |
| 27/11 | Phúc gửi hồ sơ mẫu; Khôi gửi lỗi QA vòng 1; Mạnh gửi file chấm LLM (Gemini/Groq) |
| 28/11 | Deploy; Nam gửi Chương 2 |
| 29/11 | Khôi, Phúc gửi Chương 4 (thảo luận), 5; câu hỏi phản biện; **tối 29/11 nhóm duyệt bảng kết quả** |
| 30/11 | Chấm tay LLM; QA vòng 2 |
| 01/12 | Trưa: đóng băng code. Tối: slide + tập dượt |
| 02/12 | Nộp & báo cáo |

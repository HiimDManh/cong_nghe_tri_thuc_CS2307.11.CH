# Checklist kiểm thử demo (QA) – Khôi

Chạy demo: xem mục "Chạy demo" trong `docs/HANDOFF.md` (hoặc dùng link deploy khi có).
Ghi mỗi lỗi một dòng vào `docs/handoff/khoi_qa_bugs.csv` (hoặc gửi file đó cho Mạnh). **Không sửa code.**

## A. Nhập liệu (tab đầu, form)
- [x] Nhập đủ mọi trường cho 6 hồ sơ mẫu (sidebar → "Nạp hồ sơ mẫu") → bấm "Tính điểm" → có điểm 300–850, mức rủi ro, xác suất.
- [x] Để **Không rõ** từng trường một (ô "?" hoặc "— Không rõ —") → vẫn ra điểm, "Số trường không rõ" tăng đúng.
- [x] Để Không rõ **tất cả** → ra điểm trung bình quần thể (không lỗi).
- [x] Giá trị biên: tuổi 18 và 90; thu nhập 0; số người trong hộ 1; trả góp > thu nhập (DSTI > 100%); dư nợ rất lớn.
- [x] "Không đi làm" → ngành tự thành "Không đi làm", ô "Mất việc" ở tab What-if bị khóa.
- [x] Thu nhập cá nhân = 0 hoặc Không rõ → DSTI/LTI thành Không rõ (xem expander "Trạng thái BN sau quy đổi").
- [x] Hiển thị tiếng Việt đúng dấu ở mọi nhãn, bảng, đồ thị.

## B. Kết quả
- [x] Bảng so sánh có 3 dòng: BN, FICO (đề tài cũ), XGBoost.
- [x] Biểu đồ "Yếu tố tác động": thanh cam = kéo điểm xuống, xanh = giúp tăng; tổng hợp lý với trực giác (lịch sử tín dụng tốt → xanh).
- [x] Đổi BN-Expert-Mono ↔ BN-Expert ở sidebar → điểm thay đổi nhẹ, không lỗi.
- [x] Tính nhất quán: tăng "Tổng tiền trả góp" (giữ nguyên các trường khác) với BN-Expert-Mono → điểm **không được tăng**. Ghi lại nếu vi phạm.
- [x] Lịch sử trả nợ "Rất kém" → "Rất tốt" → điểm tăng dần (không giảm ở bước nào) với BN-Expert-Mono.

## C. Đồ thị nhân quả
- [x] Hiển thị đủ 20 nút, nút có bằng chứng viền đậm; P(vỡ nợ) ở nút "Vỡ nợ" khớp tab Kết quả.

## D. Suy luận ngược
- [x] Kéo "Điểm mục tiêu" thấp hơn điểm hiện tại → báo "đã đạt".
- [x] Mục tiêu cao vừa phải → có bảng phương án, điểm đạt được ≥ mục tiêu.
- [x] Mục tiêu 800 → cảnh báo "không đạt được", có "tối đa ≈ …".
- [x] Các bảng "Điều kiện cần" với 3 mục tiêu → cột xác suất mỗi bảng cộng ≈ 1.

## E. What-if
- [x] Bật "Mất việc" → điểm giảm; bật thêm "Biến cố sức khỏe" → giảm thêm.
- [x] Chi phí sinh hoạt "Thấp" → điểm tăng nhẹ so với Không rõ.

## F. Lời khuyên (LLM)
- [x] Với "template": có đủ 4 mục **Tóm tắt / Yếu tố chính / Nên làm gì / Lưu ý**; dòng kiểm tra "✅ Trung thành với dữ kiện".
- [ ] Với Gemini/Groq (khi có key): đọc kỹ – có con số nào **không có** trong "Dữ kiện gửi cho LLM (JSON)" không? Có câu nào nói sai hướng không? Ghi lại kể cả khi bộ kiểm tra tự động không bắt được.
- [ ] Ngắt mạng / key sai → demo vẫn chạy, hiện cảnh báo và dùng template (không lộ key trên màn hình).

## G. Tri thức & CPT
- [x] Chọn từng nút tri thức (Lạm phát, Mất việc, …) → có dòng "Nguồn CPT" và bảng CPT.
- [x] Bảng "Khác biệt so với FICO" hiển thị đúng.

## H. Hiệu năng
- [x] Ghi thời gian từ khi bấm "Tính điểm" đến khi có kết quả (mục tiêu < 5 giây); thời gian tạo lời khuyên LLM.

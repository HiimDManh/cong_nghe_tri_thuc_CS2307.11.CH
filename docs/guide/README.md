# Bộ tài liệu hướng dẫn dự án – Project 6: Dự báo khả năng tài chính cá nhân theo ngành nghề

Dành cho cả nhóm (Mạnh, Nam, Khôi, Phúc). Mục tiêu là sau khi đọc, mỗi người có thể:
- giải thích được dự án làm gì, vì sao làm như vậy;
- trả lời câu hỏi của hội đồng về kiến thức nền, mô hình, thực nghiệm, công nghệ;
- tìm đúng file trong repo khi cần trích dẫn.

Bộ tài liệu **không chứa kết quả thực nghiệm**. Số liệu kết quả luôn lấy từ `reports/results_summary.md`, vì file
đó được script sinh lại mỗi khi chạy thí nghiệm. Việc này tránh việc tài liệu ghi một con số còn báo cáo ghi con số
khác.

## Mục lục
| # | Tài liệu | Nội dung | Thời gian đọc |
|---|---|---|---|
| 1 | [01_tong_quan.md](01_tong_quan.md) | Bài toán, kiến trúc tổng thể, luồng dữ liệu, cấu trúc repo, lệnh chạy | 15 phút |
| 2 | [02_kien_thuc_nen.md](02_kien_thuc_nen.md) | Tín dụng & chấm điểm, xác suất, Mạng Bayes, học tham số/cấu trúc, nhân quả do() | 45 phút |
| 3 | [03_du_lieu_tri_thuc.md](03_du_lieu_tri_thuc.md) | Dữ liệu Home Credit/German, đặc trưng, rời rạc hóa, nguồn tri thức, CPT chuyên gia, giả định | 30 phút |
| 4 | [04_mo_hinh_suy_luan.md](04_mo_hinh_suy_luan.md) | BN-Expert 2 lớp, noisy-OR hiệu chỉnh, ràng buộc đơn điệu, suy luận xuôi/ngược – có ví dụ từng bước | 40 phút |
| 5 | [05_thuc_nghiem.md](05_thuc_nghiem.md) | Mô hình so sánh, CV, các chỉ số, kiểm định thống kê, thiết kế 9 thí nghiệm, cách đọc kết quả | 45 phút |
| 6 | [06_llm_demo.md](06_llm_demo.md) | LLM diễn giải, kiểm tra độ trung thành, demo Streamlit, triển khai, bảo mật key | 20 phút |
| 7 | [07_cong_nghe.md](07_cong_nghe.md) | Công nghệ & thư viện, tái lập, kiểm thử, quy ước code/commit | 15 phút |
| 8 | [08_thuat_ngu_hoi_dap.md](08_thuat_ngu_hoi_dap.md) | Bảng thuật ngữ Việt–Anh, câu hỏi hội đồng hay gặp và gợi ý trả lời | 20 phút |

## Lộ trình đọc theo người
| Người | Bắt buộc | Nên đọc |
|---|---|---|
| **Nam** (tri thức, chương 2) | 1, 2 (mục 2.1–2.4), 3, 8 | 4 |
| **Khôi** (QA, thực nghiệm, chương 4) | 1, 2, 4, 5, 8 | 6 |
| **Phúc** (demo, LLM, chương 5) | 1, 4 (mục 4.6–4.8), 6, 7, 8 | 2, 5 |
| **Mạnh** | toàn bộ (để thống nhất câu trả lời khi bảo vệ) | – |

Tài liệu liên quan:
- `docs/HANDOFF.md` – việc của từng người, hạn, quy tắc.
- `docs/TASKS.md` – checklist.
- `Progress.md` – trạng thái hiện tại.
- `docs/DEPLOY.md` – hướng dẫn triển khai.

Khi tài liệu này và code khác nhau, **code và `configs/` là chuẩn**. Báo Mạnh để sửa tài liệu.

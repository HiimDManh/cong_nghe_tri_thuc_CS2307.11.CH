# Rubric chấm tay lời khuyên LLM – Nam, Khôi, Phúc

File chấm: `experiments/llm_faithfulness/samples_for_rating.csv` (mở bằng Excel/Google Sheets, UTF-8).
Bản 24/11 có 3 nguồn cho mỗi hồ sơ: `template`, `groq:gpt-oss-120b`, `groq:qwen3.8-27b` (150 dòng). Chấm theo nội dung; đừng để tên nguồn ảnh hưởng điểm.

**Phân công:** Nam chấm `profile` 0–14 · Khôi 15–29 · Phúc 30–44 · **cả ba cùng chấm 45–49** (để đo độ đồng
thuận; mỗi người thêm dòng riêng với `nguoi_cham` của mình). Mỗi người chấm mọi `provider` của các hồ sơ được giao.
Điền cột `nguoi_cham` = tên bạn. Chấm **độc lập** (không xem điểm của người khác). Gửi lại file cho Mạnh trước **30/11**.

Cột `facts_json` = dữ kiện Mạng Bayes đưa cho LLM – đây là "đáp án" để đối chiếu.

| Tiêu chí | 1 | 3 | 5 |
|---|---|---|---|
| `dung_du_kien_1_5` – Đúng dữ kiện | Có số/khẳng định không có trong dữ kiện, hoặc nói ngược hướng | Đúng nhưng bỏ sót ý quan trọng | Mọi con số & nhận định đều khớp dữ kiện |
| `de_hieu_1_5` – Dễ hiểu | Thuật ngữ khó, rối | Hiểu được nhưng dài/lặp | Ngắn gọn, người không chuyên hiểu ngay |
| `huu_ich_1_5` – Hữu ích | Lời khuyên chung chung, không làm theo được | Có hành động nhưng mơ hồ | Hành động cụ thể, khớp kế hoạch trong dữ kiện |

`ghi_chu`: ghi rõ câu sai (copy nguyên văn) nếu chấm ≤ 3 ở tiêu chí đầu.

Mạnh sẽ tính: điểm trung bình mỗi provider, độ đồng thuận giữa người chấm (trên các hồ sơ chấm chung), và so với
kết quả kiểm tra tự động (`experiments/llm_faithfulness/results.csv`).

<!-- sinh tự động bởi `python -m src.cli eval tables` – không sửa tay -->
**Bảng 10 – Độ trung thành của lời khuyên LLM (kiểm tra tự động)**

| provider           |   number_precision |   fact_coverage |   direction_ok |   faithful |   latency_s |   n |   n_so_ngoai_du_kien |   n_sai_huong |
|:-------------------|-------------------:|----------------:|---------------:|-----------:|------------:|----:|---------------------:|--------------:|
| groq:gpt-oss-120b  |              0.989 |           0.993 |           0.98 |       0.72 |       2.044 |  50 |                   12 |             1 |
| groq:qwen3.8-27b   |              1     |           0.993 |           0.96 |       0.94 |      14.646 |  50 |                    0 |             2 |
| template           |              1     |           1     |           1    |       1    |       0     |  50 |                    0 |             0 |
| template_corrupted |              0.959 |           0.823 |           0.04 |       0    |       0     |  50 |                   48 |            48 |

_number_precision: tỷ lệ con số trong lời khuyên có trong dữ kiện BN cung cấp; fact_coverage: tỷ lệ dữ kiện bắt buộc được nhắc; direction_ok: không nói sai hướng tác động; faithful: đạt cả ba. n_so_ngoai_du_kien / n_sai_huong: số lời khuyên có ≥ 1 con số không có trong dữ kiện / nói sai hướng. template_corrupted: đối chứng âm (cố ý sửa sai). latency_s (giây) gồm cả thời gian chờ khi bị giới hạn tốc độ (HTTP 429) của gói miễn phí → không dùng để so tốc độ model._

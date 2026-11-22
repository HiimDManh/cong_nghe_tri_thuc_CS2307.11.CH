<!-- sinh tự động bởi `python -m src.cli eval tables` – không sửa tay -->
**Bảng 10 – Độ trung thành của lời khuyên LLM (kiểm tra tự động)**

| provider           |   number_precision |   fact_coverage |   direction_ok |   faithful |   latency_s |   n |
|:-------------------|-------------------:|----------------:|---------------:|-----------:|------------:|----:|
| template           |              1     |           1     |           1    |          1 |           0 |  50 |
| template_corrupted |              0.959 |           0.823 |           0.04 |          0 |           0 |  50 |

_number_precision: tỷ lệ con số trong lời khuyên có trong dữ kiện BN cung cấp; fact_coverage: tỷ lệ dữ kiện bắt buộc được nhắc; direction_ok: không nói sai hướng tác động; faithful: đạt cả ba._

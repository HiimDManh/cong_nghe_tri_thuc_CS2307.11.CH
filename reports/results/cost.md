<!-- sinh tự động bởi `python -m src.cli eval tables` – không sửa tay -->
**Bảng 8 – Chi phí tính toán (thí nghiệm 9)**

| Mô hình        | Họ   |   Thời gian học (s) |   Suy luận / 10k hồ sơ (s) |   Số tham số |   Kích thước (KB) |
|:---------------|:-----|--------------------:|---------------------------:|-------------:|------------------:|
| FICO           | rule |               0.602 |                      0.012 |       31     |             2.622 |
| Naive Bayes    | bn   |               0.687 |                      0.034 |      103     |             3.709 |
| BN-Expert      | bn   |               1.035 |                      0.042 |     6989     |           115.926 |
| LR             | ml   |               1.166 |                      0.017 |       31     |             5.381 |
| LR-disc        | ml   |               1.622 |                      0.031 |       67     |             5.122 |
| BN-Hybrid      | bn   |               1.78  |                      0.033 |     4933.07  |            82.992 |
| BN-Learned     | bn   |               2.975 |                      0.033 |      650.667 |            10.599 |
| LightGBM       | ml   |               3.105 |                      0.034 |    23939.1   |           916.91  |
| BN-Expert-Mono | bn   |               5.534 |                      0.044 |     6989     |           115.936 |
| TAN            | bn   |               8.559 |                      0.043 |      519     |             9.127 |
| MLP            | ml   |               9.949 |                      0.021 |     4097     |           108.088 |
| XGBoost-Mono   | ml   |              10.656 |                      0.035 |    42629.7   |          1384.32  |
| XGBoost-disc   | ml   |              10.908 |                      0.047 |    46547.7   |          1476.67  |
| XGBoost        | ml   |              12.954 |                      0.039 |    49073.3   |          1602.25  |
| RF             | ml   |              14.955 |                      0.049 |   381185     |         29865.2   |

_Trung bình trên các fold, ~246k hồ sơ học, CPU 16 luồng. Kích thước = pickle của mô hình đã học (gồm cả tiền xử lý). Số tham số: BN Σ(r−1)·q; cây: số nút; LR: hệ số._

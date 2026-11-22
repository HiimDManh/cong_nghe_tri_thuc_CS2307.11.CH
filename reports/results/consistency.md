<!-- sinh tự động bởi `python -m src.cli eval tables` – không sửa tay -->
**Bảng 6 – Nhất quán với tri thức chuyên gia (thí nghiệm 7)**

% hồ sơ có ít nhất một bước ICE đi ngược hướng tri thức (bước > 0,1 điểm %), 5.000 hồ sơ test × 5 fold

| Mô hình        |   annuity_to_income |   bureau_inquiries_year |   credit_to_income |   ext_score_mean |   income |   years_employed |    TB |   PDP đúng hướng (/6) | Biến không tác động (phẳng)                     |
|:---------------|--------------------:|------------------------:|-------------------:|-----------------:|---------:|-----------------:|------:|----------------------:|:------------------------------------------------|
| FICO           |                0    |                    0    |               0    |             0    |     0    |             0    |  0    |                     6 | income, years_employed                          |
| BN-Expert-Mono |                0    |                    0    |               0    |             0    |     0    |            67.53 | 11.26 |                     3 | bureau_inquiries_year, credit_to_income         |
| LR             |                0    |                    0    |              93.94 |             0    |    99.36 |             0    | 32.22 |                     4 | –                                               |
| BN-Expert      |               92.53 |                    0    |               0    |            31.97 |     0    |            74.12 | 33.1  |                     3 | bureau_inquiries_year, credit_to_income         |
| LR-disc        |                0    |                    6.53 |              99.96 |             0    |    99.92 |             0    | 34.4  |                     2 | –                                               |
| BN-Hybrid      |               94.69 |                    0    |               0    |            32.36 |     0    |            79.79 | 34.47 |                     1 | bureau_inquiries_year, credit_to_income, income |
| XGBoost-Mono   |                0    |                   29.73 |              91.6  |             0    |    85.06 |            23.02 | 38.23 |                     2 | –                                               |
| RF             |               52.58 |                   40.44 |              76.37 |             0.84 |    82.44 |            21.7  | 45.73 |                     4 | –                                               |
| MLP            |               69.69 |                   45.44 |              82.42 |             0    |    82.26 |             5.37 | 47.53 |                     2 | –                                               |
| Naive Bayes    |               85.65 |                    0    |              92    |             0    |    84.85 |            44.32 | 51.14 |                     2 | –                                               |
| XGBoost        |               85.89 |                   36.73 |              88.34 |             1.44 |    82.35 |            28.66 | 53.9  |                     1 | –                                               |
| LightGBM       |               84.61 |                   33.94 |              88.82 |             4.35 |    84.8  |            36.97 | 55.58 |                     2 | –                                               |
| XGBoost-disc   |               86.33 |                   51.15 |              89.39 |             0.5  |    95.11 |            37.65 | 60.02 |                     1 | –                                               |
| TAN            |               92.49 |                   42.99 |              99.98 |             1.22 |    89.87 |            46.41 | 62.16 |                     2 | –                                               |

_Hướng kỳ vọng (tăng biến): annuity_to_income: ↑ rủi ro, credit_to_income: ↑ rủi ro, ext_score_mean: ↓ rủi ro, years_employed: ↓ rủi ro, bureau_inquiries_year: ↑ rủi ro, income: ↓ rủi ro. BN-Expert-Mono / XGBoost-Mono bị ràng buộc đơn điệu ở DSTI & ext_score theo thiết kế (0% ở hai cột đó là do xây dựng, không phải phát hiện). 0% ở biến phẳng (≥ 95% hồ sơ không đổi dự báo khi đổi biến) là KHÔNG có tác động – không phải tuân thủ tri thức; với BN đó là do d-separation khi đã biết các nút cha của Vỡ nợ._

<!-- sinh tự động bởi `python -m src.cli eval tables` – không sửa tay -->
**Bảng 7 – Ổn định giải thích giữa các fold (thí nghiệm 8)**

| Mô hình        |   Spearman cục bộ |   Jaccard top-3 |   Đồng dấu top-3 |   Spearman toàn cục |   MAD đóng góp (log-odds) |
|:---------------|------------------:|----------------:|-----------------:|--------------------:|--------------------------:|
| Naive Bayes    |            0.9873 |          0.9639 |           1      |              0.9879 |                    0.0081 |
| LR             |            0.9776 |          0.9264 |           1      |              0.9791 |                    0.0052 |
| TAN            |            0.9602 |          0.9459 |           1      |              0.9978 |                    0.0249 |
| BN-Expert-Mono |            0.9429 |          0.7955 |           0.9748 |              0.9978 |                    0.0292 |
| BN-Expert      |            0.9407 |          0.745  |           0.9563 |              0.9978 |                    0.0412 |
| XGBoost-Mono   |            0.9109 |          0.8046 |           0.9999 |              0.9813 |                    0.0194 |
| FICO           |            0.9032 |          0.9994 |           0.9999 |              0.8989 |                    0.001  |
| XGBoost        |            0.8878 |          0.769  |           0.999  |              0.9857 |                    0.0227 |
| LightGBM       |            0.8641 |          0.7236 |           0.9984 |              0.9802 |                    0.0248 |

Top-5 nhóm biến quan trọng nhất (TB |đóng góp| trên 2.000 hồ sơ, 5 fold):

| Mô hình        | Top-5                                                                                 |
|:---------------|:--------------------------------------------------------------------------------------|
| BN-Expert      | ext_score_mean, occupation_group, years_employed, annuity_to_income, region_rating    |
| BN-Expert-Mono | ext_score_mean, occupation_group, years_employed, annuity_to_income, income           |
| FICO           | ext_score_mean, age_years, annuity_to_income, credit_to_income, bureau_inquiries_year |
| LR             | ext_score_mean, years_employed, education, annuity_to_income, assets                  |
| LightGBM       | ext_score_mean, years_employed, education, occupation_group, age_years                |
| Naive Bayes    | ext_score_mean, years_employed, occupation_group, age_years, sector                   |
| TAN            | sector, years_employed, ext_score_mean, occupation_group, credit_to_income            |
| XGBoost        | ext_score_mean, years_employed, education, age_years, occupation_group                |
| XGBoost-Mono   | ext_score_mean, annuity_to_income, years_employed, education, age_years               |

Tương quan hạng độ quan trọng toàn cục BN-Expert-Mono vs XGBoost (SHAP): ρ = 0.29.

_Cùng 2.000 hồ sơ cố định, giải thích bởi 5 mô hình học trên 5 fold khác nhau; trung bình trên 10 cặp fold. BN/FICO: đóng góp so với mức phổ biến của quần thể (suy luận chính xác); cây: TreeSHAP; LR: SHAP tuyến tính._

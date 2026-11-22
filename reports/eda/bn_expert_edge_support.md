# Mức ủng hộ của dữ liệu cho từng cạnh BN-Expert (Cramér's V)

_Sinh bởi `python -m src.bn.structure`. Trống = cạnh có nút tri thức (không có dữ liệu)._

| edge                                   |   cramers_v |
|:---------------------------------------|------------:|
| sector → occupation_group              |       0.465 |
| sector → income                        |       0.115 |
| sector → years_employed                |       0.51  |
| sector → job_loss                      |     nan     |
| occupation_group → income              |       0.124 |
| occupation_group → default             |       0.076 |
| education → occupation_group           |       0.238 |
| education → income                     |       0.165 |
| age_years → years_employed             |       0.38  |
| age_years → n_children                 |       0.263 |
| age_years → assets                     |       0.112 |
| age_years → ext_score_mean             |       0.154 |
| age_years → bureau_inquiries_year      |       0.051 |
| age_years → health_shock               |     nan     |
| years_employed → ext_score_mean        |       0.098 |
| years_employed → default               |       0.085 |
| years_employed → job_loss              |     nan     |
| income → assets                        |       0.128 |
| income → annuity_to_income             |       0.204 |
| income → credit_to_income              |       0.136 |
| income → cashflow_shock                |     nan     |
| n_children → living_cost               |     nan     |
| assets → cashflow_shock                |     nan     |
| annuity_to_income → credit_to_income   |       0.444 |
| annuity_to_income → default            |       0.017 |
| ext_score_mean → default               |       0.213 |
| bureau_inquiries_year → ext_score_mean |       0.058 |
| region_rating → income                 |       0.193 |
| region_rating → default                |       0.061 |
| inflation → living_cost                |     nan     |
| econ_cycle → job_loss                  |     nan     |
| job_loss → cashflow_shock              |     nan     |
| health_shock → cashflow_shock          |     nan     |
| living_cost → cashflow_shock           |     nan     |
| cashflow_shock → default               |     nan     |

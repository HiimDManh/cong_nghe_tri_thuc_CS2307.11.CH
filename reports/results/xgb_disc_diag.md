<!-- sinh tự động bởi `python -m src.cli eval tables` – không sửa tay -->
**Bảng 5b – Chẩn đoán XGBoost-disc khi ít dữ liệu (5 fold, seed 42)**

|   fraction | input   | variant              |    auc |   best_iter |   split_nodes |   feasible_cols |   n_features |
|-----------:|:--------|:---------------------|-------:|------------:|--------------:|----------------:|-------------:|
|       0.01 | disc    | as_is (tuned, ES)    | 0.5032 |         184 |           267 |              19 |           64 |
|       0.01 | disc    | H1: tuned, no ES     | 0.5046 |         499 |           463 |              19 |           64 |
|       0.01 | disc    | H2: tuned, mcw=1, ES | 0.7017 |         106 |          3774 |              64 |           64 |
|       0.01 | disc    | untuned (mcw=10), ES | 0.7065 |          74 |          1178 |              57 |           64 |
|       0.01 | cont    | as_is (tuned, ES)    | 0.7026 |         163 |           264 |             nan |           30 |
|       0.01 | cont    | H1: tuned, no ES     | 0.6992 |         499 |           500 |             nan |           30 |
|       0.01 | cont    | H2: tuned, mcw=1, ES | 0.7086 |         113 |          3776 |             nan |           30 |
|       0.01 | cont    | untuned (mcw=10), ES | 0.7125 |          39 |          1068 |             nan |           30 |
|       0.05 | disc    | as_is (tuned, ES)    | 0.7206 |         175 |          1911 |              59 |           65 |
|       0.05 | disc    | H1: tuned, no ES     | 0.7186 |         499 |          3408 |              59 |           65 |
|       0.05 | disc    | H2: tuned, mcw=1, ES | 0.7164 |         110 |          5541 |              64 |           65 |
|       0.05 | disc    | untuned (mcw=10), ES | 0.7143 |          40 |          2278 |              64 |           65 |
|       0.05 | cont    | as_is (tuned, ES)    | 0.7264 |         190 |          2286 |             nan |           30 |
|       0.05 | cont    | H1: tuned, no ES     | 0.7233 |         499 |          3864 |             nan |           30 |
|       0.05 | cont    | H2: tuned, mcw=1, ES | 0.7231 |         143 |          6001 |             nan |           30 |
|       0.05 | cont    | untuned (mcw=10), ES | 0.7234 |          48 |          2368 |             nan |           30 |

_ES = early stopping (100 vòng, val nội bộ 10% train); no ES = 500 cây cố định; mcw = min_child_weight (ngưỡng TỔNG hessian mỗi lá). best_iter, split_nodes: trung vị qua 5 fold; feasible_cols: số cột one-hot mà cả hai nhánh đạt tổng hessian ≥ mcw tại tỷ lệ nền. Chỉ để chẩn đoán – bảng learning curve chính thức giữ nguyên._

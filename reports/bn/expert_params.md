# Tham số lớp tri thức của BN-Expert (sinh tự động bởi `python -m src.cli train`)

| Tham số | Giá trị | Nguồn |
|---|---|---|
| P(inflation) [low, moderate, high] | [0.547, 0.208, 0.245] | World Bank FP.CPI.TOTL.ZG, VN 2000–2024, ngưỡng 4%/8% |
| P(econ_cycle) [normal, downturn] | [0.865, 0.135] | World Bank NY.GDP.MKTP.KD.ZG, VN 2000–2024, ngưỡng 5% (giả định) |
| unemployment base (normal years) | 0.0175 | World Bank SL.UEM.TOTL.ZS, TB các năm 'normal' |
| unemployment multiplier downturn/normal | 1.165 | World Bank, TB downturn / normal |
| sector churn multiplier (proxy) | {"business_unspecified": 1.156, "education_health": 0.597, "finance_professional": 1.444, "industry_construction": 1.135, "other_services_agri": 0.943, "public_admin_security": 0.628, "self_employed": 0.831, "trade_hospitality": 1.525, "transport_postal": 0.884} | Proxy từ Home Credit: tỷ lệ thâm niên < 1 năm theo ngành |
| health shock P(<60), P(>=60) – WHO 2018 | [0.0883, 0.13369999999999999] | WHO GHO SDG 3.8.2 (chi y tế > 10%), VN 2018, theo tuổi |
| income buffer by quintile – GSO 2024 | {"Q1": 1.0, "Q2": 0.769, "Q3": 0.642, "Q4": 0.569, "Q5": 0.418} | GSO KSMS 2024 Biểu 4 & 11: (chi tiêu/thu nhập) nhóm Qk / Q1 |

Tham số GIẢ ĐỊNH (configs/bn_expert_cpt.yaml):

- tenure multiplier: {'<1': 2.0, '1-3': 1.3, '3-7': 1.0, '>=7': 0.6, 'not_working': 0.0}
- horizon multiplier: 2.0
- living_cost: base [0.35, 0.5, 0.15], shift 0.45
- cashflow_shock: leak 0.01, inhibitors {'job_loss': {'yes': 0.6}, 'health_shock': {'yes': 0.35}, 'living_cost': {'high': 0.15, 'normal': 0.03}}, asset buffer {'none': 1.0, 'car': 0.9, 'realty': 0.8, 'both': 0.7}
- default_link λ = 0.3

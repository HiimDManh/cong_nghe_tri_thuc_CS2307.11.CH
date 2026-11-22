"""Quy đổi thông tin người dùng (VND, năm, lựa chọn) -> trạng thái nút BN. Mọi trường đều có thể None
(= "không rõ") -> BN tự lấy biên. Các GIẢ ĐỊNH quy đổi được ghi ở từng hàm và trong demo."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pandas as pd

from src.common import load_config, path


@lru_cache(maxsize=1)
def gso_quintile_bounds() -> list[float]:
    """Ranh giới ngũ phân vị thu nhập bình quân đầu người/tháng (nghìn VND), VN 2024.
    GIẢ ĐỊNH: GSO chỉ công bố trung bình từng nhóm -> ranh giới = trung điểm giữa hai nhóm kề nhau."""
    g = pd.read_csv(path("knowledge_base", "vn_income_spending_quintiles_2024.csv"))
    g = g[(g.area == "national") & (g.indicator == "income_per_capita_month") & (g.quintile != "all")]
    m = g.sort_values("quintile")["value_thousand_vnd"].to_numpy()
    return [(m[i] + m[i + 1]) / 2 for i in range(len(m) - 1)]


def _bin(x: float | None, edges: list[float], labels: list[str]) -> str | None:
    if x is None:
        return None
    for e, lab in zip(edges, labels):
        if x < e:
            return lab
    return labels[-1]


def _spec(name: str) -> dict:
    return load_config("discretize")["features"][name]


@dataclass
class UserInput:
    sector: str | None = None
    occupation_group: str | None = None
    education: str | None = None
    age: float | None = None
    working: bool | None = True
    years_employed: float | None = None
    household_income_m: float | None = None      # thu nhập cả hộ / tháng, triệu VND
    household_size: int | None = None
    personal_income_m: float | None = None       # thu nhập cá nhân / tháng, triệu VND (tính DSTI, LTI)
    n_children: int | None = None
    own_house: bool | None = None
    own_car: bool | None = None
    monthly_installment_m: float | None = None   # tổng trả góp / tháng, triệu VND
    total_debt_m: float | None = None            # tổng dư nợ, triệu VND
    credit_history: str | None = None            # very_poor..very_good (tự đánh giá) – GIẢ ĐỊNH ↔ ngũ phân vị ext_score
    inquiries: str | None = None                 # "0" | "1" | "2-3" | ">=4"
    region: str | None = None                    # "1" | "2" | "3"


def income_quintile(u: UserInput) -> str | None:
    if u.household_income_m is None or not u.household_size:
        return None
    per_capita_k = u.household_income_m * 1000 / u.household_size
    return _bin(per_capita_k, gso_quintile_bounds(), ["Q1", "Q2", "Q3", "Q4", "Q5"])


def to_profile(u: UserInput) -> dict[str, str | None]:
    p: dict[str, str | None] = {"sector": u.sector, "occupation_group": u.occupation_group, "education": u.education}
    a = _spec("age_years")
    p["age_years"] = _bin(u.age, a["edges"], a["labels"])
    if u.working is False:
        p["years_employed"] = "not_working"
        p["sector"] = "not_working"
    else:
        y = _spec("years_employed")
        p["years_employed"] = _bin(u.years_employed, y["edges"], y["labels"])
    p["income"] = income_quintile(u)
    c = _spec("n_children")
    p["n_children"] = _bin(u.n_children, c["edges"], c["labels"])
    if u.own_house is None or u.own_car is None:
        p["assets"] = None
    else:
        p["assets"] = {(False, False): "none", (False, True): "car", (True, False): "realty", (True, True): "both"}[
            (bool(u.own_house), bool(u.own_car))]
    inc = u.personal_income_m
    d = _spec("annuity_to_income")
    p["annuity_to_income"] = (_bin(u.monthly_installment_m / inc, d["edges"], d["labels"])
                              if inc and u.monthly_installment_m is not None else None)
    lt = _spec("credit_to_income")
    p["credit_to_income"] = (_bin(u.total_debt_m / (12 * inc), lt["edges"], lt["labels"])
                             if inc and u.total_debt_m is not None else None)
    p["ext_score_mean"] = u.credit_history
    p["bureau_inquiries_year"] = u.inquiries
    p["region_rating"] = u.region
    return p


def from_row(r: dict) -> UserInput:
    """Hồ sơ mẫu (data/samples/profiles.csv) -> UserInput. Ô trống = không rõ."""
    def f(k, cast=float):
        v = r.get(k)
        return None if v is None or (isinstance(v, float) and pd.isna(v)) or v == "" else cast(v)

    def b(k):
        v = f(k, str)
        return None if v is None else v.strip().lower() in ("1", "true", "yes", "có", "co", "x")

    return UserInput(sector=f("sector", str), occupation_group=f("occupation_group", str), education=f("education", str),
                     age=f("age"), working=b("working"), years_employed=f("years_employed"),
                     household_income_m=f("household_income_m"), household_size=f("household_size", lambda v: int(float(v))),
                     personal_income_m=f("personal_income_m"), n_children=f("n_children", lambda v: int(float(v))),
                     own_house=b("own_house"), own_car=b("own_car"), monthly_installment_m=f("monthly_installment_m"),
                     total_debt_m=f("total_debt_m"), credit_history=f("credit_history", str),
                     inquiries=f("inquiries", str), region=f("region", lambda v: str(int(float(v)))))

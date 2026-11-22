"""Đọc Home Credit `application_train.csv` và tạo đặc trưng nghiệp vụ (chưa rời rạc hóa).

Đặc trưng tạo ra đều có ý nghĩa tài chính, dùng chung cho BN, FICO và ML:
- `sector`, `occupation_group`: ánh xạ ngành/nghề theo knowledge_base/*_mapping.csv
- `income`, `credit_to_income`, `annuity_to_income` (≈ DSTI), `credit_term_months`, `goods_to_credit`
- `age_years`, `years_employed` (NaN nếu không đi làm), `n_children`, `family_size`
- `ext_score_mean` (trung bình EXT_SOURCE_1..3 – điểm tín dụng từ nguồn ngoài, proxy lịch sử tín dụng)
- `bureau_inquiries_year`, `own_realty`, `own_car`, `education`, `region_rating`, `contract_type`

Không dùng thuộc tính nhạy cảm (giới tính, tình trạng hôn nhân) làm đặc trưng.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common import load_config, path

DAYS_EMPLOYED_NOT_WORKING = 365243  # mã đặc biệt của Home Credit cho hưu trí/thất nghiệp

RAW_COLUMNS = [
    "SK_ID_CURR", "TARGET", "ORGANIZATION_TYPE", "OCCUPATION_TYPE", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE",
    "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE", "DAYS_BIRTH", "DAYS_EMPLOYED",
    "CNT_CHILDREN", "CNT_FAM_MEMBERS", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3",
    "AMT_REQ_CREDIT_BUREAU_YEAR", "FLAG_OWN_REALTY", "FLAG_OWN_CAR", "REGION_RATING_CLIENT_W_CITY",
    "NAME_CONTRACT_TYPE", "DEF_30_CNT_SOCIAL_CIRCLE",
]

EDUCATION_MAP = {
    "Lower secondary": "secondary_or_lower",
    "Secondary / secondary special": "secondary_or_lower",
    "Incomplete higher": "incomplete_higher",
    "Higher education": "higher",
    "Academic degree": "higher",
}


def load_raw(nrows: int | None = None) -> pd.DataFrame:
    """Đọc các cột cần thiết của application_train.csv."""
    cfg = load_config("data")
    f = path(cfg["paths"]["raw"], cfg["datasets"]["home_credit"]["raw_file"])
    if not f.exists():
        raise FileNotFoundError(f"Thiếu {f}. Xem README mục Dữ liệu.")
    return pd.read_csv(f, usecols=RAW_COLUMNS, nrows=nrows)


def _mapping(name: str, key: str) -> dict[str, str]:
    m = pd.read_csv(path("knowledge_base", name), keep_default_na=False)
    return dict(zip(m[key], m["group"]))


def build_features(raw: pd.DataFrame) -> pd.DataFrame:
    """Tạo bảng đặc trưng nghiệp vụ liên tục/phân loại + nhãn `default`."""
    df = pd.DataFrame({"id": raw["SK_ID_CURR"], "default": raw["TARGET"].astype(int)})
    df["sector"] = raw["ORGANIZATION_TYPE"].map(_mapping("sector_mapping.csv", "ORGANIZATION_TYPE"))
    df["occupation_group"] = raw["OCCUPATION_TYPE"].fillna("<NA>").map(_mapping("occupation_mapping.csv", "OCCUPATION_TYPE"))
    df["education"] = raw["NAME_EDUCATION_TYPE"].map(EDUCATION_MAP)

    income = raw["AMT_INCOME_TOTAL"]
    df["income"] = income
    df["credit_to_income"] = raw["AMT_CREDIT"] / income
    df["annuity_to_income"] = raw["AMT_ANNUITY"] / income
    df["credit_term_months"] = raw["AMT_CREDIT"] / raw["AMT_ANNUITY"]
    df["goods_to_credit"] = raw["AMT_GOODS_PRICE"] / raw["AMT_CREDIT"]

    df["age_years"] = -raw["DAYS_BIRTH"] / 365.25
    emp = raw["DAYS_EMPLOYED"].where(raw["DAYS_EMPLOYED"] != DAYS_EMPLOYED_NOT_WORKING)
    df["years_employed"] = -emp / 365.25
    df["n_children"] = raw["CNT_CHILDREN"]
    df["family_size"] = raw["CNT_FAM_MEMBERS"]

    ext = raw[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]]
    df["ext_score_mean"] = ext.mean(axis=1)  # NaN chỉ khi thiếu cả 3
    df["bureau_inquiries_year"] = raw["AMT_REQ_CREDIT_BUREAU_YEAR"]
    df["social_circle_def30"] = raw["DEF_30_CNT_SOCIAL_CIRCLE"]
    df["own_realty"] = (raw["FLAG_OWN_REALTY"] == "Y").astype(int)
    df["own_car"] = (raw["FLAG_OWN_CAR"] == "Y").astype(int)
    df["region_rating"] = raw["REGION_RATING_CLIENT_W_CITY"]
    df["contract_type"] = np.where(raw["NAME_CONTRACT_TYPE"] == "Revolving loans", "revolving", "cash")
    return df


def load_features(nrows: int | None = None) -> pd.DataFrame:
    """Tiện ích: đọc raw + tạo đặc trưng."""
    return build_features(load_raw(nrows))

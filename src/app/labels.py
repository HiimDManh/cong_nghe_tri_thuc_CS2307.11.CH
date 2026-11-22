"""Nhãn tiếng Việt cho nút & trạng thái BN (dùng chung cho demo và LLM)."""
from __future__ import annotations

from functools import lru_cache

import pandas as pd

from src.common import load_config, path


@lru_cache(maxsize=1)
def node_vi() -> dict[str, str]:
    return {n: a["label"] for n, a in load_config("bn_expert")["nodes"].items()}


STATE_VI: dict[str, dict[str, str]] = {
    "education": {"secondary_or_lower": "Phổ thông trở xuống", "incomplete_higher": "Đại học chưa xong",
                  "higher": "Đại học trở lên"},
    "age_years": {"<30": "Dưới 30", "30-40": "30–40", "40-50": "40–50", "50-60": "50–60", ">=60": "Từ 60"},
    "years_employed": {"<1": "Dưới 1 năm", "1-3": "1–3 năm", "3-7": "3–7 năm", ">=7": "Từ 7 năm",
                       "not_working": "Không đi làm"},
    "income": {"Q1": "Nhóm 1 (thấp nhất)", "Q2": "Nhóm 2", "Q3": "Nhóm 3", "Q4": "Nhóm 4", "Q5": "Nhóm 5 (cao nhất)"},
    "n_children": {"0": "Không", "1": "1 con", "2": "2 con", ">=3": "Từ 3 con"},
    "assets": {"none": "Không có nhà/xe", "car": "Có xe", "realty": "Có nhà", "both": "Có nhà và xe"},
    "annuity_to_income": {"<10%": "Dưới 10%", "10-20%": "10–20%", "20-30%": "20–30%", "30-40%": "30–40%",
                          ">=40%": "Từ 40%"},
    "credit_to_income": {"<1.5x": "Dưới 1,5 lần", "1.5-3x": "1,5–3 lần", "3-4.5x": "3–4,5 lần",
                         "4.5-7x": "4,5–7 lần", ">=7x": "Từ 7 lần"},
    "ext_score_mean": {"very_poor": "Rất kém", "poor": "Kém", "fair": "Trung bình", "good": "Tốt",
                       "very_good": "Rất tốt"},
    "bureau_inquiries_year": {"0": "0 lần", "1": "1 lần", "2-3": "2–3 lần", ">=4": "Từ 4 lần",
                              "unknown": "Không rõ"},
    "region_rating": {"1": "Vùng 1 (thuận lợi nhất)", "2": "Vùng 2", "3": "Vùng 3 (kém thuận lợi)"},
    "default": {"0": "Không vỡ nợ", "1": "Vỡ nợ"},
    "inflation": {"low": "Thấp (<4%)", "moderate": "Vừa (4–8%)", "high": "Cao (≥8%)"},
    "econ_cycle": {"normal": "Bình thường", "downturn": "Suy giảm"},
    "job_loss": {"no": "Không", "yes": "Có"},
    "health_shock": {"no": "Không", "yes": "Có"},
    "living_cost": {"low": "Thấp", "normal": "Bình thường", "high": "Cao"},
    "cashflow_shock": {"no": "Không", "yes": "Có"},
}


@lru_cache(maxsize=1)
def _mapping_vi() -> dict[str, dict[str, str]]:
    out = {}
    for node, f in (("sector", "sector_mapping.csv"), ("occupation_group", "occupation_mapping.csv")):
        m = pd.read_csv(path("knowledge_base", f), keep_default_na=False).drop_duplicates("group")
        out[node] = dict(zip(m["group"], m["group_vi"]))
    return out


def state_vi(node: str, state: str | None) -> str:
    if state is None:
        return "Không rõ"
    table = STATE_VI.get(node) or _mapping_vi().get(node, {})
    return table.get(str(state), str(state))

"""Sinh CPT cho các nút tri thức (expert) từ knowledge_base/ + configs/bn_expert_cpt.yaml.

Mỗi hàm trả về CPT shape (*card(parents), card(node)) đúng thứ tự `parents` được truyền vào,
nên không phụ thuộc thứ tự cạnh trong YAML. Hàm `provenance()` liệt kê nguồn của từng tham số
để đưa vào báo cáo.
"""
from __future__ import annotations

import itertools
from typing import Callable

import numpy as np
import pandas as pd

from src.common import load_config, path


def _cfg() -> dict:
    return load_config("bn_expert_cpt")


def _tabulate(states: dict[str, list[str]], node: str, parents: list[str],
              fn: Callable[[dict[str, str]], np.ndarray]) -> np.ndarray:
    shape = tuple(len(states[p]) for p in parents) + (len(states[node]),)
    cpt = np.zeros(shape)
    for combo in itertools.product(*[range(len(states[p])) for p in parents]):
        assign = {p: states[p][i] for p, i in zip(parents, combo)}
        v = np.asarray(fn(assign), dtype=float)
        cpt[combo] = v / v.sum()
    return cpt


def _wb(indicator: str, y0: int, y1: int) -> pd.Series:
    m = pd.read_csv(path("knowledge_base", "macro_vn_worldbank.csv"))
    m = m[(m.indicator_code == indicator) & m.year.between(y0, y1)]
    return m.set_index("year")["value"]


def _freq(counts: np.ndarray) -> np.ndarray:
    return (counts + 0.5) / (counts + 0.5).sum()  # làm trơn Jeffreys để không có xác suất 0


def inflation_prior() -> np.ndarray:
    c = _cfg()["inflation"]
    v = _wb(c["indicator"], *c["years"])
    return _freq(np.bincount(np.digitize(v.values, c["edges"]), minlength=3))


def _cycle_years() -> tuple[pd.Series, pd.Series]:
    c = _cfg()["econ_cycle"]
    g = _wb(c["indicator"], *c["years"])
    return g, g < c["downturn_below"]


def econ_cycle_prior() -> np.ndarray:
    _, down = _cycle_years()
    return _freq(np.array([(~down).sum(), down.sum()]))


def unemployment_params() -> tuple[float, float]:
    """(tỷ lệ thất nghiệp nền năm 'normal', hệ số downturn/normal) từ World Bank."""
    c = _cfg()
    u = _wb(c["job_loss"]["base_indicator"], *c["econ_cycle"]["years"])
    _, down = _cycle_years()
    down = down.reindex(u.index).fillna(False).astype(bool)
    base = u[~down].mean() / 100
    return float(base), float(u[down].mean() / u[~down].mean())


def sector_churn(train_feat: pd.DataFrame) -> dict[str, float]:
    """PROXY hệ số mất việc theo ngành: tỷ lệ thâm niên < 1 năm của ngành / toàn bộ người đang làm."""
    w = train_feat[train_feat["years_employed"].notna()]
    overall = (w["years_employed"] < 1).mean()
    s = w.groupby("sector")["years_employed"].apply(lambda x: (x < 1).mean()) / overall
    return s.round(3).to_dict()


def health_by_age() -> tuple[float, float]:
    c = _cfg()["health_shock"]
    h = pd.read_csv(path("knowledge_base", "health_catastrophic_vn_who.csv"))
    h = h[(h.indicator_code == c["indicator"]) & (h.year == c["year"])].set_index("breakdown")["value"]
    return float(h[c["age_lt60"]]) / 100, float(h[c["age_ge60"]]) / 100


def income_buffer() -> dict[str, float]:
    """Hệ số đệm theo ngũ phân vị thu nhập = (chi tiêu/thu nhập của Qk) / (của Q1) – GSO KSMS 2024."""
    g = pd.read_csv(path("knowledge_base", "vn_income_spending_quintiles_2024.csv"))
    g = g[(g.area == "national") & (g.quintile != "all")]
    p = g.pivot(index="quintile", columns="indicator", values="value_thousand_vnd")
    ratio = p["living_expenditure_per_capita_month"] / p["income_per_capita_month"]
    return (ratio / ratio["Q1"]).round(3).to_dict()


def build(states: dict[str, list[str]], parents: dict[str, list[str]], train_feat: pd.DataFrame) -> dict[str, np.ndarray]:
    """CPT của mọi nút expert (trừ `default`, được nối riêng bằng calibrated noisy-OR)."""
    c = _cfg()
    cpts: dict[str, np.ndarray] = {}
    cpts["inflation"] = inflation_prior()
    cpts["econ_cycle"] = econ_cycle_prior()

    base, m_cycle = unemployment_params()
    churn = sector_churn(train_feat)
    jl = c["job_loss"]

    def job_loss(a: dict[str, str]) -> np.ndarray:
        p = base * jl["horizon_multiplier"] * jl["tenure_multiplier"][a["years_employed"]]
        p *= churn.get(a["sector"], 1.0) * (m_cycle if a["econ_cycle"] == "downturn" else 1.0)
        p = min(p, 0.95)
        return np.array([1 - p, p])

    cpts["job_loss"] = _tabulate(states, "job_loss", parents["job_loss"], job_loss)

    h_lt60, h_ge60 = health_by_age()
    cpts["health_shock"] = _tabulate(states, "health_shock", parents["health_shock"],
                                     lambda a: [1 - (h_ge60 if a["age_years"] == ">=60" else h_lt60),
                                                h_ge60 if a["age_years"] == ">=60" else h_lt60])

    lc = c["living_cost"]
    infl_idx = {s: i for i, s in enumerate(states["inflation"])}
    child_idx = {s: i for i, s in enumerate(states["n_children"])}

    def living_cost(a: dict[str, str]) -> np.ndarray:
        s = infl_idx[a["inflation"]] + child_idx[a["n_children"]]
        logits = np.log(lc["base_probs"]) + lc["shift_per_unit"] * s * np.array([-1.0, 0.0, 1.0])
        e = np.exp(logits - logits.max())
        return e / e.sum()

    cpts["living_cost"] = _tabulate(states, "living_cost", parents["living_cost"], living_cost)

    cf = c["cashflow_shock"]
    ib = income_buffer()

    def cashflow(a: dict[str, str]) -> np.ndarray:
        q = 1 - cf["leak"]
        for node, table in cf["inhibitors"].items():
            q *= 1 - table.get(a[node], 0.0)
        p = (1 - q) * ib[a["income"]] * cf["asset_buffer"][a["assets"]]
        return np.array([1 - p, p])

    cpts["cashflow_shock"] = _tabulate(states, "cashflow_shock", parents["cashflow_shock"], cashflow)
    return cpts


def provenance(train_feat: pd.DataFrame) -> dict[str, object]:
    """Các tham số đã dùng + nguồn – in vào báo cáo."""
    base, m_cycle = unemployment_params()
    h = health_by_age()
    return {
        "P(inflation) [low, moderate, high]": inflation_prior().round(3).tolist(),
        "P(econ_cycle) [normal, downturn]": econ_cycle_prior().round(3).tolist(),
        "unemployment base (normal years)": round(base, 4),
        "unemployment multiplier downturn/normal": round(m_cycle, 3),
        "sector churn multiplier (proxy)": sector_churn(train_feat),
        "health shock P(<60), P(>=60) – WHO 2018": h,
        "income buffer by quintile – GSO 2024": income_buffer(),
    }

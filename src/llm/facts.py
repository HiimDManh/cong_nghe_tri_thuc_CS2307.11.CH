"""Dữ kiện (facts) do BN tính ra cho một hồ sơ – đầu vào DUY NHẤT của LLM.

LLM không tự tính xác suất: mọi con số (điểm, xác suất, đóng góp, what-if, kế hoạch phản thực) đều do BN
tính ở đây; LLM chỉ diễn đạt thành lời khuyên tiếng Việt. Bộ kiểm tra độ trung thành (faithfulness.py)
đối chiếu con số trong lời khuyên với chính các dữ kiện này.
"""
from __future__ import annotations

import pandas as pd

from src.app.labels import node_vi, state_vi
from src.bn.backward import counterfactual_search
from src.bn.core import DiscreteBN
from src.bn.model import risk_band, to_score
from src.common import load_config

INPUTS = ["sector", "occupation_group", "education", "age_years", "years_employed", "income", "n_children",
          "assets", "annuity_to_income", "credit_to_income", "ext_score_mean", "bureau_inquiries_year",
          "region_rating"]


def _p(bn: DiscreteBN, ev: dict[str, str]) -> float:
    return float(bn.predict_proba(pd.DataFrame([ev]) if ev else pd.DataFrame(index=[0]))[0])


def contributions(bn: DiscreteBN, profile: dict[str, str]) -> list[dict]:
    """Đóng góp (điểm) của từng biến đã biết so với MỨC PHỔ BIẾN: điểm(hồ sơ) − Σ_s P(biến=s)·điểm(hồ sơ, biến=s),
    P(biến=s) là phân phối biên của quần thể (từ BN). Một lần suy luận theo lô cho mọi biến/trạng thái."""
    nodes = [n for n in INPUTS if profile.get(n) is not None]
    marg = {n: bn.query(pd.DataFrame(index=[0]), n)[0] for n in nodes}
    rows, key = [dict(profile)], [(None, None)]
    for n in nodes:
        for s in bn.states[n]:
            rows.append({**profile, n: s})
            key.append((n, s))
    sc = to_score(bn.predict_proba(pd.DataFrame(rows)))
    s0 = float(sc[0])
    out = []
    for n in nodes:
        ref = sum(marg[n][bn.states[n].index(s)] * sc[i] for i, (m, s) in enumerate(key) if m == n)
        out.append({"node": n, "label": node_vi()[n], "state": state_vi(n, profile[n]), "points": round(s0 - ref)})
    return sorted(out, key=lambda r: r["points"])


def next_target(score: float) -> int | None:
    for b in sorted(load_config("bn_expert_cpt")["scoring"]["risk_bands"], key=lambda b: b["min"]):
        if b["min"] > score + 1:
            return int(b["min"])
    return None


def build_facts(bn: DiscreteBN, profile: dict[str, str], target_score: int | None = None,
                others: dict[str, float] | None = None) -> dict:
    """Tập dữ kiện gọn (JSON-able) cho một hồ sơ. `others`: điểm của mô hình khác (FICO, XGBoost) nếu có."""
    profile = {k: v for k, v in profile.items() if v is not None and k != "default"}
    p = _p(bn, profile)
    score = float(to_score(p))
    pop = _p(bn, {})
    contrib = contributions(bn, profile)
    facts: dict = {
        "diem": round(score), "muc_rui_ro": risk_band(score), "xac_suat_vo_no_pct": round(100 * p, 1),
        "xac_suat_vo_no_trung_binh_quan_the_pct": round(100 * pop, 1), "thang_diem": "300–850",
        "ho_so": {node_vi()[k]: state_vi(k, v) for k, v in profile.items() if k in INPUTS},
        "bien_chua_biet": [node_vi()[n] for n in INPUTS if n not in profile],
        "yeu_to_keo_diem_xuong": [c for c in contrib if c["points"] < 0][:3],
        "yeu_to_giup_diem": [c for c in reversed(contrib) if c["points"] > 0][:3],
    }
    for n in ("sector", "ext_score_mean"):
        if n in profile:
            facts[f"rui_ro_nhom_{n}"] = {"nhom": state_vi(n, profile[n]),
                                         "xac_suat_vo_no_pct": round(100 * _p(bn, {n: profile[n]}), 1)}
    whatif = {}
    shocks = [("job_loss", "yes", "Mất việc"), ("health_shock", "yes", "Biến cố sức khỏe (chi y tế lớn)"),
              ("econ_cycle", "downturn", "Kinh tế suy giảm")]
    for node, val, lab in shocks:
        if node == "job_loss" and profile.get("years_employed") == "not_working":
            continue
        s1 = float(to_score(_p(bn, {**profile, node: val})))
        whatif[lab] = {"diem_moi": round(s1), "thay_doi": round(s1 - score)}
    facts["what_if"] = whatif
    target = target_score or next_target(score)
    if target:
        cf = counterfactual_search(bn, profile, target_score=target)
        facts["muc_tieu_diem"] = target
        facts["ke_hoach"] = [{"thay_doi": pl.describe(), "diem_dat_duoc": round(pl.score), "chi_phi": pl.cost}
                             for pl in cf["plans"][:3]]
        if not cf["plans"]:
            b = cf["best_possible"]
            facts["khong_dat_muc_tieu"] = {"diem_toi_da": round(b.score), "thay_doi": b.describe()}
    if others:
        facts["mo_hinh_khac"] = {k: round(v) for k, v in others.items()}
    return facts

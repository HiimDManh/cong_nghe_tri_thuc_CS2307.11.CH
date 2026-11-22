"""Xây và học BN-Expert (2 lớp) + biến thể đơn điệu; quy đổi xác suất -> điểm 300–850.

- Lớp data: CPT học từ dữ liệu (BDeu).
- Lớp expert: CPT từ tri thức (src/bn/expert_cpt.py).
- Nút `default`: P_data(D | cha dữ liệu) học từ dữ liệu, nối với `cashflow_shock` bằng calibrated noisy-OR:
    P(D=1 | pa, shock=no)  = p0
    P(D=1 | pa, shock=yes) = 1 − (1 − p0)(1 − λ)
    p0 = (P_data − λπ) / (1 − λπ),  π = P(shock=yes) tiên nghiệm của quần thể
  => khi không có bằng chứng về biến cố, xác suất ≈ P_data đã học; bật biến cố -> rủi ro tăng theo λ.
- `monotone=True` (BN-Expert-Mono): chiếu CPT P_data lên ràng buộc đơn điệu chuyên gia bằng isotonic
  regression có trọng số số mẫu (DSTI tăng -> rủi ro không giảm; ext_score tăng -> rủi ro không tăng).
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

from src.bn import expert_cpt
from src.bn.core import DiscreteBN
from src.common import load_config, path
from src.data.discretize import Discretizer

MONOTONE_CONSTRAINTS = {"annuity_to_income": "increasing", "ext_score_mean": "decreasing"}
EDUCATION_STATES = ["secondary_or_lower", "incomplete_higher", "higher"]


def node_states(disc: Discretizer | None = None) -> dict[str, list[str]]:
    """Trạng thái của mọi nút (data + expert), theo đúng thứ tự có nghĩa."""
    disc = disc or Discretizer()
    st = disc.states()
    st["sector"] = list(dict.fromkeys(pd.read_csv(path("knowledge_base", "sector_mapping.csv"))["group"]))
    st["occupation_group"] = list(dict.fromkeys(
        pd.read_csv(path("knowledge_base", "occupation_mapping.csv"), keep_default_na=False)["group"]))
    st["education"] = EDUCATION_STATES
    st["region_rating"] = ["1", "2", "3"]
    st["default"] = ["0", "1"]
    for n, a in load_config("bn_expert")["nodes"].items():
        if a.get("layer") == "expert":
            st[n] = [str(s) for s in a["states"]]
    return st


def expert_structure() -> tuple[dict[str, list[str]], dict[str, list[str]], list[str]]:
    """(states, parents, data_parents_of_default) theo configs/bn_expert.yaml."""
    cfg = load_config("bn_expert")
    states = node_states()
    states = {n: states[n] for n in cfg["nodes"]}
    parents: dict[str, list[str]] = {n: [] for n in cfg["nodes"]}
    for p, c, *_ in cfg["edges"]:
        parents[c].append(p)
    expert = {n for n, a in cfg["nodes"].items() if a.get("layer") == "expert"}
    data_par = [p for p in parents["default"] if p not in expert]
    return states, parents, data_par


def isotonic_project(cpt: np.ndarray, counts: np.ndarray, parents: list[str],
                     constraints: dict[str, str], max_passes: int = 30, tol: float = 1e-8) -> np.ndarray:
    """Chiếu P(D=1|pa) lên giao các ràng buộc đơn điệu theo từng trục cha.

    Mỗi bước là isotonic regression có trọng số N_ij (phép chiếu lên một tập lồi); lặp luân phiên
    (POCS) đến khi mọi ràng buộc thỏa (sai số < tol).
    """
    p1 = cpt[..., 1].copy()
    w = np.maximum(counts, 1e-3)
    axes = {parents.index(v): d for v, d in constraints.items() if v in parents}

    def violation(p: np.ndarray) -> float:
        v = 0.0
        for ax, d in axes.items():
            diff = np.diff(p, axis=ax)
            v = max(v, float((-diff if d == "increasing" else diff).max(initial=0.0)))
        return v

    for _ in range(max_passes):
        for ax, direction in axes.items():
            moved_p, moved_w = np.moveaxis(p1, ax, -1), np.moveaxis(w, ax, -1)
            out = moved_p.copy()
            for idx in itertools.product(*[range(s) for s in moved_p.shape[:-1]]):
                ir = IsotonicRegression(increasing=(direction == "increasing"), y_min=1e-6, y_max=1 - 1e-6)
                out[idx] = ir.fit_transform(np.arange(moved_p.shape[-1]), moved_p[idx], sample_weight=moved_w[idx])
            p1 = np.moveaxis(out, -1, ax)
        if violation(p1) < tol:
            break
    # Bước đóng: POCS chỉ hội tụ tiệm cận. cummax/cummin tuần tự cho nghiệm thỏa CHÍNH XÁC mọi ràng buộc,
    # vì min/max theo một trục của các hàm đơn điệu theo trục khác vẫn đơn điệu theo trục đó.
    for ax, direction in axes.items():
        acc = np.maximum.accumulate if direction == "increasing" else np.minimum.accumulate
        p1 = acc(p1, axis=ax)
    assert violation(p1) <= 1e-12
    return np.stack([1 - p1, p1], axis=-1)


def fit_expert_bn(train_disc: pd.DataFrame, train_feat: pd.DataFrame, ess: float = 10.0,
                  monotone: bool = False, lam: float | None = None) -> DiscreteBN:
    """Học BN-Expert trên tập train (đã rời rạc) + đặc trưng gốc (cho proxy churn của ngành)."""
    states, parents, data_par = expert_structure()
    link = load_config("bn_expert_cpt")["default_link"]
    lam = link["lambda"] if lam is None else lam
    bn = DiscreteBN(states, parents, meta={"name": "BN-Expert-Mono" if monotone else "BN-Expert", "lambda": lam})
    expert_cpts = expert_cpt.build(states, parents, train_feat)
    expert = set(expert_cpts)
    bn.cpts.update(expert_cpts)
    data_nodes = [n for n in states if n not in expert and n != "default"]
    bn.fit(train_disc, data_nodes, ess)

    # P_data(default | cha dữ liệu)
    full = parents["default"]
    bn.parents["default"] = data_par
    bn.fit_node(train_disc, "default", ess)
    p_data = bn.cpts["default"]
    if monotone:
        p_data = isotonic_project(p_data, bn.meta["counts"]["default"], data_par, MONOTONE_CONSTRAINTS)
    bn.parents["default"] = full

    pi = float(bn.query(pd.DataFrame(index=[0]), "cashflow_shock")[0, 1])
    p = p_data[..., 1]
    p0 = np.clip((p - lam * pi) / (1 - lam * pi), link["min_p0"], 1 - 1e-6)
    shock_axis = full.index("cashflow_shock")
    no = np.stack([1 - p0, p0], -1)
    yes_p = 1 - (1 - p0) * (1 - lam)
    yes = np.stack([1 - yes_p, yes_p], -1)
    cpt = np.stack([no, yes], axis=-2)  # (..., shock, default) với shock là trục cha cuối của data_par
    bn.cpts["default"] = np.moveaxis(cpt, -2, shock_axis)
    bn.meta.update(pi_shock=pi, n_p0_clipped=int((p - lam * pi <= 0).sum()))
    bn.validate()
    return bn


# ---------------------------------------------------------------------- điểm tín dụng
def score_params() -> tuple[float, float]:
    s = load_config("bn_expert_cpt")["scoring"]
    lo, hi = s["anchor_low"], s["anchor_high"]
    l_lo, l_hi = np.log((1 - lo["p"]) / lo["p"]), np.log((1 - hi["p"]) / hi["p"])
    b = (hi["score"] - lo["score"]) / (l_hi - l_lo)
    return lo["score"] - b * l_lo, b


def to_score(p: np.ndarray | float) -> np.ndarray:
    """P(vỡ nợ) -> điểm 300–850 (log-odds tuyến tính, đơn điệu giảm theo p)."""
    a, b = score_params()
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    lo, hi = load_config("bn_expert_cpt")["scoring"]["clip"]
    return np.clip(a + b * np.log((1 - p) / p), lo, hi)


def score_to_p(score: float) -> float:
    """Ngược của to_score (trong vùng không bị cắt)."""
    a, b = score_params()
    return float(1 / (1 + np.exp((score - a) / b)))


def risk_band(score: float) -> str:
    for band in load_config("bn_expert_cpt")["scoring"]["risk_bands"]:
        if score >= band["min"]:
            return band["label"]
    return "Rất kém"

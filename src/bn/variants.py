"""Các biến thể Bayes để so sánh: Naive Bayes, TAN, BN-Learned (Hill-Climb + BIC), BN-Hybrid.

Tất cả dùng CÙNG tập nút dữ liệu của BN-Expert (không có lớp expert) và cùng cách ước lượng tham số
(m-estimate) -> khác biệt chỉ nằm ở cấu trúc.
"""
from __future__ import annotations

import warnings

import pandas as pd

from src.bn.core import DiscreteBN
from src.bn.model import expert_structure

TARGET = "default"
# Thứ tự thời gian/nhân quả (tri thức) cho BN-Hybrid: không biến ở tầng sau được làm cha tầng trước.
TIERS = [
    ["sector", "age_years", "education", "region_rating"],
    ["occupation_group", "years_employed", "n_children"],
    ["income", "bureau_inquiries_year"],
    ["assets", "annuity_to_income", "ext_score_mean"],
    ["credit_to_income"],
    [TARGET],
]


def data_nodes() -> tuple[dict[str, list[str]], list[str]]:
    states, parents, _ = expert_structure()
    from src.common import load_config

    nodes = [n for n, a in load_config("bn_expert")["nodes"].items() if a.get("layer") == "data"]
    return {n: states[n] for n in nodes}, nodes


def _complete(train_disc: pd.DataFrame, nodes: list[str], max_rows: int | None, seed: int) -> pd.DataFrame:
    d = train_disc[nodes].dropna()
    if max_rows and len(d) > max_rows:
        d = d.sample(max_rows, random_state=seed)
    return d.astype(str)


def from_edges(edges: list[tuple[str, str]], name: str, train_disc: pd.DataFrame, ess: float) -> DiscreteBN:
    states, nodes = data_nodes()
    parents = {n: [] for n in nodes}
    for p, c in edges:
        parents[c].append(p)
    bn = DiscreteBN(states, parents, meta={"name": name, "edges": [list(e) for e in edges]})
    bn.fit(train_disc, ess=ess)
    bn.validate()
    return bn


def naive_bayes(train_disc: pd.DataFrame, ess: float = 10.0) -> DiscreteBN:
    _, nodes = data_nodes()
    return from_edges([(TARGET, n) for n in nodes if n != TARGET], "Naive Bayes", train_disc, ess)


def tan(train_disc: pd.DataFrame, ess: float = 10.0, max_rows: int | None = 100_000, seed: int = 42) -> DiscreteBN:
    from pgmpy.estimators import TreeSearch

    _, nodes = data_nodes()
    d = _complete(train_disc, nodes, max_rows, seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        dag = TreeSearch(d).estimate(estimator_type="tan", class_node=TARGET, show_progress=False)
    return from_edges(list(dag.edges()), "TAN", train_disc, ess)


def hill_climb(train_disc: pd.DataFrame, hybrid: bool, ess: float = 10.0, max_rows: int | None = 60_000,
               seed: int = 42, max_indegree: int = 4) -> DiscreteBN:
    """BN-Learned (hybrid=False): Hill-Climb + BIC, không ràng buộc.
    BN-Hybrid (hybrid=True): + cạnh bắt buộc từ BN-Expert (lớp data) + thứ tự tầng TIERS."""
    from pgmpy.estimators import ExpertKnowledge, HillClimbSearch

    _, nodes = data_nodes()
    d = _complete(train_disc, nodes, max_rows, seed)
    ek = None
    if hybrid:
        _, parents, _ = expert_structure()
        required = [(p, c) for c, ps in parents.items() for p in ps if p in nodes and c in nodes]
        ek = ExpertKnowledge(required_edges=required, temporal_order=TIERS)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        dag = HillClimbSearch(d).estimate(scoring_method="bic-d", max_indegree=max_indegree,
                                          expert_knowledge=ek, show_progress=False)
    return from_edges(list(dag.edges()), "BN-Hybrid" if hybrid else "BN-Learned", train_disc, ess)

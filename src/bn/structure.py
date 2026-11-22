"""Đọc cấu trúc BN-Expert từ YAML, kiểm tra DAG, vẽ hình, và đo mức ủng hộ của dữ liệu cho từng cạnh."""
from __future__ import annotations

import textwrap
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from src.common import load_config, path, utf8_stdout

DATA_COLOR, EXPERT_COLOR, TARGET_COLOR = "#A6C8E8", "#F6C28B", "#E58C8A"

# Toạ độ (cột, hàng) để hình đọc từ trái (nguyên nhân) sang phải (vỡ nợ)
LAYOUT = {
    "region_rating": (0, 7), "education": (0, 5), "sector": (0, 3), "age_years": (0, 1),
    "occupation_group": (1, 5), "years_employed": (1, 3), "n_children": (1, 1),
    "income": (2, 6.4), "ext_score_mean": (2.2, 3), "bureau_inquiries_year": (2.2, 1.4),
    "assets": (3.2, 7.2), "annuity_to_income": (3.2, 5.2), "credit_to_income": (4.2, 6.6),
    "inflation": (0, -1.4), "econ_cycle": (1.2, -2.0), "living_cost": (1.2, -0.4),
    "job_loss": (2.4, -0.6), "health_shock": (2.4, -2.0), "cashflow_shock": (3.6, -0.8),
    "default": (5, 3),
}


def load_expert() -> dict[str, Any]:
    return load_config("bn_expert")


def to_graph(cfg: dict[str, Any] | None = None) -> nx.DiGraph:
    cfg = cfg or load_expert()
    g = nx.DiGraph()
    for n, a in cfg["nodes"].items():
        g.add_node(n, **a)
    for p, c, why, ev in cfg["edges"]:
        if p not in g or c not in g:
            raise KeyError(f"Cạnh {p}->{c}: nút chưa khai báo")
        g.add_edge(p, c, reason=why, evidence=ev)
    if not nx.is_directed_acyclic_graph(g):
        raise ValueError(f"Có chu trình: {nx.find_cycle(g)}")
    return g


def draw(g: nx.DiGraph, out: str = "bn_expert_dag.png") -> None:
    fig, ax = plt.subplots(figsize=(16, 10))
    pos = {n: LAYOUT.get(n, (5, 0)) for n in g}
    colors = [TARGET_COLOR if g.nodes[n].get("target") else
              EXPERT_COLOR if g.nodes[n]["layer"] == "expert" else DATA_COLOR for n in g]
    nx.draw_networkx_edges(g, pos, ax=ax, arrowsize=14, edge_color="#777", node_size=3600,
                           connectionstyle="arc3,rad=0.06")
    nx.draw_networkx_nodes(g, pos, ax=ax, node_color=colors, node_size=3600, edgecolors="#333")
    labels = {n: textwrap.fill(g.nodes[n]["label"], 11) for n in g}
    nx.draw_networkx_labels(g, pos, labels, font_size=8, ax=ax)
    for c, lbl in [(DATA_COLOR, "Quan sát (học từ dữ liệu)"), (EXPERT_COLOR, "Tri thức chuyên gia (what-if)"),
                   (TARGET_COLOR, "Nút đích")]:
        ax.scatter([], [], c=c, s=150, edgecolors="#333", label=lbl)
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    ax.set_title("BN-Expert (đề xuất) – Ngành → Thu nhập → Biến cố → Vỡ nợ", fontsize=13)
    ax.axis("off")
    fig.tight_layout()
    f = path("reports", "figures", out)
    fig.savefig(f, dpi=140)
    plt.close(fig)
    print(f"[bn] hình DAG -> {f}")


def edge_support(g: nx.DiGraph, X: pd.DataFrame) -> pd.DataFrame:
    """Cramér's V giữa hai đầu mỗi cạnh data–data (mức ủng hộ từ dữ liệu, không phải kiểm định nhân quả)."""
    from src.data.eda import cramers_v

    rows = []
    for p, c in g.edges:
        if p in X and c in X:
            v = cramers_v(X[p].fillna("NA"), X[c].fillna("NA"))
            rows.append({"edge": f"{p} → {c}", "cramers_v": round(v, 3)})
        else:
            rows.append({"edge": f"{p} → {c}", "cramers_v": None})
    return pd.DataFrame(rows)


def main() -> None:
    utf8_stdout()
    g = to_graph()
    draw(g)
    from src.data.discretize import Discretizer
    from src.data.home_credit import load_features

    X = Discretizer().fit_transform(load_features())
    sup = edge_support(g, X)
    out = path("reports", "eda", "bn_expert_edge_support.md")
    out.write_text("# Mức ủng hộ của dữ liệu cho từng cạnh BN-Expert (Cramér's V)\n\n"
                   "_Sinh bởi `python -m src.bn.structure`. Trống = cạnh có nút tri thức (không có dữ liệu)._\n\n"
                   + sup.to_markdown(index=False) + "\n", encoding="utf-8")
    print(f"[bn] {g.number_of_nodes()} nút, {g.number_of_edges()} cạnh, DAG hợp lệ")
    print(sup.to_string(index=False))


if __name__ == "__main__":
    main()

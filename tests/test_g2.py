"""Test giai đoạn 2: mapping, rời rạc hóa, FICO, cấu trúc BN-Expert."""
import numpy as np
import pandas as pd
import pytest

from src.common import load_config, path


def test_mappings_unique_and_grouped():
    s = pd.read_csv(path("knowledge_base", "sector_mapping.csv"))
    o = pd.read_csv(path("knowledge_base", "occupation_mapping.csv"), keep_default_na=False)
    assert not s["ORGANIZATION_TYPE"].duplicated().any()
    assert not o["OCCUPATION_TYPE"].duplicated().any()
    assert 6 <= s["group"].nunique() <= 10
    assert o["group"].nunique() <= 5
    assert s["source_url"].str.startswith("http").all()


@pytest.fixture(scope="module")
def hc():
    f = path("data", "raw", "application_train.csv")
    if not f.exists():
        pytest.skip("Chưa có Home Credit")
    from src.data.home_credit import load_features

    return load_features(nrows=20000)


def test_all_raw_values_mapped(hc):
    assert hc["sector"].notna().all()
    assert hc["occupation_group"].notna().all()


def test_discretizer_states_and_no_leak(hc):
    from src.data.discretize import Discretizer

    train, test = hc.iloc[:15000], hc.iloc[15000:]
    d = Discretizer().fit(train)
    X = d.transform(test)
    states = d.states()
    for col, allowed in states.items():
        vals = set(X[col].dropna().unique())
        assert vals <= set(allowed), (col, vals - set(allowed))
        assert len(allowed) <= 5, col
    # ngưỡng quantile chỉ phụ thuộc tập train
    assert d.edges_["income"] == Discretizer().fit(train).edges_["income"]


def test_fico_monotone_and_range(hc):
    from src.baselines.fico import FicoScorer
    from src.data.discretize import Discretizer

    X = Discretizer().fit_transform(hc)
    f = FicoScorer()
    s = f.score(X)
    assert s.min() >= 300 and s.max() <= 850
    better = X.copy()
    better["ext_score_mean"] = "very_good"
    assert np.all(f.score(better) >= s)  # cải thiện lịch sử tín dụng không làm giảm điểm


def test_fico_weights_sum_to_one():
    w = sum(v["weight"] for v in load_config("fico")["factors"].values())
    assert np.isclose(w, 1.0)


def test_bn_expert_is_dag_and_target_reachable():
    import networkx as nx

    from src.bn.structure import to_graph

    g = to_graph()
    assert nx.is_directed_acyclic_graph(g)
    assert nx.is_weakly_connected(g)
    for n in g:
        if n != "default" and g.nodes[n].get("role") != "indicator":
            assert nx.has_path(g, n, "default"), f"{n} không ảnh hưởng tới default"
        if g.nodes[n].get("role") == "indicator":
            assert g.out_degree(n) == 0 and g.in_degree(n) > 0
    # chuỗi nhân quả của đề
    for a, b in [("sector", "income"), ("cashflow_shock", "default")]:
        assert g.has_edge(a, b)
    assert nx.has_path(g, "income", "cashflow_shock")

"""Test Mạng Bayes: tính đúng của suy luận (đối chiếu pgmpy), CPT, đơn điệu, điểm, suy luận ngược."""
import networkx as nx
import numpy as np
import pandas as pd
import pytest

from src.bn.core import DiscreteBN


# --------------------------------------------------------------------------- mạng nhỏ tổng hợp
@pytest.fixture(scope="module")
def toy():
    rng = np.random.default_rng(0)
    states = {"A": ["a0", "a1", "a2"], "B": ["b0", "b1"], "C": ["c0", "c1"], "D": ["d0", "d1", "d2"], "Y": ["0", "1"]}
    parents = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"], "Y": ["D", "A"]}
    bn = DiscreteBN(states, parents)
    for n, ps in parents.items():
        shape = tuple(len(states[p]) for p in ps) + (len(states[n]),)
        bn.cpts[n] = rng.dirichlet(np.ones(shape[-1]), size=shape[:-1]) if ps else rng.dirichlet(np.ones(shape[-1]))
    bn.validate()
    return bn


def _pgmpy_query(model, target, ev):
    from pgmpy.inference import VariableElimination

    ev = {k: v for k, v in ev.items() if isinstance(v, str)}
    return VariableElimination(model).query([target], evidence=ev or None, show_progress=False).values


def test_batch_inference_matches_pgmpy(toy):
    model = toy.to_pgmpy()
    rows = [{"A": "a1", "B": "b0", "C": "c1", "D": "d2"}, {"B": "b1"}, {"C": "c0", "D": "d0"}, {}, {"A": "a2", "D": "d1"}]
    ours = toy.query(pd.DataFrame(rows).reindex(columns=["A", "B", "C", "D"]), "Y")
    for r, o in zip(rows, ours):
        np.testing.assert_allclose(o, _pgmpy_query(model, "Y", r), atol=1e-10)
    # đích không phải nút lá (suy luận ngược chiều cạnh)
    ours_b = toy.query(pd.DataFrame([{"Y": "1", "D": "d0"}]), "A")[0]
    np.testing.assert_allclose(ours_b, _pgmpy_query(model, "A", {"Y": "1", "D": "d0"}), atol=1e-10)


def test_bdeu_matches_pgmpy(toy):
    from pgmpy.estimators import BayesianEstimator

    rng = np.random.default_rng(1)
    data = pd.DataFrame({n: rng.choice(s, 500) for n, s in toy.states.items()})
    bn = DiscreteBN(toy.states, toy.parents).fit(data, ess=5, prior="bdeu")
    model = toy.to_pgmpy()
    est = BayesianEstimator(model, data, state_names=toy.states)
    cpd = est.estimate_cpd("D", prior_type="BDeu", equivalent_sample_size=5)
    np.testing.assert_allclose(bn.cpts["D"].reshape(-1, 3).T, cpd.get_values(), atol=1e-10)


def test_m_estimate_unseen_config_returns_marginal(toy):
    data = pd.DataFrame({"A": ["a0"] * 90 + ["a1"] * 10, "B": ["b0"] * 100, "C": ["c0"] * 100,
                         "D": ["d0"] * 100, "Y": ["0"] * 80 + ["1"] * 20})
    bn = DiscreteBN(toy.states, toy.parents).fit(data, ess=10)
    # tổ hợp cha (D=d2, A=a2) chưa gặp -> phân phối biên ~ (0.8, 0.2) chứ không phải (0.5, 0.5)
    np.testing.assert_allclose(bn.cpts["Y"][2, 2], [80.5 / 101, 20.5 / 101], atol=1e-9)


def test_json_roundtrip(toy, tmp_path):
    f = tmp_path / "bn.json"
    toy.to_json(f)
    bn2 = DiscreteBN.from_json(f)
    ev = pd.DataFrame([{"A": "a1"}, {"D": "d2"}])
    np.testing.assert_allclose(toy.query(ev, "Y"), bn2.query(ev, "Y"), atol=1e-6)


# --------------------------------------------------------------------------- BN-Expert trên Home Credit
@pytest.fixture(scope="module")
def hc():
    from src.common import path

    if not path("data", "raw", "application_train.csv").exists():
        pytest.skip("Chưa có Home Credit")
    from src.data.discretize import Discretizer
    from src.data.home_credit import load_features

    feat = load_features(nrows=40000)
    X = Discretizer().fit_transform(feat)
    return feat, X


@pytest.fixture(scope="module")
def experts(hc):
    from src.bn.model import fit_expert_bn

    feat, X = hc
    return fit_expert_bn(X, feat), fit_expert_bn(X, feat, monotone=True)


def test_expert_bn_valid(experts):
    for bn in experts:
        bn.validate()
        assert nx.is_directed_acyclic_graph(bn.graph)
        for n, c in bn.cpts.items():
            np.testing.assert_allclose(c.sum(-1), 1.0, atol=1e-9)


def test_expert_inference_matches_pgmpy_partial_evidence(experts, hc):
    bn = experts[1]
    _, X = hc
    model = bn.to_pgmpy()
    rows = X.drop(columns="default").iloc[:3].to_dict("records")
    rows[1] = {k: v for i, (k, v) in enumerate(rows[1].items()) if i % 2 == 0}  # thiếu một nửa bằng chứng
    rows[2] = {"sector": rows[2]["sector"], "income": rows[2]["income"], "health_shock": "yes"}
    ours = bn.query(pd.DataFrame(rows), "default")
    for r, o in zip(rows, ours):
        np.testing.assert_allclose(o, _pgmpy_query(model, "default", r), atol=1e-8)


def test_probabilities_valid(experts, hc):
    _, X = hc
    p = experts[0].predict_proba(X.drop(columns="default").iloc[:2000])
    assert np.all((p > 0) & (p < 1))


def test_monotone_variant_respects_constraints(experts):
    bn = experts[1]
    ps = bn.parents["default"]
    p1 = bn.cpts["default"][..., 1]
    dsti = ps.index("annuity_to_income")
    ext = ps.index("ext_score_mean")
    assert np.all(np.diff(p1, axis=dsti) >= -1e-9), "DSTI tăng thì rủi ro không được giảm"
    assert np.all(np.diff(p1, axis=ext) <= 1e-9), "Lịch sử tín dụng tốt hơn thì rủi ro không được tăng"


def test_shock_increases_risk(experts, hc):
    _, X = hc
    ev = X.drop(columns="default")
    ev = ev[ev["years_employed"] != "not_working"].iloc[:200]  # 'mất việc' bất khả với người không đi làm
    bn = experts[0]
    base = bn.predict_proba(ev)
    shocked = bn.predict_proba(ev.assign(job_loss="yes"))
    assert np.all(shocked >= base - 1e-12) and shocked.mean() > base.mean()


def test_impossible_evidence_gives_nan(experts):
    ev = pd.DataFrame([{"years_employed": "not_working", "job_loss": "yes"}])
    assert np.isnan(experts[0].predict_proba(ev)).all()


def test_lambda_zero_recovers_data_cpt(hc):
    from src.bn.model import fit_expert_bn

    feat, X = hc
    bn = fit_expert_bn(X, feat, lam=0.0)
    p = bn.cpts["default"][..., 1]
    shock = bn.parents["default"].index("cashflow_shock")
    np.testing.assert_allclose(np.take(p, 0, axis=shock), np.take(p, 1, axis=shock), atol=1e-9)


def test_score_mapping():
    from src.bn.model import score_to_p, to_score

    assert to_score(0.5) == pytest.approx(400) and to_score(0.005) == pytest.approx(800, abs=1e-6)
    s = to_score(np.linspace(0.001, 0.999, 200))
    assert np.all(np.diff(s) <= 0) and s.min() >= 300 and s.max() <= 850
    assert to_score(score_to_p(650)) == pytest.approx(650)


# --------------------------------------------------------------------------- suy luận ngược
def test_intervention_cuts_parents(experts):
    from src.bn.backward import intervene

    bn2 = intervene(experts[0], ["income"])
    assert bn2.parents["income"] == [] and experts[0].parents["income"] != []
    bn2.validate()


def test_counterfactual_plans_reach_target_and_respect_directions(experts, hc):
    from src.bn.backward import _levers, _ordered, counterfactual_search

    bn = experts[1]
    _, X = hc
    prof = X.drop(columns="default").iloc[5].dropna().to_dict()
    r = counterfactual_search(bn, prof, target_p=r_p if (r_p := None) else 0.5 * float(bn.predict_proba(pd.DataFrame([prof]))[0]))
    lv = _levers()
    for plan in r["plans"]:
        assert plan.p_default <= r["target"]["p_default"] + 1e-12
        for k, (a, b) in plan.changes.items():
            order = _ordered(bn, k)
            if a in order:
                step = order.index(b) - order.index(a)
                assert (step > 0) if lv[k]["direction"] == "up" else (step < 0)
                assert abs(step) <= lv[k]["max_steps"]
    costs = [p.cost for p in r["plans"]]
    assert costs == sorted(costs)


def test_backward_posterior_is_distribution(experts, hc):
    from src.bn.backward import backward_posterior

    _, X = hc
    prof = X.drop(columns="default").iloc[0].dropna().to_dict()
    res = backward_posterior(experts[1], prof, {"default": "0"})
    for df in res.values():
        assert df.iloc[:, 1].sum() == pytest.approx(1, abs=1e-3) and df.iloc[:, 2].sum() == pytest.approx(1, abs=1e-3)


def test_variants_fit(hc):
    from src.bn import variants as V

    _, X = hc
    for bn in [V.naive_bayes(X), V.tan(X, max_rows=10000), V.hill_climb(X, hybrid=True, max_rows=10000)]:
        bn.validate()
        p = bn.predict_proba(X.drop(columns="default").iloc[:100])
        assert np.all((p > 0) & (p < 1))

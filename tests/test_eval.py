"""Test khung đánh giá (metric, kiểm định, split), quy đổi đầu vào demo và kiểm tra độ trung thành LLM."""
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import roc_auc_score

from src.evaluation import metrics as M


def test_delong_auc_matches_sklearn_and_null():
    rng = np.random.default_rng(0)
    y = rng.random(3000) < 0.2
    p1 = y * 0.8 + rng.random(3000)
    p2 = y * 0.3 + rng.random(3000)
    d = M.delong(y, p1, p2)
    assert d["auc1"] == pytest.approx(roc_auc_score(y, p1)) and d["auc2"] == pytest.approx(roc_auc_score(y, p2))
    assert d["p_value"] < 1e-6
    assert M.delong(y, p1, p1 + 1e-12 * rng.random(3000))["p_value"] > 0.5


def test_ece_zero_for_perfect_calibration_and_holm():
    rng = np.random.default_rng(1)
    p = rng.random(200000) * 0.3
    y = (rng.random(200000) < p).astype(int)
    assert M.ece(y, p) < 0.005 and M.ece(y, np.clip(p + 0.1, 0, 1)) > 0.09
    assert M.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])


def test_paired_bootstrap_sign():
    rng = np.random.default_rng(2)
    p = rng.random(5000) * 0.3
    y = (rng.random(5000) < p).astype(int)
    r = M.paired_bootstrap(y, p, np.clip(p * 1.8, 0, 1), n=200)
    assert r["d_logloss_hi"] < 0 and r["d_ece_hi"] < 0  # mô hình hiệu chỉnh đúng tốt hơn rõ rệt


def test_splits_stratified():
    from src.evaluation.cv import make_splits

    y = np.r_[np.ones(100), np.zeros(900)].astype(int)
    f = make_splits(np.arange(1000), y, 5, [1, 2])
    for s in (1, 2):
        assert np.bincount(f[s]).tolist() == [200] * 5
        assert all(y[f[s] == k].sum() == 20 for k in range(5))
    assert not np.array_equal(f[1], f[2])


def test_group_mapping_and_mask():
    from src.baselines.ml import GROUPS, group_of
    from src.evaluation.explain import mask

    assert group_of("cat__sector_trade_hospitality") == "sector"
    assert group_of("num__not_working") == "years_employed"
    Xf = pd.DataFrame({c: [1.0, 2.0] for g in GROUPS.values() for c in g["cont"] if c != "not_working"})
    Xf["years_employed"] = [np.nan, 3.0]
    for c in ("sector", "occupation_group", "education"):
        Xf[c] = ["a", "b"]
    Xd = pd.DataFrame({c: ["x", "y"] for g in GROUPS.values() for c in g["disc"]})
    m = np.zeros((2, len(GROUPS)), bool)
    m[1, list(GROUPS).index("years_employed")] = True
    f2, d2 = mask(Xf, Xd, m)
    assert f2.loc[0, "not_working"] == 1 and f2.loc[0, "years_employed"] == 0  # không đi làm ≠ thiếu
    assert np.isnan(f2.loc[1, "years_employed"]) and np.isnan(f2.loc[1, "not_working"]) and pd.isna(d2.loc[1, "years_employed"])


def test_convert_profile():
    from src.app.convert import UserInput, gso_quintile_bounds, to_profile

    b = gso_quintile_bounds()
    assert len(b) == 4 and all(np.diff(b) > 0)
    p = to_profile(UserInput(age=25, working=True, years_employed=2, household_income_m=12, household_size=3,
                             personal_income_m=10, monthly_installment_m=3.5, total_debt_m=600, own_house=True,
                             own_car=False, n_children=0))
    assert p["age_years"] == "<30" and p["years_employed"] == "1-3" and p["income"] == "Q3"  # 4 triệu/người
    assert p["annuity_to_income"] == "30-40%" and p["credit_to_income"] == "4.5-7x" and p["assets"] == "realty"
    q = to_profile(UserInput(working=False))
    assert q["years_employed"] == "not_working" and q["sector"] == "not_working" and q["income"] is None


def test_faithfulness_detects_fabrication():
    from src.llm.faithfulness import check, numbers

    facts = {"diem": 612, "muc_rui_ro": "Trung bình", "xac_suat_vo_no_pct": 6.4, "thang_diem": "300–850",
             "yeu_to_keo_diem_xuong": [{"label": "Lịch sử tín dụng", "points": -18}], "yeu_to_giup_diem": []}
    good = "**Tóm tắt**\nĐiểm của bạn là 612, mức Trung bình, xác suất vỡ nợ 6,4%.\n1. Lịch sử tín dụng kéo điểm xuống 18 điểm."
    assert check(good, facts)["faithful"]
    assert numbers("1.500.000 đồng và 6,4%") == [1500000.0, 6.4]
    bad = good.replace("6,4%", "9,7%")
    assert not check(bad, facts)["faithful"]
    wrong_dir = good.replace("kéo điểm xuống", "giúp tăng")
    assert not check(wrong_dir, facts)["direction_ok"]
    # nhãn "Thu nhập" không được khớp nhầm vào "Trả góp/Thu nhập (DSTI)"
    f2 = {**facts, "yeu_to_keo_diem_xuong": [{"label": "Thu nhập", "points": -5}],
          "yeu_to_giup_diem": [{"label": "Trả góp/Thu nhập (DSTI)", "points": 4}]}
    txt = "Điểm 612, mức Trung bình, 6,4%. Thu nhập kéo điểm xuống 5 điểm. Trả góp/Thu nhập (DSTI) giúp tăng 4 điểm."
    assert check(txt, f2)["direction_ok"]
    # số thứ tự "kế hoạch 2" là nhãn; còn số tự tính (612 → 670 "thiếu 58 điểm") vẫn bị bắt
    assert numbers("Đạt 612 điểm (kế hoạch 2), Phương án 3") == [612.0]
    assert not check(good + " Còn thiếu 58 điểm.", facts)["faithful"]


def test_report_placeholders_never_invent_numbers():
    from src.evaluation.report import render

    missing: list[str] = []
    out = render("AUC {{num:auc.X}} và {{num:khong_co}} {{table:khong_co_bang}}", {"auc.X": "0.712"}, missing)
    assert "0.712" in out and "⟦THIẾU num:khong_co⟧" in out and len(missing) == 2

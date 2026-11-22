"""Chạy thực nghiệm BN vs Black-box ML (G4). Mỗi thí nghiệm -> experiments/<tên>/results.csv.

    python -m src.cli eval                 # chạy tất cả theo thứ tự
    python -m src.cli eval main_cv missing # chỉ một số thí nghiệm

Thứ tự phụ thuộc: main_cv (lưu dự báo OOF + mô hình seed đầu vào data/interim/) -> các thí nghiệm khác.
Thời gian đo trên CPU 16 luồng: main_cv ~16 phút, các thí nghiệm còn lại mỗi cái ≤ ~10 phút.
"""
from __future__ import annotations

import pickle
import time

import joblib
import numpy as np
import pandas as pd
from scipy import stats

from src.bn.model import to_score
from src.common import load_config, path, set_seed, utf8_stdout
from src.data.home_credit import load_features
from src.evaluation import metrics as M
from src.evaluation.cv import fold_data, load_splits
from src.evaluation.explain import GROUP_NAMES, attribution, mask
from src.evaluation.models import BNModel, build, n_params

MODELS_DIR = path("data", "interim", "models")
OOF_DIR = path("data", "interim", "oof")
METRIC_COLS = ["auc", "pr_auc", "gini", "ks", "brier", "logloss", "ece"]


def _cfg() -> dict:
    return load_config("eval")


def _out(name: str) -> "path":
    d = path("experiments", name)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _data() -> tuple[pd.DataFrame, dict[int, np.ndarray]]:
    feat = load_features()
    return feat, load_splits(feat)


def _fitted(seed: int, k: int) -> dict:
    return joblib.load(MODELS_DIR / f"seed{seed}_fold{k}.joblib")


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ============================================================================ (1)(2)(9) CV chính
def main_cv(feat: pd.DataFrame, sp: dict, models: list[str] | None = None) -> pd.DataFrame:
    cfg = _cfg()
    names = models or list(cfg["models"])
    nb = cfg["experiments"]["ece_bins"]
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    OOF_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for si, seed in enumerate(cfg["cv"]["seeds"]):
        set_seed(seed)
        oof = {n: np.full(len(feat), np.nan, np.float32) for n in names}
        for k in range(cfg["cv"]["n_folds"]):
            fd = fold_data(feat, sp[seed] != k)
            fitted = {}
            for n in names:
                if si > 0 and not cfg["models"][n]["all_seeds"]:
                    continue
                t = time.perf_counter()
                m = build(n, seed=seed).fit(fd.train_f, fd.train_d, fd.y_train)
                fit_s = time.perf_counter() - t
                t = time.perf_counter()
                p = m.predict_proba(fd.test_f, fd.test_d)
                pred_s = time.perf_counter() - t
                oof[n][fd.test_idx] = p
                rows.append({"seed": seed, "fold": k, "model": n, "family": cfg["models"][n]["family"],
                             "input": cfg["models"][n]["input"], **M.all_metrics(fd.y_test, p, nb),
                             "fit_s": fit_s, "pred_s_per_10k": pred_s / len(p) * 1e4, "n_params": n_params(m),
                             "size_kb": len(pickle.dumps(m)) / 1024, "n_train": len(fd.y_train)})
                fitted[n] = m
            if si == 0:
                joblib.dump(fitted, MODELS_DIR / f"seed{seed}_fold{k}.joblib", compress=3)
            _log(f"main_cv seed {seed} fold {k}: xong {len(fitted)} mô hình")
        np.savez_compressed(OOF_DIR / f"oof_seed{seed}.npz", y=feat["default"].to_numpy(),
                            **{n: v for n, v in oof.items() if not np.isnan(v).all()})
    df = pd.DataFrame(rows)
    out = _out("main_cv")
    df.to_csv(out / "results.csv", index=False)
    summarize_main(df).to_csv(out / "summary.csv", index=False)
    return df


def summarize_main(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["model", "family", "input"])
    s = g[METRIC_COLS].agg(["mean", "std"])
    s.columns = [f"{a}_{b}" for a, b in s.columns]
    s["n_runs"] = g.size()
    return s.reset_index().sort_values("auc_mean", ascending=False)


# ============================================================================ (3) kiểm định
def significance() -> pd.DataFrame:
    cfg = _cfg()
    res = pd.read_csv(path("experiments", "main_cv", "results.csv"))
    seeds = cfg["cv"]["seeds"]
    refs = [cfg["experiments"]["bootstrap"]["reference"], "XGBoost"]
    n_boot = cfg["experiments"]["bootstrap"]["n"]
    nb = cfg["experiments"]["ece_bins"]
    oof = {s: np.load(OOF_DIR / f"oof_seed{s}.npz") for s in seeds}
    rows = []
    for ref in refs:
        others = [n for n in cfg["models"] if n != ref]
        dl = {s: {n: M.delong(oof[s]["y"], oof[s][ref], oof[s][n]) for n in others if n in oof[s].files}
              for s in seeds}
        holm = {s: dict(zip(dl[s], M.holm([d["p_value"] for d in dl[s].values()]))) for s in seeds}
        y = oof[seeds[0]]["y"]
        for n in others:
            r = {"reference": ref, "model": n}
            d0 = dl[seeds[0]][n]
            r.update(auc_ref=d0["auc1"], auc_model=d0["auc2"], d_auc=d0["diff"])
            for s in seeds:
                if n in dl[s]:
                    r[f"delong_p_holm_seed{s}"] = holm[s][n]
            r.update(M.paired_bootstrap(y, oof[seeds[0]][ref], oof[seeds[0]][n], n_boot, seeds[0], nb))
            a = res[res.model == ref].set_index(["seed", "fold"])
            b = res[res.model == n].set_index(["seed", "fold"])
            j = a.join(b, lsuffix="_ref", rsuffix="_m", how="inner")
            for met in ("auc", "logloss"):
                r[f"nb_ttest_p_{met}"] = M.corrected_ttest((j[f"{met}_ref"] - j[f"{met}_m"]).to_numpy(), 4, 1)
                r[f"wins_{met}"] = int(((j[f"{met}_ref"] > j[f"{met}_m"]) if met == "auc"
                                        else (j[f"{met}_ref"] < j[f"{met}_m"])).sum())
            r["n_pairs"] = len(j)
            rows.append(r)
        _log(f"significance: xong reference {ref}")
    df = pd.DataFrame(rows)
    df.to_csv(_out("significance") / "results.csv", index=False)
    return df


# ============================================================================ (4) thiếu thông tin
SCENARIOS = {
    "no_ext_score": ["ext_score_mean"],
    "no_credit_history": ["ext_score_mean", "bureau_inquiries_year"],
    "thin_file": ["ext_score_mean", "bureau_inquiries_year", "annuity_to_income", "credit_to_income", "assets"],
}


def missing(feat: pd.DataFrame, sp: dict) -> pd.DataFrame:
    cfg = _cfg()
    e = cfg["experiments"]["missing"]
    seed = cfg["cv"]["seeds"][0]
    nb = cfg["experiments"]["ece_bins"]
    rows = []
    for k in range(cfg["cv"]["n_folds"]):
        fd = fold_data(feat, sp[seed] != k)
        fitted = _fitted(seed, k)
        U = np.random.default_rng(1000 + k).random((len(fd.y_test), len(GROUP_NAMES)))
        cases = [("mcar", r, U < r) for r in e["rates"]]
        for sc, gs in SCENARIOS.items():
            m = np.zeros_like(U, bool)
            m[:, [GROUP_NAMES.index(g) for g in gs]] = True
            cases.append((sc, m.mean(), m))
        for sc, r, m in cases:
            f2, d2 = mask(fd.test_f, fd.test_d, m)
            for n in e["models"]:
                p = fitted[n].predict_proba(f2, d2)
                rows.append({"fold": k, "scenario": sc, "rate": round(float(r), 3), "model": n,
                             **M.all_metrics(fd.y_test, p, nb)})
        _log(f"missing: fold {k}")
    df = pd.DataFrame(rows)
    df.to_csv(_out("missing") / "results.csv", index=False)
    return df


# ============================================================================ (5) dữ liệu ít
def learning_curve(feat: pd.DataFrame, sp: dict) -> pd.DataFrame:
    cfg = _cfg()
    e = cfg["experiments"]["learning_curve"]
    seed = cfg["cv"]["seeds"][0]
    nb = cfg["experiments"]["ece_bins"]
    rows = []
    for k in range(cfg["cv"]["n_folds"]):
        test = sp[seed] == k
        tr_idx = np.flatnonzero(~test)
        y = feat["default"].to_numpy()
        for frac in e["fractions"]:
            rng = np.random.default_rng(seed * 100 + k)
            sub = np.concatenate([rng.choice(tr_idx[y[tr_idx] == c], int(round(frac * (y[tr_idx] == c).sum())),
                                             replace=False) for c in (0, 1)])
            tm = np.zeros(len(feat), bool)
            tm[sub] = True
            fd = fold_data(feat, tm, test)
            for n in e["models"]:
                t = time.perf_counter()
                try:
                    m = build(n, seed=seed).fit(fd.train_f, fd.train_d, fd.y_train)
                    p = m.predict_proba(fd.test_f, fd.test_d)
                    met = M.all_metrics(fd.y_test, p, nb)
                except Exception as ex:  # ghi nhận trung thực nếu mô hình không học được với dữ liệu quá ít
                    met = {c: np.nan for c in METRIC_COLS} | {"error": repr(ex)[:120]}
                rows.append({"fold": k, "fraction": frac, "n_train": len(fd.y_train), "model": n, **met,
                             "fit_s": time.perf_counter() - t})
            _log(f"learning_curve: fold {k} frac {frac}")
    df = pd.DataFrame(rows)
    main = pd.read_csv(path("experiments", "main_cv", "results.csv"))
    main = main[(main.seed == seed) & main.model.isin(e["models"])].assign(fraction=1.0)
    df = pd.concat([df, main[["fold", "fraction", "n_train", "model", *METRIC_COLS, "fit_s"]]], ignore_index=True)
    df.to_csv(_out("learning_curve") / "results.csv", index=False)
    return df


# ============================================================================ (6) dịch chuyển theo ngành
def sector_shift(feat: pd.DataFrame) -> pd.DataFrame:
    """Leave-one-sector-out: học trên 9 nhóm ngành, kiểm tra trên nhóm còn lại; so với dự báo OOF
    (in-distribution, ngành đó CÓ trong train) của cùng mô hình ở seed đầu."""
    cfg = _cfg()
    e = cfg["experiments"]["sector_shift"]
    seed = cfg["cv"]["seeds"][0]
    nb = cfg["experiments"]["ece_bins"]
    oof = np.load(OOF_DIR / f"oof_seed{seed}.npz")
    rows = []
    for g in sorted(feat["sector"].unique()):
        te = (feat["sector"] == g).to_numpy()
        fd = fold_data(feat, ~te, te)
        for n in e["models"]:
            m = build(n, seed=seed).fit(fd.train_f, fd.train_d, fd.y_train)
            p_out = m.predict_proba(fd.test_f, fd.test_d)
            p_in = oof[n][te]
            r = {"sector": g, "n_test": int(te.sum()), "default_rate": float(fd.y_test.mean()), "model": n}
            for tag, p in (("loso", p_out), ("in", p_in)):
                mm = M.all_metrics(fd.y_test, p, nb)
                r.update({f"{c}_{tag}": mm[c] for c in ("auc", "logloss", "brier", "ece")})
                r[f"citl_{tag}"] = float(p.mean() - fd.y_test.mean())  # calibration-in-the-large
            rows.append(r)
        _log(f"sector_shift: {g}")
    df = pd.DataFrame(rows)
    df.to_csv(_out("sector_shift") / "results.csv", index=False)
    return df


# ============================================================================ (7) nhất quán tri thức
MISSING_STATES = {"years_employed": "not_working", "bureau_inquiries_year": "unknown"}


def _levels(fd, f: str) -> tuple[list[str], list[float]]:
    states = [s for s in fd.disc.states()[f] if s != MISSING_STATES.get(f)]
    reps = [float(fd.train_f.loc[fd.train_d[f] == s, f].median()) for s in states]
    return states, reps


def consistency(feat: pd.DataFrame, sp: dict) -> pd.DataFrame:
    """ICE theo từng bậc của biến có hướng tác động tri thức rõ ràng; đếm tỷ lệ hồ sơ mà mô hình cho
    rủi ro đi NGƯỢC tri thức (bước ngược > tol), và hướng của đường phụ thuộc trung bình (PDP)."""
    cfg = _cfg()
    e = cfg["experiments"]["consistency"]
    exp_dir = cfg["expected_direction"]
    seed = cfg["cv"]["seeds"][0]
    tol = e["tol"]
    rows = []
    for k in range(cfg["cv"]["n_folds"]):
        fd = fold_data(feat, sp[seed] != k)
        fitted = _fitted(seed, k)
        rng = np.random.default_rng(2000 + k)
        sel = rng.choice(len(fd.y_test), min(e["n_rows"], len(fd.y_test)), replace=False)
        Xf, Xd = fd.test_f.iloc[sel], fd.test_d.iloc[sel]
        for f, direction in exp_dir.items():
            states, reps = _levels(fd, f)
            ok = (Xd[f] != MISSING_STATES.get(f, "__none__")).to_numpy()
            xf, xd = Xf[ok], Xd[ok]
            for n in e["models"]:
                P = np.column_stack([fitted[n].predict_proba(xf.assign(**{f: v}), xd.assign(**{f: s}))
                                     for s, v in zip(states, reps)])
                d = np.diff(P, axis=1)
                wrong = (d < -tol) if direction == "increasing" else (d > tol)
                pdp = P.mean(0)
                dp = np.diff(pdp)
                rows.append({"fold": k, "feature": f, "expected": direction, "model": n, "n_rows": int(ok.sum()),
                             "violation_rate": float(wrong.any(1).mean()),
                             "mean_wrong_step": float(np.where(wrong, np.abs(d), 0).sum(1).mean()),
                             "flat_rate": float((np.abs(P[:, -1] - P[:, 0]) < tol).mean()),
                             "pdp_monotone_ok": bool(np.all(dp >= 0) if direction == "increasing" else np.all(dp <= 0)),
                             "effect_first_to_last": float(pdp[-1] - pdp[0]),
                             "pdp": ";".join(f"{v:.4f}" for v in pdp)})
        _log(f"consistency: fold {k}")
    df = pd.DataFrame(rows)
    df.to_csv(_out("consistency") / "results.csv", index=False)
    return df


# ============================================================================ (8) ổn định giải thích
def _row_rank_corr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ra, rb = stats.rankdata(a, axis=1), stats.rankdata(b, axis=1)
    ra -= ra.mean(1, keepdims=True)
    rb -= rb.mean(1, keepdims=True)
    den = np.sqrt((ra ** 2).sum(1) * (rb ** 2).sum(1))
    return np.divide((ra * rb).sum(1), den, out=np.full(len(a), np.nan), where=den > 0)


def stability(feat: pd.DataFrame, sp: dict) -> pd.DataFrame:
    cfg = _cfg()
    e = cfg["experiments"]["stability"]
    seed = cfg["cv"]["seeds"][0]
    probe = feat.sample(e["n_probe"], random_state=seed)
    A: dict[str, list[np.ndarray]] = {n: [] for n in e["models"]}
    for k in range(cfg["cv"]["n_folds"]):
        fd = fold_data(feat, sp[seed] != k)
        fitted = _fitted(seed, k)
        Xd = fd.disc.transform(probe).drop(columns="default")
        for n in e["models"]:
            A[n].append(attribution(fitted[n], probe, Xd, fd.train_f, fd.train_d))
        _log(f"stability: fold {k}")
    rows, imp = [], []
    K = cfg["cv"]["n_folds"]
    for n, mats in A.items():
        g_imp = [np.abs(a).mean(0) for a in mats]
        for k in range(K):
            imp.append({"model": n, "fold": k, **dict(zip(GROUP_NAMES, g_imp[k]))})
        for i in range(K):
            for j in range(i + 1, K):
                a, b = mats[i], mats[j]
                top_a, top_b = np.argsort(-np.abs(a), 1)[:, :3], np.argsort(-np.abs(b), 1)[:, :3]
                jac = np.mean([len(set(x) & set(y)) / len(set(x) | set(y)) for x, y in zip(top_a, top_b)])
                sign = np.mean(np.sign(np.take_along_axis(a, top_a, 1)) == np.sign(np.take_along_axis(b, top_a, 1)))
                rows.append({"model": n, "fold_i": i, "fold_j": j,
                             "global_rank_corr": stats.spearmanr(g_imp[i], g_imp[j]).statistic,
                             "local_rank_corr": float(np.nanmean(_row_rank_corr(np.abs(a), np.abs(b)))),
                             "top3_jaccard": float(jac), "top3_sign_agree": float(sign),
                             "attr_mad": float(np.abs(a - b).mean())})
    df = pd.DataFrame(rows)
    out = _out("stability")
    df.to_csv(out / "results.csv", index=False)
    pd.DataFrame(imp).to_csv(out / "global_importance.csv", index=False)
    return df


# ============================================================================ (9) chi phí
def cost() -> pd.DataFrame:
    res = pd.read_csv(path("experiments", "main_cv", "results.csv"))
    df = res.groupby(["model", "family"]).agg(fit_s=("fit_s", "mean"), fit_s_std=("fit_s", "std"),
                                              pred_s_per_10k=("pred_s_per_10k", "mean"),
                                              n_params=("n_params", "mean"), size_kb=("size_kb", "mean"),
                                              n_train=("n_train", "mean")).reset_index().sort_values("fit_s")
    df.to_csv(_out("cost") / "results.csv", index=False)
    return df


# ============================================================================ độ nhạy λ + what-if
def lambda_sensitivity(feat: pd.DataFrame, sp: dict) -> pd.DataFrame:
    cfg = _cfg()
    seed = cfg["cv"]["seeds"][0]
    nb = cfg["experiments"]["ece_bins"]
    rows = []
    for k in range(cfg["cv"]["n_folds"]):
        fd = fold_data(feat, sp[seed] != k)
        working = np.flatnonzero((fd.test_d["years_employed"] != "not_working").to_numpy())
        sel = np.random.default_rng(3000 + k).choice(working, 2000, replace=False)
        xd = fd.test_d.iloc[sel]
        for lam in cfg["experiments"]["lambda"]:
            m = BNModel("BN-Expert-Mono", seed=seed, lam=lam).fit(fd.train_f, fd.train_d, fd.y_train)
            p = m.predict_proba(fd.test_f, fd.test_d)
            r = {"fold": k, "lambda": lam, **M.all_metrics(fd.y_test, p, nb), "pi_shock": m.bn.meta["pi_shock"],
                 "n_p0_clipped": m.bn.meta["n_p0_clipped"]}
            base = to_score(m.bn.predict_proba(xd))
            for ev, val in (("job_loss", "yes"), ("health_shock", "yes"), ("cashflow_shock", "yes"),
                            ("econ_cycle", "downturn"), ("inflation", "high")):
                r[f"dscore_{ev}"] = float((to_score(m.bn.predict_proba(xd.assign(**{ev: val}))) - base).mean())
            rows.append(r)
        _log(f"lambda: fold {k}")
    df = pd.DataFrame(rows)
    df.to_csv(_out("lambda_sensitivity") / "results.csv", index=False)
    return df


# ============================================================================ điều phối
ALL = ["main_cv", "significance", "missing", "learning_curve", "sector_shift", "consistency", "stability",
       "cost", "lambda", "german", "figures", "tables"]


def main(which: list[str] | None = None) -> None:
    utf8_stdout()
    which = which or ALL
    need_data = {"main_cv", "missing", "learning_curve", "sector_shift", "consistency", "stability", "lambda"}
    feat, sp = _data() if need_data & set(which) else (None, None)
    t0 = time.time()
    for w in which:
        t = time.time()
        if w == "main_cv":
            main_cv(feat, sp)
        elif w == "significance":
            significance()
        elif w == "missing":
            missing(feat, sp)
        elif w == "learning_curve":
            learning_curve(feat, sp)
        elif w == "sector_shift":
            sector_shift(feat)
        elif w == "consistency":
            consistency(feat, sp)
        elif w == "stability":
            stability(feat, sp)
        elif w == "cost":
            cost()
        elif w == "lambda":
            lambda_sensitivity(feat, sp)
        elif w == "german":
            from src.evaluation.german import run as german

            german()
        elif w == "figures":
            from src.evaluation.figures import main as figs

            figs()
        elif w == "tables":
            from src.evaluation.tables import main as tables

            tables()
        else:
            raise SystemExit(f"Không có thí nghiệm '{w}'. Chọn trong: {ALL}")
        _log(f"== {w} xong trong {time.time() - t:.0f}s")
    _log(f"Tổng {time.time() - t0:.0f}s")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:] or None)

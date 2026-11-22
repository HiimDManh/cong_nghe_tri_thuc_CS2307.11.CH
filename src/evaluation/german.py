"""Thí nghiệm (5b) – dữ liệu ít trên German Credit (1.000 hồ sơ): BN chuyên gia nhỏ vs NB/TAN vs ML.

10 lần lặp × stratified 5-fold; với mỗi fold học trên 25% / 50% / 100% tập train (200 / 400 / 800 hồ sơ).
"""
from __future__ import annotations

import time
import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.bn.core import DiscreteBN
from src.common import load_config, path
from src.evaluation import metrics as M

NUM = ["duration", "credit_amount", "age", "installment_commitment", "existing_credits", "num_dependents",
       "residence_since"]


def load() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    raw = pd.read_csv(path("data", "raw", "german_credit.csv"))
    cfg = load_config("german_bn")
    y = (raw["class"] == "bad").astype(int).to_numpy()
    disc = pd.DataFrame(index=raw.index)
    for c, s in cfg["discretize"].items():
        disc[c] = pd.cut(raw[c], [-np.inf, *s["edges"], np.inf], right=False, labels=s["labels"]).astype(str)
    for c in cfg["categorical"]:
        disc[c] = raw[c].astype(str)
    return raw.drop(columns="class"), disc, y


def _states(disc: pd.DataFrame) -> dict[str, list[str]]:
    cfg = load_config("german_bn")
    st = {c: list(s["labels"]) for c, s in cfg["discretize"].items()}
    st.update({c: sorted(disc[c].unique()) for c in cfg["categorical"]})
    st["default"] = ["0", "1"]
    return st


def fit_bn(kind: str, D: pd.DataFrame, states: dict[str, list[str]]) -> DiscreteBN:
    nodes = list(states)
    if kind == "BN-Expert":
        parents = {n: [] for n in nodes}
        for p, c, *_ in load_config("german_bn")["edges"]:
            parents[c].append(p)
    elif kind == "Naive Bayes":
        parents = {n: ([] if n == "default" else ["default"]) for n in nodes}
    else:  # TAN
        from pgmpy.estimators import TreeSearch

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            dag = TreeSearch(D[nodes]).estimate(estimator_type="tan", class_node="default", show_progress=False)
        parents = {n: [] for n in nodes}
        for p, c in dag.edges():
            parents[c].append(p)
    return DiscreteBN(states, parents).fit(D, ess=10.0)


def _ml(kind: str, seed: int):
    if kind == "LR":
        return LogisticRegression(max_iter=2000)
    if kind == "RF":
        return RandomForestClassifier(n_estimators=300, min_samples_leaf=5, random_state=seed, n_jobs=-1)
    from xgboost import XGBClassifier

    return XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                         random_state=seed, n_jobs=4, verbosity=0)


def run() -> pd.DataFrame:
    cfg = load_config("german_bn")["cv"]
    X, D, y = load()
    states = _states(D)
    D = D.assign(default=y.astype(str))
    cat = [c for c in X.columns if c not in NUM]
    rows = []
    t0 = time.time()
    for rep in range(cfg["repeats"]):
        for k, (tr, te) in enumerate(StratifiedKFold(cfg["n_folds"], shuffle=True, random_state=rep).split(X, y)):
            for frac in cfg["fractions"]:
                rng = np.random.default_rng(rep * 100 + k)
                sub = tr if frac == 1.0 else np.concatenate(
                    [rng.choice(tr[y[tr] == c], int(round(frac * (y[tr] == c).sum())), replace=False) for c in (0, 1)])
                for kind in ("BN-Expert", "Naive Bayes", "TAN"):
                    bn = fit_bn(kind, D.iloc[sub], states)
                    p = bn.predict_proba(D.iloc[te].drop(columns="default"))
                    rows.append({"repeat": rep, "fold": k, "fraction": frac, "n_train": len(sub), "model": kind,
                                 **M.all_metrics(y[te], p, 10)})
                pre = ColumnTransformer([("num", StandardScaler(), NUM),
                                         ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat)])
                A, B = pre.fit_transform(X.iloc[sub]), pre.transform(X.iloc[te])
                for kind in ("LR", "XGBoost", "RF"):
                    p = _ml(kind, rep).fit(A, y[sub]).predict_proba(B)[:, 1]
                    rows.append({"repeat": rep, "fold": k, "fraction": frac, "n_train": len(sub), "model": kind,
                                 **M.all_metrics(y[te], p, 10)})
    df = pd.DataFrame(rows)
    out = path("experiments", "german_small_data")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "results.csv", index=False)
    print(f"[german] {len(df)} dòng trong {time.time() - t0:.0f}s -> {out}")
    return df

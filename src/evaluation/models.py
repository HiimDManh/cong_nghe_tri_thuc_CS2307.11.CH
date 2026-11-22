"""Sổ đăng ký mô hình cho thực nghiệm: mọi mô hình có cùng giao diện
`fit(Xf, Xd, y)` / `predict_proba(Xf, Xd)` (Xf = đặc trưng liên tục, Xd = trạng thái rời rạc)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.baselines.fico import FicoScorer
from src.baselines.ml import MLModel
from src.bn import variants as V
from src.bn.core import DiscreteBN
from src.bn.model import fit_expert_bn


class FicoModel:
    family = "rule"

    def __init__(self) -> None:
        self.name = "FICO"
        self.m = FicoScorer()

    def fit(self, Xf: pd.DataFrame, Xd: pd.DataFrame, y: np.ndarray) -> "FicoModel":
        self.m.fit(Xd, y)
        return self

    def predict_proba(self, Xf: pd.DataFrame, Xd: pd.DataFrame) -> np.ndarray:
        return self.m.predict_proba(Xd)


class BNModel:
    family = "bn"

    def __init__(self, name: str, seed: int = 42, lam: float | None = None) -> None:
        self.name, self.seed, self.lam = name, seed, lam
        self.bn: DiscreteBN | None = None

    def fit(self, Xf: pd.DataFrame, Xd: pd.DataFrame, y: np.ndarray) -> "BNModel":
        D = Xd.assign(default=np.asarray(y).astype(int).astype(str))
        n = self.name
        if n in ("BN-Expert", "BN-Expert-Mono"):
            self.bn = fit_expert_bn(D, Xf, monotone=n.endswith("Mono"), lam=self.lam)
        elif n == "Naive Bayes":
            self.bn = V.naive_bayes(D)
        elif n == "TAN":
            self.bn = V.tan(D, seed=self.seed)
        elif n == "BN-Learned":
            self.bn = V.hill_climb(D, hybrid=False, seed=self.seed)
        elif n == "BN-Hybrid":
            self.bn = V.hill_climb(D, hybrid=True, seed=self.seed)
        else:
            raise KeyError(n)
        return self

    def predict_proba(self, Xf: pd.DataFrame, Xd: pd.DataFrame) -> np.ndarray:
        return self.bn.predict_proba(Xd)


ML_SPECS = {
    "LR": ("lr", "cont", False), "LR-disc": ("lr", "disc", False),
    "XGBoost": ("xgboost", "cont", False), "XGBoost-disc": ("xgboost", "disc", False),
    "XGBoost-Mono": ("xgboost", "cont", True), "LightGBM": ("lightgbm", "cont", False),
    "RF": ("rf", "cont", False), "MLP": ("mlp", "cont", False),
}


def build(name: str, seed: int = 42, lam: float | None = None):
    if name == "FICO":
        return FicoModel()
    if name in ML_SPECS:
        algo, kind, mono = ML_SPECS[name]
        return MLModel(name, algo, kind, monotone=mono, seed=seed)
    return BNModel(name, seed=seed, lam=lam)


def n_params(model) -> int:
    """Số tham số tự do (BN: Σ (r−1)·q; ML: hệ số / số lá; FICO: số điểm luật + 2 tham số Platt)."""
    if isinstance(model, BNModel):
        return int(sum(c[..., :-1].size for c in model.bn.cpts.values()))
    if isinstance(model, FicoModel):
        return int(sum(len(c["points"]) for f in model.m.config["factors"].values()
                       for c in f["components"].values()) + 2)
    est = model.est
    if model.algo == "lr":
        return int(est.coef_.size + 1)
    if model.algo == "xgboost":
        df = est.get_booster().trees_to_dataframe()
        return int((df["Feature"] == "Leaf").sum() + (df["Feature"] != "Leaf").sum() * 2)
    if model.algo == "lightgbm":
        d = est.booster_.dump_model()["tree_info"]
        return int(sum(t["num_leaves"] * 3 - 2 for t in d))
    if model.algo == "rf":
        return int(sum(t.tree_.node_count for t in est.estimators_))
    if model.algo == "mlp":
        return int(sum(w.size for w in est.coefs_) + sum(b.size for b in est.intercepts_))
    return -1

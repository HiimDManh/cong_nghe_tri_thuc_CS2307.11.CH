"""Chỉ số đánh giá: phân biệt (AUC, PR-AUC, Gini, KS), hiệu chỉnh (Brier, Log-loss, ECE),
kiểm định (DeLong, paired bootstrap, t-test hiệu chỉnh Nadeau–Bengio)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score, roc_curve

EPS = 1e-7


def ece(y: np.ndarray, p: np.ndarray, n_bins: int = 15) -> float:
    """Expected Calibration Error với bin cùng số mẫu (equal-mass)."""
    order = np.argsort(p, kind="stable")
    bins = np.array_split(order, n_bins)
    return float(sum(len(b) * abs(y[b].mean() - p[b].mean()) for b in bins) / len(p))


def ks(y: np.ndarray, p: np.ndarray) -> float:
    fpr, tpr, _ = roc_curve(y, p)
    return float(np.max(tpr - fpr))


def all_metrics(y: np.ndarray, p: np.ndarray, n_bins: int = 15) -> dict[str, float]:
    y = np.asarray(y).astype(int)
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    auc = roc_auc_score(y, p)
    return {"auc": auc, "pr_auc": average_precision_score(y, p), "gini": 2 * auc - 1, "ks": ks(y, p),
            "brier": brier_score_loss(y, p), "logloss": log_loss(y, p, labels=[0, 1]), "ece": ece(y, p, n_bins)}


def reliability(y: np.ndarray, p: np.ndarray, n_bins: int = 15) -> pd.DataFrame:
    order = np.argsort(p, kind="stable")
    rows = [{"p_mean": p[b].mean(), "y_rate": y[b].mean(), "n": len(b)} for b in np.array_split(order, n_bins)]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------- DeLong
def _midrank(x: np.ndarray) -> np.ndarray:
    return stats.rankdata(x, method="average")


def delong(y: np.ndarray, p1: np.ndarray, p2: np.ndarray) -> dict[str, float]:
    """Kiểm định DeLong cho hai AUC tương quan (Sun & Xu 2014, cài đặt O(n log n))."""
    y = np.asarray(y).astype(bool)
    m, n = y.sum(), (~y).sum()
    aucs, v10, v01 = [], [], []
    for p in (p1, p2):
        pos, neg = p[y], p[~y]
        tx, ty, tz = _midrank(pos), _midrank(neg), _midrank(np.concatenate([pos, neg]))
        auc = (tz[:m].sum() - m * (m + 1) / 2) / (m * n)
        aucs.append(auc)
        v10.append((tz[:m] - tx) / n)
        v01.append(1 - (tz[m:] - ty) / m)
    s10, s01 = np.cov(np.vstack(v10)), np.cov(np.vstack(v01))
    var = (s10[0, 0] + s10[1, 1] - 2 * s10[0, 1]) / m + (s01[0, 0] + s01[1, 1] - 2 * s01[0, 1]) / n
    z = (aucs[0] - aucs[1]) / np.sqrt(var) if var > 0 else 0.0
    return {"auc1": aucs[0], "auc2": aucs[1], "diff": aucs[0] - aucs[1], "z": z,
            "p_value": float(2 * stats.norm.sf(abs(z)))}


# ---------------------------------------------------------------------------------------------- bootstrap
def paired_bootstrap(y: np.ndarray, p_ref: np.ndarray, p_other: np.ndarray, n: int = 1000, seed: int = 42,
                     n_bins: int = 15) -> dict[str, float]:
    """CI 95% của chênh lệch (ref − other) cho Brier, Log-loss, ECE bằng paired bootstrap.

    ECE: bin cố định (equal-mass theo từng mô hình trên mẫu gốc) để mỗi lần lặp chỉ cần bincount.
    """
    rng = np.random.default_rng(seed)
    y = np.asarray(y).astype(float)
    N = len(y)
    out = {}
    per_row = {}
    for k, p in (("ref", p_ref), ("other", p_other)):
        p = np.clip(p, EPS, 1 - EPS)
        per_row[k] = {"brier": (p - y) ** 2, "logloss": -(y * np.log(p) + (1 - y) * np.log(1 - p))}
        edges = np.quantile(p, np.linspace(0, 1, n_bins + 1)[1:-1])
        per_row[k]["bin"] = np.searchsorted(edges, p, side="right")
        per_row[k]["p"] = p
    diffs = {m: np.empty(n) for m in ("brier", "logloss", "ece")}

    def _ece(idx: np.ndarray, k: str) -> float:
        b = per_row[k]["bin"][idx]
        cnt = np.bincount(b, minlength=n_bins)
        sy = np.bincount(b, weights=y[idx], minlength=n_bins)
        sp = np.bincount(b, weights=per_row[k]["p"][idx], minlength=n_bins)
        return float(np.abs(sy - sp).sum() / len(idx))

    for i in range(n):
        idx = rng.integers(0, N, N)
        for m in ("brier", "logloss"):
            diffs[m][i] = per_row["ref"][m][idx].mean() - per_row["other"][m][idx].mean()
        diffs["ece"][i] = _ece(idx, "ref") - _ece(idx, "other")
    full = np.arange(N)
    for m in ("brier", "logloss", "ece"):
        point = (per_row["ref"][m].mean() - per_row["other"][m].mean()) if m != "ece" else \
            _ece(full, "ref") - _ece(full, "other")
        lo, hi = np.percentile(diffs[m], [2.5, 97.5])
        out[f"d_{m}"], out[f"d_{m}_lo"], out[f"d_{m}_hi"] = point, lo, hi
    return out


def corrected_ttest(diffs: np.ndarray, n_train: int, n_test: int) -> float:
    """t-test lặp lại có hiệu chỉnh phương sai (Nadeau & Bengio 2003) cho k-fold × r lần. Trả p-value 2 phía."""
    d = np.asarray(diffs, dtype=float)
    k = len(d)
    var = d.var(ddof=1)
    if var == 0:
        return 0.0 if d.mean() != 0 else 1.0
    t = d.mean() / np.sqrt((1 / k + n_test / n_train) * var)
    return float(2 * stats.t.sf(abs(t), df=k - 1))


def holm(pvals: list[float]) -> list[float]:
    """Hiệu chỉnh Holm–Bonferroni cho nhiều phép so sánh."""
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (len(p) - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj.tolist()

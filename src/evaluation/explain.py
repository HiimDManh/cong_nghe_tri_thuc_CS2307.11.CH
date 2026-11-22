"""Giải thích cục bộ theo NHÓM BIẾN (13 nút đầu vào của BN), trong không gian log-odds.

- BN / FICO: "che bằng chứng" (occlusion) – đóng góp của nhóm g = logit p(x) − logit p(x \\ g).
  Với BN, bỏ bằng chứng = lấy biên chính xác (không cần giá trị thay thế) – cách giải thích tự nhiên của BN.
  Với FICO, bỏ bằng chứng = điểm thành phần 'missing' (0.5) của luật.
- XGBoost / LightGBM: TreeSHAP (pred_contribs của thư viện), cộng các cột one-hot về nhóm biến.
- LR: SHAP tuyến tính = hệ số × (x − trung bình train) trong không gian đã biến đổi.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.baselines.ml import GROUPS, MLModel, group_of

GROUP_NAMES = list(GROUPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-7, 1 - 1e-7)
    return np.log(p / (1 - p))


def mask(Xf: pd.DataFrame, Xd: pd.DataFrame, m: np.ndarray, groups: list[str] | None = None
         ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Che (NaN) nhóm biến groups[j] ở các dòng m[:, j] trên CẢ hai dạng dữ liệu."""
    groups = groups or GROUP_NAMES
    Xf, Xd = Xf.copy(), Xd.copy()
    if "not_working" not in Xf:
        Xf["not_working"] = Xf["years_employed"].isna().astype(float)
        Xf["years_employed"] = Xf["years_employed"].fillna(0.0)
    for c in ("sector", "occupation_group", "education"):
        Xf[c] = Xf[c].astype(object)
    for j, g in enumerate(groups):
        rows = m[:, j]
        if not rows.any():
            continue
        for c in GROUPS[g]["cont"]:
            Xf.loc[rows, c] = np.nan
        for c in GROUPS[g]["disc"]:
            Xd.loc[rows, c] = np.nan
    return Xf, Xd


def occlusion(model, Xf: pd.DataFrame, Xd: pd.DataFrame) -> np.ndarray:
    """(n, 13) đóng góp log-odds của từng nhóm biến bằng cách che bằng chứng."""
    base = logit(model.predict_proba(Xf, Xd))
    out = np.zeros((len(Xd), len(GROUP_NAMES)))
    for j, g in enumerate(GROUP_NAMES):
        m = np.zeros((len(Xd), len(GROUP_NAMES)), bool)
        m[:, j] = True
        f2, d2 = mask(Xf, Xd, m)
        out[:, j] = base - logit(model.predict_proba(f2, d2))
    return np.nan_to_num(out)


def baseline_attribution(model, Xf: pd.DataFrame, Xd: pd.DataFrame, train_d: pd.DataFrame) -> np.ndarray:
    """(n, 13) đóng góp log-odds so với mức phổ biến (chỉ dùng trạng thái rời rạc -> cho BN và FICO)."""
    base = logit(model.predict_proba(Xf, Xd))
    out = np.zeros((len(Xd), len(GROUP_NAMES)))
    for j, g in enumerate(GROUP_NAMES):
        col = GROUPS[g]["disc"][0]
        freq = train_d[col].value_counts(normalize=True, dropna=True)
        ref = sum(w * logit(model.predict_proba(Xf, Xd.assign(**{col: s}))) for s, w in freq.items())
        out[:, j] = np.where(Xd[col].isna().to_numpy(), 0.0, base - ref)
    return out


def _aggregate(contrib: np.ndarray, names: list[str]) -> np.ndarray:
    out = np.zeros((contrib.shape[0], len(GROUP_NAMES)))
    for k, n in enumerate(names):
        out[:, GROUP_NAMES.index(group_of(n))] += contrib[:, k]
    return out


def ml_attribution(model: MLModel, Xf: pd.DataFrame, Xd: pd.DataFrame, train_mean: np.ndarray | None = None
                   ) -> np.ndarray:
    A = model.transform(Xf, Xd)
    names = model.feature_names()
    if model.algo == "xgboost":
        import xgboost as xgb

        c = model.est.get_booster().predict(xgb.DMatrix(A), pred_contribs=True)[:, :-1]
    elif model.algo == "lightgbm":
        c = model.est.predict(A, pred_contrib=True)[:, :-1]
    elif model.algo == "lr":
        mu = train_mean if train_mean is not None else A.mean(0)
        c = (A - mu) * model.est.coef_[0]
    else:
        raise ValueError(f"Không hỗ trợ giải thích cho {model.algo}")
    return _aggregate(np.asarray(c), names)


def attribution(model, Xf: pd.DataFrame, Xd: pd.DataFrame, train_f: pd.DataFrame | None = None,
                train_d: pd.DataFrame | None = None) -> np.ndarray:
    if isinstance(model, MLModel):
        mu = model.transform(train_f, train_d).mean(0) if (model.algo == "lr" and train_f is not None) else None
        return ml_attribution(model, Xf, Xd, mu)
    if train_d is None:
        return occlusion(model, Xf, Xd)
    return baseline_attribution(model, Xf, Xd, train_d)

"""Chia fold dùng chung cho MỌI mô hình: stratified k-fold × nhiều seed, lưu ra file để tái lập.

Rời rạc hóa (ngưỡng quantile) được fit lại trên TRAIN của từng fold trong `fold_data` -> không rò rỉ.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from src.common import load_config, path
from src.data.discretize import Discretizer


def make_splits(ids: np.ndarray, y: np.ndarray, n_folds: int, seeds: list[int]) -> dict[int, np.ndarray]:
    """{seed: mảng fold_id (0..k-1) cho từng dòng}."""
    out = {}
    for s in seeds:
        f = np.empty(len(y), dtype=np.int8)
        for k, (_, te) in enumerate(StratifiedKFold(n_folds, shuffle=True, random_state=s).split(ids, y)):
            f[te] = k
        out[s] = f
    return out


def load_splits(feat: pd.DataFrame) -> dict[int, np.ndarray]:
    """Đọc split đã lưu (tạo mới nếu chưa có). Kiểm tra khớp id để tránh dùng nhầm split."""
    cfg = load_config("eval")["cv"]
    f = path(cfg["splits_file"])
    if f.exists():
        z = np.load(f)
        if np.array_equal(z["id"], feat["id"].to_numpy()):
            return {int(k[5:]): z[k] for k in z.files if k.startswith("fold_")}
        raise ValueError(f"{f} không khớp dữ liệu hiện tại – xóa file để tạo lại")
    sp = make_splits(feat["id"].to_numpy(), feat["default"].to_numpy(), cfg["n_folds"], cfg["seeds"])
    f.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, id=feat["id"].to_numpy(), **{f"fold_{s}": v for s, v in sp.items()})
    return sp


@dataclass
class FoldData:
    """Dữ liệu một fold ở cả hai dạng: liên tục (`*_f`) và rời rạc (`*_d`, không có cột default)."""
    train_f: pd.DataFrame
    test_f: pd.DataFrame
    train_d: pd.DataFrame
    test_d: pd.DataFrame
    y_train: np.ndarray
    y_test: np.ndarray
    test_idx: np.ndarray
    disc: Discretizer


def fold_data(feat: pd.DataFrame, train_mask: np.ndarray, test_mask: np.ndarray | None = None) -> FoldData:
    test_mask = ~train_mask if test_mask is None else test_mask
    tr, te = feat[train_mask], feat[test_mask]
    disc = Discretizer().fit(tr)
    dtr, dte = disc.transform(tr), disc.transform(te)
    return FoldData(tr, te, dtr.drop(columns="default"), dte.drop(columns="default"),
                    tr["default"].to_numpy(), te["default"].to_numpy(), np.flatnonzero(test_mask), disc)

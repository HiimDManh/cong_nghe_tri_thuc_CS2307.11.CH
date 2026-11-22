"""Baseline FICO rule-based (đề tài trước) trên đặc trưng đã rời rạc hóa.

Điểm tất định theo luật trong `configs/fico.yaml`. Để so sánh các chỉ số xác suất (Brier, ECE…),
`fit` chỉ học ánh xạ đơn điệu điểm -> P(vỡ nợ) bằng hồi quy logistic 1 biến (Platt scaling).
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from src.common import load_config


class FicoScorer:
    """Chấm điểm 300–850 theo 5 nhóm yếu tố FICO và quy đổi sang xác suất vỡ nợ."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or load_config("fico")
        lo, hi = self.config["score_range"]
        self.lo, self.span = lo, hi - lo
        total = sum(f["weight"] for f in self.config["factors"].values())
        if not np.isclose(total, 1.0):
            raise ValueError(f"Tổng trọng số nhóm = {total}, phải = 1")
        self._platt: LogisticRegression | None = None

    def factor_scores(self, X: pd.DataFrame) -> pd.DataFrame:
        """Điểm thành phần ∈ [0,1] của từng nhóm yếu tố (dùng cho giải thích)."""
        out = {}
        for name, f in self.config["factors"].items():
            s = np.zeros(len(X))
            for col, c in f["components"].items():
                pts = X[col].map(c["points"]).astype(float).fillna(c["missing"]).to_numpy()
                s += c["weight"] * pts
            out[name] = s
        return pd.DataFrame(out, index=X.index)

    def score(self, X: pd.DataFrame) -> np.ndarray:
        fs = self.factor_scores(X)
        w = np.array([f["weight"] for f in self.config["factors"].values()])
        return self.lo + self.span * fs.to_numpy() @ w

    def fit(self, X: pd.DataFrame, y: pd.Series | np.ndarray) -> "FicoScorer":
        """Chỉ fit Platt scaling (luật chấm điểm không đổi)."""
        self._platt = LogisticRegression().fit(self.score(X).reshape(-1, 1), np.asarray(y).astype(int))
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """P(vỡ nợ). Chưa fit -> ánh xạ tuyến tính ngược (chỉ dùng cho xếp hạng)."""
        s = self.score(X)
        if self._platt is None:
            return 1 - (s - self.lo) / self.span
        return self._platt.predict_proba(s.reshape(-1, 1))[:, 1]

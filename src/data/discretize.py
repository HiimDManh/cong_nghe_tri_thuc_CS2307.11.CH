"""Rời rạc hóa đặc trưng theo `configs/discretize.yaml`.

`Discretizer.fit` chỉ học ngưỡng quantile trên tập train (gọi lại cho mỗi fold CV);
ngưỡng nghiệp vụ (`fixed`) không phụ thuộc dữ liệu.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.common import load_config

ASSET_LABELS = {(0, 0): "none", (0, 1): "car", (1, 0): "realty", (1, 1): "both"}


class Discretizer:
    """Biến bảng đặc trưng nghiệp vụ thành bảng trạng thái rời rạc (chuỗi) cho BN."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or load_config("discretize")["features"]
        self.edges_: dict[str, list[float]] = {}

    @property
    def features(self) -> list[str]:
        return list(self.config)

    def fit(self, df: pd.DataFrame) -> "Discretizer":
        for name, spec in self.config.items():
            if spec["method"] == "fixed":
                self.edges_[name] = list(spec["edges"])
            elif spec["method"] == "quantile":
                qs = np.linspace(0, 1, spec["n_bins"] + 1)[1:-1]
                edges = np.unique(df[name].dropna().quantile(qs).to_numpy())
                if len(edges) != spec["n_bins"] - 1:
                    raise ValueError(f"{name}: quantile trùng nhau, giảm n_bins")
                self.edges_[name] = edges.tolist()
        return self

    def _bin(self, s: pd.Series, name: str, spec: dict[str, Any]) -> pd.Series:
        edges = [-np.inf, *self.edges_[name], np.inf]
        out = pd.cut(s, edges, right=False, labels=spec["labels"]).astype(object)
        if "missing_state" in spec:
            out = out.where(s.notna(), spec["missing_state"])
        return out

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.edges_ and any(s["method"] in ("fixed", "quantile") for s in self.config.values()):
            raise RuntimeError("Gọi fit() trước")
        out = pd.DataFrame(index=df.index)
        for name, spec in self.config.items():
            m = spec["method"]
            if m in ("fixed", "quantile"):
                out[name] = self._bin(df[name], name, spec)
            elif m == "categorical":
                out[name] = df[name].astype(object).where(df[name].notna(), None).map(
                    lambda v: None if v is None else str(v))
            elif m == "derived" and name == "assets":
                out[name] = [ASSET_LABELS[(r, c)] for r, c in zip(df["own_realty"], df["own_car"])]
            else:
                raise ValueError(f"Không hỗ trợ {name}: {m}")
        if "default" in df:
            out["default"] = df["default"].astype(int).astype(str)
        return out

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)

    def states(self) -> dict[str, list[str]]:
        """Danh sách trạng thái của từng nút (dùng để khai báo state_names cho pgmpy)."""
        st: dict[str, list[str]] = {}
        for name, spec in self.config.items():
            if "labels" in spec:
                st[name] = list(spec["labels"]) + ([spec["missing_state"]] if "missing_state" in spec else [])
        st["assets"] = list(ASSET_LABELS.values())
        return st

    def save(self, f: Path) -> None:
        f.write_text(json.dumps(self.edges_, indent=2), encoding="utf-8")

    def load(self, f: Path) -> "Discretizer":
        self.edges_ = json.loads(f.read_text(encoding="utf-8"))
        return self

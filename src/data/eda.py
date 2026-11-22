"""EDA nhanh cho German Credit -> `reports/eda/german_credit.md` + hình trong `reports/figures/`.

Mục đích: nắm phân phối, tỷ lệ vỡ nợ theo nhóm, và độ liên hệ của từng biến với nhãn
(Cramér's V) để làm đầu vào cho thiết kế cấu trúc BN-Expert. Không có logic mô hình ở đây.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from src.common import load_config, path, utf8_stdout

NUMERIC_BINS = 5  # chỉ dùng để tính Cramér's V cho biến số, không phải rời rạc hóa chính thức


def load_german() -> pd.DataFrame:
    """Đọc German Credit thô và thêm cột `default` (1 = bad)."""
    cfg = load_config("data")
    g = cfg["datasets"]["german_credit"]
    df = pd.read_csv(path(cfg["paths"]["raw"], g["raw_file"]))
    df["default"] = (df[g["target"]] == g["positive_label"]).astype(int)
    return df.drop(columns=[g["target"]])


def cramers_v(x: pd.Series, y: pd.Series) -> float:
    """Cramér's V có hiệu chỉnh độ lệch (Bergsma 2013)."""
    table = pd.crosstab(x, y)
    if table.shape[0] < 2 or table.shape[1] < 2:
        return 0.0
    chi2 = chi2_contingency(table, correction=False)[0]
    n = table.values.sum()
    r, k = table.shape
    phi2 = max(0.0, chi2 / n - (k - 1) * (r - 1) / (n - 1))
    rc, kc = r - (r - 1) ** 2 / (n - 1), k - (k - 1) ** 2 / (n - 1)
    denom = min(kc - 1, rc - 1)
    return float(np.sqrt(phi2 / denom)) if denom > 0 else 0.0


def run() -> None:
    utf8_stdout()
    df = load_german()
    out_md = path("reports", "eda", "german_credit.md")
    fig_dir = path("reports", "figures")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    features = [c for c in df.columns if c != "default"]
    numeric = [c for c in features if pd.api.types.is_numeric_dtype(df[c])]
    categorical = [c for c in features if c not in numeric]

    # Độ liên hệ với nhãn
    assoc = []
    for c in features:
        x = pd.qcut(df[c], NUMERIC_BINS, duplicates="drop") if c in numeric else df[c]
        assoc.append({"feature": c, "type": "numeric" if c in numeric else "categorical",
                      "n_levels": int(df[c].nunique()), "cramers_v": round(cramers_v(x, df["default"]), 3)})
    assoc_df = pd.DataFrame(assoc).sort_values("cramers_v", ascending=False)

    lines: list[str] = [
        "# EDA nhanh – German Credit (OpenML `credit-g`)",
        "",
        "_Sinh tự động bởi `python -m src.data.eda`. Không sửa tay._",
        "",
        f"- Số dòng × cột: **{df.shape[0]} × {df.shape[1] - 1}** (+ nhãn)",
        f"- Tỷ lệ vỡ nợ (`class == bad`): **{df['default'].mean():.1%}**",
        f"- Giá trị thiếu: **{int(df.isna().sum().sum())}**",
        f"- Biến số ({len(numeric)}): {', '.join(numeric)}",
        f"- Biến phân loại ({len(categorical)}): {', '.join(categorical)}",
        "",
        "## Độ liên hệ với nhãn vỡ nợ (Cramér's V, biến số chia 5 quantile)",
        "",
        assoc_df.to_markdown(index=False),
        "",
        "## Thống kê biến số",
        "",
        df[numeric].describe().T.round(2).to_markdown(),
        "",
    ]

    for c in ["job", "employment", "purpose", "credit_history", "checking_status", "savings_status"]:
        t = df.groupby(c, observed=True)["default"].agg(n="size", default_rate="mean").sort_values("default_rate")
        t["default_rate"] = t["default_rate"].round(3)
        lines += [f"## Tỷ lệ vỡ nợ theo `{c}`", "", t.to_markdown(), ""]

    # Hình 1: tỷ lệ vỡ nợ theo job & employment
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    for ax, c in zip(axes, ["job", "employment"]):
        t = df.groupby(c, observed=True)["default"].mean().sort_values()
        ax.barh(t.index.astype(str), t.values, color="#4C72B0")
        ax.axvline(df["default"].mean(), color="gray", ls="--", lw=1, label="trung bình")
        ax.set_title(f"Tỷ lệ vỡ nợ theo {c}")
        ax.set_xlabel("P(default)")
        ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "eda_german_default_by_job.png", dpi=130)
    plt.close(fig)

    # Hình 2: phân phối biến số chính theo nhãn
    cols = [c for c in ["duration", "credit_amount", "age"] if c in numeric]
    fig, axes = plt.subplots(1, len(cols), figsize=(4 * len(cols), 3.4))
    for ax, c in zip(np.atleast_1d(axes), cols):
        for lbl, color in [(0, "#4C72B0"), (1, "#DD8452")]:
            ax.hist(df.loc[df["default"] == lbl, c], bins=25, alpha=0.6, density=True, color=color,
                    label="bad" if lbl else "good")
        ax.set_title(c)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "eda_german_numeric_by_class.png", dpi=130)
    plt.close(fig)

    lines += [
        "## Hình",
        "",
        "![default by job](../figures/eda_german_default_by_job.png)",
        "",
        "![numeric by class](../figures/eda_german_numeric_by_class.png)",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[eda] đã ghi {out_md}")


if __name__ == "__main__":
    run()

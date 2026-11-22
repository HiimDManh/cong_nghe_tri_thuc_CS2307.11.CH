"""EDA Home Credit -> `reports/eda/home_credit.md` + hình. Đầu vào cho thiết kế BN-Expert & rời rạc hóa."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.common import path, utf8_stdout
from src.data.eda import cramers_v
from src.data.home_credit import load_features

N_BINS = 5  # chỉ để đo liên hệ, không phải ngưỡng rời rạc chính thức


def run() -> None:
    utf8_stdout()
    df = load_features()
    out_md = path("reports", "eda", "home_credit.md")
    fig_dir = path("reports", "figures")
    out_md.parent.mkdir(parents=True, exist_ok=True)

    feats = [c for c in df.columns if c not in ("id", "default")]
    rows = []
    for c in feats:
        s = df[c]
        numeric = pd.api.types.is_numeric_dtype(s) and s.nunique() > 6
        x = pd.qcut(s, N_BINS, duplicates="drop").astype(str) if numeric else s.astype(str)
        x = x.where(s.notna(), "missing")
        rows.append({"feature": c, "missing_%": round(100 * s.isna().mean(), 1), "n_unique": int(s.nunique()),
                     "cramers_v": round(cramers_v(x, df["default"]), 3)})
    assoc = pd.DataFrame(rows).sort_values("cramers_v", ascending=False)

    by_sector = df.groupby("sector").agg(n=("default", "size"), default_rate=("default", "mean"),
                                         median_income=("income", "median"),
                                         median_years_employed=("years_employed", "median"),
                                         median_age=("age_years", "median")).sort_values("default_rate").round(3)
    by_occ = df.groupby("occupation_group").agg(n=("default", "size"), default_rate=("default", "mean"),
                                                median_income=("income", "median")).sort_values("default_rate").round(3)
    num = ["income", "credit_to_income", "annuity_to_income", "credit_term_months", "age_years",
           "years_employed", "ext_score_mean", "bureau_inquiries_year"]
    q = df[num].quantile([0.01, 0.2, 0.4, 0.5, 0.6, 0.8, 0.99]).T.round(3)

    # Quan hệ đơn điệu từng biến số với tỷ lệ vỡ nợ (theo quintile)
    mono = {}
    for c in num:
        b = pd.qcut(df[c], 5, duplicates="drop")
        mono[c] = df.groupby(b, observed=True)["default"].mean().round(3).tolist()
    mono_df = pd.DataFrame({k: pd.Series(v) for k, v in mono.items()}).T
    mono_df.columns = [f"Q{i + 1}" for i in range(mono_df.shape[1])]

    lines = [
        "# EDA – Home Credit `application_train.csv`",
        "",
        "_Sinh tự động bởi `python -m src.data.eda_home_credit`. Không sửa tay._",
        "",
        f"- Số dòng: **{len(df):,}**; tỷ lệ vỡ nợ (`TARGET=1`): **{df['default'].mean():.2%}**",
        "- Đặc trưng đã tạo trong `src/data/home_credit.py` (không dùng giới tính/hôn nhân).",
        "",
        "## Liên hệ với nhãn (Cramér's V; biến số chia 5 quantile, thiếu = 1 nhóm riêng)",
        "",
        assoc.to_markdown(index=False),
        "",
        "## Theo nhóm ngành (`sector`)",
        "",
        by_sector.to_markdown(),
        "",
        "## Theo nhóm nghề (`occupation_group`, ISCO-08)",
        "",
        by_occ.to_markdown(),
        "",
        "## Tỷ lệ vỡ nợ theo quintile của biến số (kiểm tra hướng tác động/đơn điệu)",
        "",
        mono_df.to_markdown(),
        "",
        "## Quantile biến số",
        "",
        q.to_markdown(),
        "",
        "![sector](../figures/eda_hc_sector.png)",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    t = by_sector.sort_values("default_rate")
    axes[0].barh(t.index, t["default_rate"], color="#4C72B0")
    axes[0].axvline(df["default"].mean(), color="gray", ls="--", lw=1)
    axes[0].set_title("Tỷ lệ vỡ nợ theo nhóm ngành")
    axes[1].barh(t.index, t["median_income"], color="#55A868")
    axes[1].set_title("Thu nhập trung vị theo nhóm ngành")
    axes[1].set_yticklabels([])
    fig.tight_layout()
    fig.savefig(fig_dir / "eda_hc_sector.png", dpi=130)
    plt.close(fig)
    print(f"[eda] đã ghi {out_md}")


if __name__ == "__main__":
    run()

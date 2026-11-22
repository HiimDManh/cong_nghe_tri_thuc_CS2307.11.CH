"""Hình cho báo cáo thực nghiệm -> reports/figures/exp_*.png (sinh từ experiments/*/results.csv).

Quy ước màu: mỗi mô hình một màu CỐ ĐỊNH (theo thực thể, không theo thứ hạng) – bảng màu phân loại
đã kiểm định khả năng phân biệt cho người mù màu; tối đa 4 mô hình chính trên một hình đường.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve

from src.common import load_config, path

KEY = ["BN-Expert-Mono", "XGBoost", "TAN", "FICO"]
COLOR = {"BN-Expert-Mono": "#2a78d6", "XGBoost": "#eb6834", "TAN": "#1baf7a", "FICO": "#eda100",
         "LR": "#6250d6", "BN-Expert": "#e87ba4", "LightGBM": "#008300", "Naive Bayes": "#e34948"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
FIG = path("reports", "figures")


def _style(ax: plt.Axes, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.set_xlabel(xlabel, color=MUTED, fontsize=9)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)


def _save(fig: plt.Figure, name: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=150)
    plt.close(fig)


def _line(ax, x, y, n, **kw) -> None:
    ax.plot(x, y, color=COLOR[n], linewidth=2, marker="o", markersize=4, label=n, **kw)


def roc_and_reliability() -> None:
    seed = load_config("eval")["cv"]["seeds"][0]
    z = np.load(path("data", "interim", "oof", f"oof_seed{seed}.npz"))
    y = z["y"]
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    for n in KEY:
        fpr, tpr, _ = roc_curve(y, z[n])
        ax.plot(fpr, tpr, color=COLOR[n], linewidth=2, label=n)
    ax.plot([0, 1], [0, 1], color=MUTED, linewidth=1, linestyle="--")
    _style(ax, f"ROC – dự báo OOF, 5-fold, seed {seed}", "Tỷ lệ dương tính giả", "Tỷ lệ dương tính thật")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    _save(fig, "exp_roc.png")

    from src.evaluation.metrics import reliability

    fig, axes = plt.subplots(2, 2, figsize=(7.5, 6.6), sharex=True, sharey=True)
    for ax, n in zip(axes.ravel(), KEY):
        r = reliability(y, z[n], load_config("eval")["experiments"]["ece_bins"])
        ax.plot([0, 0.5], [0, 0.5], color=MUTED, linewidth=1, linestyle="--")
        ax.plot(r.p_mean, r.y_rate, color=COLOR[n], linewidth=2, marker="o", markersize=4)
        _style(ax, n, "Xác suất dự báo (TB bin)", "Tỷ lệ vỡ nợ thực tế")
        ax.set_xlim(0, 0.45)
        ax.set_ylim(0, 0.45)
    fig.suptitle("Biểu đồ hiệu chỉnh (15 bin cùng số mẫu)", x=0.02, ha="left", fontsize=11)
    _save(fig, "exp_reliability.png")


def missing_fig() -> None:
    df = pd.read_csv(path("experiments", "missing", "results.csv"))
    d = df[df.scenario == "mcar"].groupby(["model", "rate"])[["auc", "logloss"]].mean().reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, met, lab in zip(axes, ["auc", "logloss"], ["ROC-AUC (cao hơn tốt hơn)", "Log-loss (thấp hơn tốt hơn)"]):
        for n in KEY + ["LR"]:
            s = d[d.model == n]
            _line(ax, s.rate * 100, s[met], n)
        _style(ax, lab, "% nhóm biến bị che lúc suy luận (ngẫu nhiên)", "")
    axes[0].legend(frameon=False, fontsize=8)
    _save(fig, "exp_missing.png")


def learning_curve_fig() -> None:
    df = pd.read_csv(path("experiments", "learning_curve", "results.csv"))
    d = df.groupby(["model", "fraction"])[["auc", "ece", "n_train"]].mean().reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, met, lab in zip(axes, ["auc", "ece"], ["ROC-AUC", "ECE (thấp hơn tốt hơn)"]):
        for n in KEY + ["LR"]:
            s = d[d.model == n].sort_values("n_train")
            _line(ax, s.n_train, s[met], n)
        ax.set_xscale("log")
        _style(ax, lab, "Số mẫu huấn luyện (thang log)", "")
    axes[0].legend(frameon=False, fontsize=8)
    _save(fig, "exp_learning_curve.png")


def sector_fig() -> None:
    df = pd.read_csv(path("experiments", "sector_shift", "results.csv"))
    df["d_auc"] = df.auc_loso - df.auc_in
    sectors = df.groupby("sector").n_test.first().sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    offs = np.linspace(-0.27, 0.27, len(KEY))
    for o, n in zip(offs, KEY):
        s = df[df.model == n].set_index("sector").loc[sectors]
        ax.scatter(s.d_auc, np.arange(len(sectors)) + o, color=COLOR[n], s=28, label=n, zorder=3,
                   edgecolor="white", linewidth=1)
    ax.axvline(0, color=MUTED, linewidth=1)
    ax.set_yticks(range(len(sectors)), sectors)
    _style(ax, "Δ AUC khi ngành KHÔNG có trong dữ liệu học (LOSO − in-distribution)", "Δ AUC", "")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    _save(fig, "exp_sector_shift.png")


def consistency_fig() -> None:
    df = pd.read_csv(path("experiments", "consistency", "results.csv"))
    t = df.groupby(["model", "feature"]).violation_rate.mean().unstack()
    t = t.loc[t.mean(1).sort_values().index]
    fig, ax = plt.subplots(figsize=(8, 5.2))
    im = ax.imshow(t.to_numpy() * 100, cmap="Blues", vmin=0, vmax=max(5, float(np.nanmax(t.to_numpy()) * 100)),
                   aspect="auto")
    ax.set_xticks(range(t.shape[1]), t.columns, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(t.shape[0]), t.index, fontsize=8)
    for i in range(t.shape[0]):
        for j in range(t.shape[1]):
            v = t.iloc[i, j] * 100
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=7,
                    color="white" if v > 0.6 * im.get_clim()[1] else INK)
    ax.set_title("% hồ sơ có dự báo đi NGƯỢC hướng tri thức (ICE, bước > 0.1 điểm %)", loc="left", fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.03, label="%")
    _save(fig, "exp_consistency.png")


def stability_fig() -> None:
    df = pd.read_csv(path("experiments", "stability", "results.csv"))
    s = df.groupby("model")[["local_rank_corr", "top3_jaccard"]].mean().sort_values("local_rank_corr")
    fig, ax = plt.subplots(figsize=(6.5, 4))
    y = np.arange(len(s))
    ax.barh(y - 0.2, s.local_rank_corr, height=0.38, color="#2a78d6", label="Spearman cục bộ (|đóng góp|)")
    ax.barh(y + 0.2, s.top3_jaccard, height=0.38, color="#eb6834", label="Jaccard top-3")
    ax.set_yticks(y, s.index, fontsize=8)
    ax.set_xlim(0, 1)
    _style(ax, "Ổn định giải thích giữa 5 fold (1 = giống hệt)", "", "")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    _save(fig, "exp_stability.png")


def lambda_fig() -> None:
    df = pd.read_csv(path("experiments", "lambda_sensitivity", "results.csv"))
    d = df.groupby("lambda").mean(numeric_only=True).reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    _line(axes[0], d["lambda"], d["auc"], "BN-Expert-Mono")
    _style(axes[0], "AUC khi không có bằng chứng biến cố", "λ", "ROC-AUC")
    lab = {"dscore_job_loss": "Mất việc", "dscore_health_shock": "Biến cố sức khỏe",
           "dscore_cashflow_shock": "Hụt dòng tiền"}
    for (c, l), col in zip(lab.items(), ["#2a78d6", "#eb6834", "#1baf7a"]):
        axes[1].plot(d["lambda"], d[c], color=col, linewidth=2, marker="o", markersize=4, label=l)
    _style(axes[1], "Thay đổi điểm TB khi bật biến cố (what-if)", "λ", "Δ điểm")
    axes[1].legend(frameon=False, fontsize=8)
    _save(fig, "exp_lambda.png")


def main() -> None:
    for f in (roc_and_reliability, missing_fig, learning_curve_fig, sector_fig, consistency_fig, stability_fig,
              lambda_fig):
        try:
            f()
        except FileNotFoundError as e:
            print(f"[figures] bỏ qua {f.__name__}: thiếu {e.filename}")
    print(f"[figures] -> {FIG}")

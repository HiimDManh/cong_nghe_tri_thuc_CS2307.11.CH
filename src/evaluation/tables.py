"""Bảng Markdown + số liệu chính từ experiments/*/results.csv -> reports/results/.

- `reports/results/<tên>.md`: bảng cho từng thí nghiệm (chèn vào báo cáo bằng {{table:<tên>}}).
- `reports/results/key_numbers.json`: số liệu chính có tên (chèn bằng {{num:<khóa>}}) – người viết văn bản
  KHÔNG tự gõ số, để báo cáo luôn khớp kết quả chạy.
- `reports/results_summary.md`: toàn bộ bảng + hình (đọc nhanh).
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from src.common import load_config, path

OUT = path("reports", "results")
KEY: dict[str, str] = {}


def _r(p: str) -> pd.DataFrame | None:
    f = path("experiments", p, "results.csv")
    return pd.read_csv(f) if f.exists() else None


def _fmt(m: float, s: float | None = None, d: int = 4) -> str:
    return f"{m:.{d}f}" if s is None or np.isnan(s) else f"{m:.{d}f} ± {s:.{d}f}"


def _write(name: str, title: str, body: str) -> str:
    OUT.mkdir(parents=True, exist_ok=True)
    txt = f"<!-- sinh tự động bởi `python -m src.cli eval tables` – không sửa tay -->\n**{title}**\n\n{body}\n"
    (OUT / f"{name}.md").write_text(txt, encoding="utf-8")
    return txt


def main_cv() -> str | None:
    f = path("experiments", "main_cv", "summary.csv")
    if not f.exists():
        return None
    s = pd.read_csv(f)
    rows = []
    for _, r in s.iterrows():
        rows.append({"Mô hình": r.model, "Họ": r.family, "Đầu vào": r.input,
                     "ROC-AUC": _fmt(r.auc_mean, r.auc_std), "PR-AUC": _fmt(r.pr_auc_mean, r.pr_auc_std),
                     "Gini": _fmt(r.gini_mean, d=3), "KS": _fmt(r.ks_mean, d=3),
                     "Brier": _fmt(r.brier_mean, r.brier_std, 5), "Log-loss": _fmt(r.logloss_mean, r.logloss_std),
                     "ECE": _fmt(r.ece_mean, r.ece_std), "Số lần": int(r.n_runs)})
    t = s.set_index("model")
    for m in t.index:
        KEY[f"auc.{m}"] = f"{t.loc[m, 'auc_mean']:.3f}"
        KEY[f"logloss.{m}"] = f"{t.loc[m, 'logloss_mean']:.4f}"
        KEY[f"ece.{m}"] = f"{t.loc[m, 'ece_mean']:.4f}"
        KEY[f"brier.{m}"] = f"{t.loc[m, 'brier_mean']:.5f}"
    KEY["best_auc_model"] = s.iloc[0].model
    bn = s[s.family == "bn"].iloc[0]
    KEY["best_bn_model"], KEY["best_bn_auc"] = bn.model, f"{bn.auc_mean:.3f}"
    KEY["gap_best_vs_bnmono"] = f"{t.auc_mean.max() - t.loc['BN-Expert-Mono', 'auc_mean']:.3f}"
    KEY["gap_bnmono_vs_fico"] = f"{t.loc['BN-Expert-Mono', 'auc_mean'] - t.loc['FICO', 'auc_mean']:.3f}"
    note = (f"Stratified {load_config('eval')['cv']['n_folds']}-fold × {len(load_config('eval')['cv']['seeds'])} seed "
            f"(mean ± std trên các fold), Home Credit 307.511 hồ sơ, tỷ lệ vỡ nợ 8,07%. ECE: 15 bin cùng số mẫu.")
    return _write("main_cv", "Bảng 1 – Phân biệt & hiệu chỉnh (thí nghiệm 1, 2)",
                  pd.DataFrame(rows).to_markdown(index=False) + f"\n\n_{note}_")


def significance() -> str | None:
    d = _r("significance")
    if d is None:
        return None
    pcols = [c for c in d.columns if c.startswith("delong_p_holm")]
    rows = []
    for _, r in d.iterrows():
        rows.append({"Tham chiếu": r.reference, "So với": r.model, "Δ AUC (ref − mô hình)": f"{r.d_auc:+.4f}",
                     "DeLong p (Holm, max 3 seed)": f"{r[pcols].max():.2g}",
                     "t-test hiệu chỉnh p (AUC)": f"{r.nb_ttest_p_auc:.2g}",
                     "Thắng AUC / số cặp fold": f"{int(r.wins_auc)}/{int(r.n_pairs)}",
                     "Δ Log-loss [CI 95%]": f"{r.d_logloss:+.5f} [{r.d_logloss_lo:+.5f}, {r.d_logloss_hi:+.5f}]",
                     "Δ ECE [CI 95%]": f"{r.d_ece:+.4f} [{r.d_ece_lo:+.4f}, {r.d_ece_hi:+.4f}]"})
    ref = d[d.reference == "BN-Expert-Mono"].set_index("model")
    for m in ref.index:
        KEY[f"delong_p.{m}"] = f"{ref.loc[m, pcols].max():.2g}"
    return _write("significance", "Bảng 2 – Kiểm định ý nghĩa thống kê (thí nghiệm 3)",
                  pd.DataFrame(rows).to_markdown(index=False) +
                  "\n\n_DeLong trên dự báo OOF gộp của từng seed, hiệu chỉnh Holm trong mỗi tham chiếu; t-test "
                  "Nadeau–Bengio trên 15 cặp fold; CI 95% của Δ Log-loss/ECE: paired bootstrap 1.000 lần (seed 42). "
                  "Δ < 0 ở Log-loss/ECE nghĩa là tham chiếu tốt hơn._")


def missing() -> str | None:
    d = _r("missing")
    if d is None:
        return None
    m = d[d.scenario == "mcar"].groupby(["model", "rate"]).auc.mean().unstack()
    m["Δ (50% − 0%)"] = m[0.5] - m[0.0]
    m = m.sort_values("Δ (50% − 0%)", ascending=False)
    m.columns = [c if isinstance(c, str) else f"{int(c * 100)}%" for c in m.columns]
    t1 = m.round(4).reset_index().rename(columns={"model": "Mô hình"}).to_markdown(index=False)
    sc = d[d.scenario != "mcar"].groupby(["model", "scenario"])[["auc", "logloss", "ece"]].mean().unstack()
    full = d[(d.scenario == "mcar") & (d.rate == 0)].groupby("model")[["auc", "logloss"]].mean()
    rows = []
    for mod in sc.index:
        r = {"Mô hình": mod, "Đầy đủ AUC": f"{full.loc[mod, 'auc']:.4f}"}
        for s in ("no_ext_score", "no_credit_history", "thin_file"):
            r[f"{s} AUC"] = f"{sc.loc[mod, ('auc', s)]:.4f}"
            r[f"{s} LL"] = f"{sc.loc[mod, ('logloss', s)]:.4f}"
        rows.append(r)
    for mod in m.index:
        KEY[f"missing_auc30.{mod}"] = f"{m.loc[mod, '30%']:.3f}"
        KEY[f"missing_auc20.{mod}"] = f"{m.loc[mod, '20%']:.3f}"
        KEY[f"missing_auc10.{mod}"] = f"{m.loc[mod, '10%']:.3f}"
        for sc_ in ("no_ext_score", "thin_file"):
            KEY[f"missing_{sc_}.{mod}"] = f"{sc.loc[mod, ('auc', sc_)]:.3f}"
        KEY[f"missing_drop50.{mod}"] = f"{m.loc[mod, 'Δ (50% − 0%)']:.3f}"
        KEY[f"missing_auc50.{mod}"] = f"{m.loc[mod, '50%']:.3f}"
    t2 = pd.DataFrame(rows).sort_values("thin_file AUC", ascending=False).to_markdown(index=False)
    return _write("missing", "Bảng 3 – Thiếu thông tin lúc suy luận (thí nghiệm 4)",
                  "(a) Che ngẫu nhiên (MCAR) một tỷ lệ nhóm biến đầu vào ở tập test – ROC-AUC trung bình 5 fold\n\n"
                  + t1 + "\n\n(b) Kịch bản thiếu có cấu trúc: `no_ext_score` = không có điểm tín dụng ngoài; "
                  "`no_credit_history` = thêm không có số lần tra cứu; `thin_file` = khách hàng mới: chỉ biết nhân "
                  "khẩu, ngành/nghề, thu nhập, thâm niên (không có lịch sử tín dụng, khoản vay, tài sản). LL = Log-loss.\n\n"
                  + t2 + "\n\n_Mô hình được học trên dữ liệu ĐẦY ĐỦ; chỉ che lúc suy luận. BN/FICO bỏ qua biến thiếu "
                  "(BN lấy biên chính xác, FICO dùng điểm 'missing'); ML liên tục: XGBoost/LightGBM dùng nhánh mặc "
                  "định cho NaN, LR/RF/MLP điền trung vị train; ML rời rạc: one-hot toàn 0._")


def learning_curve() -> str | None:
    d = _r("learning_curve")
    if d is None:
        return None
    t = d.groupby(["model", "fraction"]).agg(auc=("auc", "mean"), ece=("ece", "mean"), n=("n_train", "mean"))
    auc = t.auc.unstack()
    ece = t.ece.unstack()
    n = t.n.unstack().iloc[0]
    auc.columns = [f"{c:.0%} (n≈{int(n[c]):,})" for c in auc.columns]
    ece.columns = auc.columns
    for mod in auc.index:
        KEY[f"lc_auc_1pct.{mod}"] = f"{auc.loc[mod].iloc[0]:.3f}"
        KEY[f"lc_auc_10pct.{mod}"] = f"{auc.loc[mod].iloc[2]:.3f}"
        KEY[f"lc_ece_1pct.{mod}"] = f"{ece.loc[mod].iloc[0]:.4f}"
    body = ("(a) Home Credit – ROC-AUC theo cỡ tập học (5 fold, seed 42; test luôn là fold đầy đủ)\n\n"
            + auc.sort_values(auc.columns[0], ascending=False).round(4).reset_index().to_markdown(index=False)
            + "\n\n(b) Home Credit – ECE theo cỡ tập học\n\n"
            + ece.sort_values(ece.columns[0]).round(4).reset_index().to_markdown(index=False))
    g = _r("german_small_data")
    if g is not None:
        gt = g.groupby(["model", "fraction"])[["auc", "logloss"]].agg(["mean", "std"])
        rows = []
        for mod in g.model.unique():
            r = {"Mô hình": mod}
            for fr in sorted(g.fraction.unique()):
                nn = int(g[g.fraction == fr].n_train.mean())
                r[f"AUC n={nn}"] = _fmt(gt.loc[(mod, fr), ("auc", "mean")], gt.loc[(mod, fr), ("auc", "std")], 3)
                r[f"LL n={nn}"] = f"{gt.loc[(mod, fr), ('logloss', 'mean')]:.3f}"
            rows.append(r)
        body += ("\n\n(c) German Credit (1.000 hồ sơ, 10 lần × 5-fold) – BN chuyên gia nhỏ (`configs/german_bn.yaml`)\n\n"
                 + pd.DataFrame(rows).to_markdown(index=False))
    return _write("learning_curve", "Bảng 4 – Dữ liệu ít (thí nghiệm 5)", body)


def sector_shift() -> str | None:
    d = _r("sector_shift")
    if d is None:
        return None
    d = d.assign(d_auc=d.auc_loso - d.auc_in, d_ll=d.logloss_loso - d.logloss_in,
                 abs_citl=d.citl_loso.abs(), abs_citl_in=d.citl_in.abs())
    g = d.groupby("model").agg(auc_in=("auc_in", "mean"), auc_loso=("auc_loso", "mean"), d_auc=("d_auc", "mean"),
                               worst_d_auc=("d_auc", "min"), d_ll=("d_ll", "mean"), ece_loso=("ece_loso", "mean"),
                               citl_loso=("abs_citl", "mean"), citl_in=("abs_citl_in", "mean"))
    g["d_auc_excl"] = d[d.sector != "not_working"].groupby("model").d_auc.mean()
    g["citl_excl"] = d[d.sector != "not_working"].groupby("model").abs_citl.mean()
    g = g.sort_values("d_auc", ascending=False)
    for mod in g.index:
        KEY[f"sector_dauc.{mod}"] = f"{g.loc[mod, 'd_auc']:+.4f}"
        KEY[f"sector_dauc_excl.{mod}"] = f"{g.loc[mod, 'd_auc_excl']:+.4f}"
        KEY[f"sector_citl.{mod}"] = f"{g.loc[mod, 'citl_loso']:.4f}"
        KEY[f"sector_citl_excl.{mod}"] = f"{g.loc[mod, 'citl_excl']:.4f}"
        KEY[f"sector_dauc_notworking.{mod}"] = f"{d[(d.model == mod) & (d.sector == 'not_working')].d_auc.iloc[0]:+.4f}"
    g.columns = ["AUC in-dist", "AUC LOSO", "Δ AUC TB", "Δ AUC tệ nhất", "Δ Log-loss TB", "ECE LOSO",
                 "|p̄ − y̅| LOSO", "|p̄ − y̅| in-dist", "Δ AUC TB (trừ not_working)", "|p̄ − y̅| LOSO (trừ not_working)"]
    per = d.pivot_table(index="sector", columns="model", values="d_auc").round(4)
    return _write("sector_shift", "Bảng 5 – Dịch chuyển theo ngành: leave-one-sector-out (thí nghiệm 6)",
                  g.round(4).reset_index().rename(columns={"model": "Mô hình"}).to_markdown(index=False)
                  + "\n\nΔ AUC theo từng ngành (LOSO − in-distribution):\n\n" + per.reset_index().to_markdown(index=False)
                  + "\n\n_LOSO: học trên 9 nhóm ngành, kiểm tra trên nhóm còn lại; in-dist: dự báo OOF (5-fold seed 42) "
                    "của cùng mô hình trên đúng các hồ sơ đó. |p̄ − y̅| = sai lệch hiệu chỉnh tổng thể._")


def exp_dir_cols(d: pd.DataFrame) -> list[str]:
    return sorted(d.feature.unique())


def consistency() -> str | None:
    d = _r("consistency")
    if d is None:
        return None
    v = (d.groupby(["model", "feature"]).violation_rate.mean().unstack() * 100)
    v["TB"] = v.mean(1)
    v = v.sort_values("TB")
    ok = d.groupby(["model", "feature"]).pdp_monotone_ok.mean().unstack()
    nok = (ok == 1).sum(1).reindex(v.index)
    flat = d.groupby(["model", "feature"]).flat_rate.mean().unstack()
    v["PDP đúng hướng (/6)"] = nok.astype(int)
    v["Biến không tác động (phẳng)"] = [", ".join(flat.columns[flat.loc[m] >= 0.95]) or "–" for m in v.index]
    for mod in v.index:
        KEY[f"violation.{mod}"] = f"{v.loc[mod, 'TB']:.1f}%"
        for feat in exp_dir_cols(d):
            KEY[f"violation_feat.{mod}.{feat}"] = f"{v.loc[mod, feat]:.1f}%"
    exp = load_config("eval")["expected_direction"]
    note = ", ".join(f"{k}: {'↑ rủi ro' if x == 'increasing' else '↓ rủi ro'}" for k, x in exp.items())
    return _write("consistency", "Bảng 6 – Nhất quán với tri thức chuyên gia (thí nghiệm 7)",
                  "% hồ sơ có ít nhất một bước ICE đi ngược hướng tri thức (bước > 0,1 điểm %), 5.000 hồ sơ test × 5 fold\n\n"
                  + v.round(2).reset_index().rename(columns={"model": "Mô hình"}).to_markdown(index=False)
                  + f"\n\n_Hướng kỳ vọng (tăng biến): {note}. BN-Expert-Mono / XGBoost-Mono bị ràng buộc đơn điệu ở "
                    "DSTI & ext_score theo thiết kế (0% ở hai cột đó là do xây dựng, không phải phát hiện). 0% ở biến phẳng (≥ 95% hồ sơ không đổi dự báo khi đổi biến) "
                    "là KHÔNG có tác động – không phải tuân thủ tri thức; với BN đó là do d-separation khi đã biết các nút cha của Vỡ nợ._")


def stability() -> str | None:
    d = _r("stability")
    if d is None:
        return None
    s = d.groupby("model")[["local_rank_corr", "top3_jaccard", "top3_sign_agree", "global_rank_corr", "attr_mad"]].mean()
    s = s.sort_values("local_rank_corr", ascending=False)
    for mod in s.index:
        KEY[f"stab_local.{mod}"] = f"{s.loc[mod, 'local_rank_corr']:.3f}"
        KEY[f"stab_top3.{mod}"] = f"{s.loc[mod, 'top3_jaccard']:.3f}"
    s.columns = ["Spearman cục bộ", "Jaccard top-3", "Đồng dấu top-3", "Spearman toàn cục", "MAD đóng góp (log-odds)"]
    body = s.round(4).reset_index().rename(columns={"model": "Mô hình"}).to_markdown(index=False)
    f = path("experiments", "stability", "global_importance.csv")
    if f.exists():
        gi = pd.read_csv(f).drop(columns="fold").groupby("model").mean()
        top = {m: ", ".join(gi.loc[m].sort_values(ascending=False).index[:5]) for m in gi.index}
        body += "\n\nTop-5 nhóm biến quan trọng nhất (TB |đóng góp| trên 2.000 hồ sơ, 5 fold):\n\n" + \
            pd.DataFrame({"Mô hình": list(top), "Top-5": list(top.values())}).to_markdown(index=False)
        if {"BN-Expert-Mono", "XGBoost"} <= set(gi.index):
            from scipy.stats import spearmanr

            rho = spearmanr(gi.loc["BN-Expert-Mono"], gi.loc["XGBoost"]).statistic
            KEY["importance_rho_bnmono_xgb"] = f"{rho:.2f}"
            body += f"\n\nTương quan hạng độ quan trọng toàn cục BN-Expert-Mono vs XGBoost (SHAP): ρ = {rho:.2f}."
    return _write("stability", "Bảng 7 – Ổn định giải thích giữa các fold (thí nghiệm 8)", body +
                  "\n\n_Cùng 2.000 hồ sơ cố định, giải thích bởi 5 mô hình học trên 5 fold khác nhau; trung bình trên "
                  "10 cặp fold. BN/FICO: đóng góp so với mức phổ biến của quần thể (suy luận chính xác); cây: TreeSHAP; LR: SHAP tuyến tính._")


def cost() -> str | None:
    d = _r("cost")
    if d is None:
        return None
    d = d[["model", "family", "fit_s", "pred_s_per_10k", "n_params", "size_kb"]].copy()
    d.columns = ["Mô hình", "Họ", "Thời gian học (s)", "Suy luận / 10k hồ sơ (s)", "Số tham số", "Kích thước (KB)"]
    return _write("cost", "Bảng 8 – Chi phí tính toán (thí nghiệm 9)",
                  d.round(3).to_markdown(index=False) +
                  "\n\n_Trung bình trên các fold, ~246k hồ sơ học, CPU 16 luồng. Kích thước = pickle của mô hình đã học "
                  "(gồm cả tiền xử lý). Số tham số: BN Σ(r−1)·q; cây: số nút; LR: hệ số._")


def lambda_() -> str | None:
    d = _r("lambda_sensitivity")
    if d is None:
        return None
    g = d.groupby("lambda")[["auc", "logloss", "ece", "dscore_job_loss", "dscore_health_shock",
                             "dscore_cashflow_shock", "dscore_econ_cycle", "dscore_inflation", "n_p0_clipped"]].mean()
    g.columns = ["AUC", "Log-loss", "ECE", "Δ điểm: mất việc", "Δ điểm: sức khỏe", "Δ điểm: hụt dòng tiền",
                 "Δ điểm: suy thoái", "Δ điểm: lạm phát cao", "Ô p0 bị cắt"]
    KEY["lambda_auc_0"] = f"{g.loc[0.0, 'AUC']:.4f}" if 0.0 in g.index else ""
    KEY["lambda_auc_03"] = f"{g.loc[0.3, 'AUC']:.4f}" if 0.3 in g.index else ""
    KEY["lambda_auc_05"] = f"{g.loc[0.5, 'AUC']:.4f}" if 0.5 in g.index else ""
    if 0.3 in g.index:
        for c, k in (("Δ điểm: mất việc", "job"), ("Δ điểm: sức khỏe", "health"), ("Δ điểm: hụt dòng tiền", "cash")):
            KEY[f"whatif_{k}"] = f"{g.loc[0.3, c]:.0f}"
    return _write("lambda", "Bảng 9 – Độ nhạy tham số giả định λ của lớp tri thức (BN-Expert-Mono)",
                  g.round(4).reset_index().to_markdown(index=False) +
                  "\n\n_AUC/Log-loss/ECE: dự báo khi KHÔNG có bằng chứng biến cố (đúng như dữ liệu). Δ điểm: thay đổi "
                  "điểm 300–850 trung bình của 2.000 hồ sơ đang đi làm khi bật biến cố (what-if), 5 fold._")


def xgb_disc_diag() -> str | None:
    """Chẩn đoán XGBoost-disc @1% (`diagnose_xgb_disc.py`): chỉ giải thích, không thay bảng learning curve."""
    d = _r("xgb_disc_diagnosis")
    if d is None:
        return None
    g = (d.groupby(["fraction", "input", "variant"], sort=False)
           .agg(auc=("auc", "mean"), best_iter=("best_iteration", "median"), split_nodes=("n_split_nodes", "median"),
                feasible_cols=("feasible_onehot_cols", "median"), n_features=("n_features", "median"))
           .reset_index())
    tags = {"as_is (tuned, ES)": "asis", "H1: tuned, no ES": "noes", "H2: tuned, mcw=1, ES": "mcw1",
            "untuned (mcw=10), ES": "untuned"}
    for _, r in g.iterrows():
        k = f"{r['input']}_{r['fraction']:.0%}_{tags[r['variant']]}"
        KEY[f"xgbd_auc.{k}"] = f"{r['auc']:.3f}"
        KEY[f"xgbd_iter.{k}"] = f"{r['best_iter']:.0f}"
        if r["input"] == "disc":
            KEY[f"xgbd_feasible.{k}"] = f"{r['feasible_cols']:.0f}"
            KEY[f"xgbd_nfeat.{k}"] = f"{r['n_features']:.0f}"
    one = d[(d.fraction == 0.01) & (d.input == "disc")].iloc[0]
    KEY["xgbd_mcw_tuned"] = f"{d.loc[d.variant.str.startswith('as_is'), 'min_child_weight'].iloc[0]:.1f}"
    KEY["xgbd_n_train_1pct"] = f"{one['n_train_inner']:,}"
    KEY["xgbd_val_pos_1pct"] = f"{int(d[d.fraction == 0.01]['n_val_pos'].median())}"
    g["auc"] = g["auc"].round(4)
    return _write("xgb_disc_diag", "Bảng 5b – Chẩn đoán XGBoost-disc khi ít dữ liệu (5 fold, seed 42)",
                  g.to_markdown(index=False) +
                  "\n\n_ES = early stopping (100 vòng, val nội bộ 10% train); no ES = 500 cây cố định; mcw = "
                  "min_child_weight (ngưỡng TỔNG hessian mỗi lá). best_iter, split_nodes: trung vị qua 5 fold; "
                  "feasible_cols: số cột one-hot mà cả hai nhánh đạt tổng hessian ≥ mcw tại tỷ lệ nền. Chỉ để chẩn "
                  "đoán – bảng learning curve chính thức giữ nguyên._")


def llm() -> str | None:
    d = _r("llm_faithfulness")
    if d is None:
        return None
    g = d.groupby("provider")[["number_precision", "fact_coverage", "direction_ok", "faithful", "latency_s"]].mean()
    g["n"] = d.groupby("provider").size()
    g["n_so_ngoai_du_kien"] = d.assign(b=d["number_precision"] < 1).groupby("provider")["b"].sum()
    g["n_sai_huong"] = d.assign(b=~d["direction_ok"].astype(bool)).groupby("provider")["b"].sum()
    for p in g.index:
        KEY[f"llm_faithful.{p}"] = f"{g.loc[p, 'faithful']:.0%}"
        KEY[f"llm_n_unfaithful.{p}"] = f"{int(g.loc[p, 'n'] - d[d.provider == p]['faithful'].astype(bool).sum())}"
        KEY[f"llm_n_bad_numbers.{p}"] = f"{int(g.loc[p, 'n_so_ngoai_du_kien'])}"
        KEY[f"llm_n_wrong_dir.{p}"] = f"{int(g.loc[p, 'n_sai_huong'])}"
    return _write("llm", "Bảng 10 – Độ trung thành của lời khuyên LLM (kiểm tra tự động)",
                  g.round(3).reset_index().to_markdown(index=False) +
                  "\n\n_number_precision: tỷ lệ con số trong lời khuyên có trong dữ kiện BN cung cấp; fact_coverage: tỷ lệ "
                  "dữ kiện bắt buộc được nhắc; direction_ok: không nói sai hướng tác động; faithful: đạt cả ba. "
                  "n_so_ngoai_du_kien / n_sai_huong: số lời khuyên có ≥ 1 con số không có trong dữ kiện / nói sai hướng. "
                  "template_corrupted: đối chứng âm (cố ý sửa sai). latency_s (giây) gồm cả thời gian chờ khi bị giới "
                  "hạn tốc độ (HTTP 429) của gói miễn phí → không dùng để so tốc độ model._")


def main() -> None:
    parts = [f() for f in (main_cv, significance, missing, learning_curve, xgb_disc_diag, sector_shift, consistency,
                           stability, cost, lambda_, llm)]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "key_numbers.json").write_text(json.dumps(KEY, ensure_ascii=False, indent=1), encoding="utf-8")
    figs = sorted(p.name for p in path("reports", "figures").glob("exp_*.png"))
    summary = ["# Tổng hợp kết quả thực nghiệm", "",
               "_Sinh tự động bởi `python -m src.cli eval tables` từ `experiments/*/results.csv`. Không sửa tay._", ""]
    summary += [p for p in parts if p]
    summary += ["## Hình", ""] + [f"![{f}](figures/{f})" for f in figs]
    path("reports", "results_summary.md").write_text("\n\n".join(summary), encoding="utf-8")
    print(f"[tables] {sum(p is not None for p in parts)} bảng, {len(KEY)} số liệu chính -> reports/results/")

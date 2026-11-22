"""Học mô hình cuối cùng trên TOÀN BỘ dữ liệu Home Credit để dùng cho demo (không dùng cho đánh giá –
đánh giá dùng CV ở src/evaluation/). Lưu JSON nhỏ trong models/ (được commit để deploy không cần train lại).

    python -m src.cli train
"""
from __future__ import annotations

import json
import time

import pandas as pd

from src.bn import expert_cpt
from src.bn.model import fit_expert_bn
from src.common import load_config, path, set_seed, utf8_stdout
from src.data.discretize import Discretizer
from src.data.home_credit import load_features


def main() -> None:
    utf8_stdout()
    set_seed(load_config("data")["seed"])
    t0 = time.time()
    feat = load_features()
    disc = Discretizer().fit(feat)
    X = disc.transform(feat)
    out = path("models")
    out.mkdir(exist_ok=True)
    disc.save(out / "discretizer.json")

    for mono, name in [(False, "bn_expert"), (True, "bn_expert_mono")]:
        bn = fit_expert_bn(X, feat, monotone=mono)
        bn.meta.update(n_train=len(X), default_rate=float(feat["default"].mean()))
        bn.to_json(out / f"{name}.json")
        print(f"[train] {bn.meta['name']}: π(shock)={bn.meta['pi_shock']:.4f}, ô p0 bị cắt={bn.meta['n_p0_clipped']} -> models/{name}.json")

    # XGBoost trên đúng trạng thái BN (one-hot) để demo so sánh hộp đen – lưu JSON gốc của XGBoost (không pickle)
    from src.baselines.ml import MLModel

    xgb = MLModel("XGBoost-disc", "xgboost", "disc").fit(feat, X.drop(columns="default"), feat["default"].to_numpy())
    xgb.est.get_booster().save_model(out / "xgb_disc.json")
    (out / "xgb_disc_features.json").write_text(json.dumps(xgb.feature_names(), ensure_ascii=False), encoding="utf-8")
    print(f"[train] XGBoost-disc: {xgb.best_iter + 1} cây -> models/xgb_disc.json")

    prov = expert_cpt.provenance(feat)
    rep = path("reports", "bn")
    rep.mkdir(parents=True, exist_ok=True)
    lines = ["# Tham số lớp tri thức của BN-Expert (sinh tự động bởi `python -m src.cli train`)", "",
             "| Tham số | Giá trị | Nguồn |", "|---|---|---|"]
    sources = {
        "P(inflation)": "World Bank FP.CPI.TOTL.ZG, VN 2000–2024, ngưỡng 4%/8%",
        "P(econ_cycle)": "World Bank NY.GDP.MKTP.KD.ZG, VN 2000–2024, ngưỡng 5% (giả định)",
        "unemployment base": "World Bank SL.UEM.TOTL.ZS, TB các năm 'normal'",
        "unemployment multiplier": "World Bank, TB downturn / normal",
        "sector churn": "Proxy từ Home Credit: tỷ lệ thâm niên < 1 năm theo ngành",
        "health shock": "WHO GHO SDG 3.8.2 (chi y tế > 10%), VN 2018, theo tuổi",
        "income buffer": "GSO KSMS 2024 Biểu 4 & 11: (chi tiêu/thu nhập) nhóm Qk / Q1",
    }
    for k, v in prov.items():
        src = next((s for key, s in sources.items() if k.startswith(key)), "")
        lines.append(f"| {k} | {json.dumps(v, ensure_ascii=False)} | {src} |")
    cfg = load_config("bn_expert_cpt")
    lines += ["", "Tham số GIẢ ĐỊNH (configs/bn_expert_cpt.yaml):", "",
              f"- tenure multiplier: {cfg['job_loss']['tenure_multiplier']}",
              f"- horizon multiplier: {cfg['job_loss']['horizon_multiplier']}",
              f"- living_cost: base {cfg['living_cost']['base_probs']}, shift {cfg['living_cost']['shift_per_unit']}",
              f"- cashflow_shock: leak {cfg['cashflow_shock']['leak']}, inhibitors {cfg['cashflow_shock']['inhibitors']}, "
              f"asset buffer {cfg['cashflow_shock']['asset_buffer']}",
              f"- default_link λ = {cfg['default_link']['lambda']}", ""]
    (rep / "expert_params.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[train] xong trong {time.time() - t0:.1f}s; tham số tri thức -> reports/bn/expert_params.md")


if __name__ == "__main__":
    main()

"""Chẩn đoán XGBoost-disc ở 1% dữ liệu train (AUC≈0.5 trong thí nghiệm learning curve).

Hai giả thuyết:
  H1 – early stopping dừng ở vòng 0 (tập val nội bộ quá nhỏ).
  H2 – `min_child_weight` đã tinh chỉnh (≈37, tính theo tổng hessian) quá lớn so với dữ liệu nhỏ:
       với p≈0.08 mỗi mẫu đóng góp hessian p(1−p)≈0.074 → mỗi lá cần ≈500 dòng; biến one-hot
       hiếm không tách được → cây chỉ có lá gốc → dự đoán hằng số.
Chỉ chẩn đoán để giải thích trong báo cáo; KHÔNG thay kết quả chính thức của learning curve.
Cách chạy: `python -m src.evaluation.diagnose_xgb_disc` → experiments/xgb_disc_diagnosis/results.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from src.baselines.ml import MLModel, preprocessor
from src.common import load_config, path, utf8_stdout
from src.data.home_credit import load_features
from src.evaluation import metrics as M
from src.evaluation.cv import fold_data, load_splits

FRACTIONS = [0.01, 0.05]
FIXED_ROUNDS = 500  # số cây cố định cho biến thể không early stopping


def _variants(tuned: dict, untuned: dict) -> dict[str, tuple[dict, bool]]:
    """Tên biến thể → (tham số, có early stopping?)."""
    return {
        "as_is (tuned, ES)": (tuned, True),
        "H1: tuned, no ES": (tuned | {"n_estimators": FIXED_ROUNDS}, False),
        "H2: tuned, mcw=1, ES": (tuned | {"min_child_weight": 1.0}, True),
        "untuned (mcw=10), ES": (untuned, True),
    }


def _n_splits(est: XGBClassifier) -> int:
    df = est.get_booster().trees_to_dataframe()
    return int((df["Feature"] != "Leaf").sum())


def _feasible_cols(A: np.ndarray, y: np.ndarray, mcw: float) -> int:
    """Số cột one-hot mà cả hai nhánh đạt tổng hessian ≥ mcw tại dự đoán khởi đầu (tỷ lệ nền)."""
    p = y.mean()
    h = p * (1 - p)
    n1 = A.sum(axis=0)
    return int(((np.minimum(n1, len(A) - n1) * h) >= mcw).sum())


def run() -> pd.DataFrame:
    utf8_stdout()
    cfg = load_config("eval")
    seed = cfg["cv"]["seeds"][0]
    feat = load_features()
    sp = load_splits(feat)
    y_all = feat["default"].to_numpy()
    ref = MLModel("XGBoost-disc", "xgboost", "disc", seed=seed)
    tuned = ref._params("xgboost")
    untuned = {k: v for k, v in cfg["ml"]["xgboost"].items() if k != "tuned_params_file"}
    rows = []
    for k in range(cfg["cv"]["n_folds"]):
        test = sp[seed] == k
        tr_idx = np.flatnonzero(~test)
        for frac in FRACTIONS:
            # cùng cách lấy mẫu con phân tầng như learning_curve() trong run.py
            rng = np.random.default_rng(seed * 100 + k)
            sub = np.concatenate([rng.choice(tr_idx[y_all[tr_idx] == c], int(round(frac * (y_all[tr_idx] == c).sum())),
                                             replace=False) for c in (0, 1)])
            tm = np.zeros(len(feat), bool)
            tm[sub] = True
            fd = fold_data(feat, tm, test)
            for kind in ("disc", "cont"):
                m = MLModel(f"XGBoost-{kind}", "xgboost", kind, seed=seed)
                X, Xte = m._X(fd.train_f, fd.train_d), m._X(fd.test_f, fd.test_d)
                Xtr, Xva, ytr, yva = train_test_split(X, fd.y_train, test_size=cfg["ml"]["inner_val_frac"],
                                                      stratify=fd.y_train, random_state=seed)
                pre = preprocessor(kind, False)
                A, V, T = pre.fit_transform(Xtr), pre.transform(Xva), pre.transform(Xte)
                for vname, (params, use_es) in _variants(tuned, untuned).items():
                    p = dict(params)
                    es = p.pop("early_stopping_rounds")
                    est = XGBClassifier(**p, tree_method="hist", eval_metric="logloss",
                                        early_stopping_rounds=es if use_es else None,
                                        random_state=seed, n_jobs=-1, verbosity=0)
                    est.fit(A, ytr, eval_set=[(V, yva)], verbose=False)
                    prob = est.predict_proba(T)[:, 1]
                    rows.append({
                        "fold": k, "fraction": frac, "input": kind, "variant": vname,
                        "n_train_inner": len(ytr), "n_val_inner": len(yva), "n_val_pos": int(yva.sum()),
                        "n_features": A.shape[1], "min_child_weight": p["min_child_weight"],
                        "feasible_onehot_cols": _feasible_cols(A, ytr, p["min_child_weight"]) if kind == "disc" else np.nan,
                        "best_iteration": int(est.best_iteration) if use_es else FIXED_ROUNDS - 1,
                        "n_split_nodes": _n_splits(est), "pred_std": float(prob.std()),
                        "auc": M.all_metrics(fd.y_test, prob, cfg["experiments"]["ece_bins"])["auc"],
                    })
            print(f"[diag] fold {k} frac {frac} xong")
    df = pd.DataFrame(rows)
    out = path("experiments", "xgb_disc_diagnosis")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "results.csv", index=False)
    summ = (df.groupby(["fraction", "input", "variant"], sort=False)
              .agg(auc=("auc", "mean"), auc_sd=("auc", "std"), best_iter=("best_iteration", "median"),
                   split_nodes=("n_split_nodes", "median"), feasible_cols=("feasible_onehot_cols", "median"),
                   n_features=("n_features", "median"), n_val_pos=("n_val_pos", "median")).round(4).reset_index())
    (out / "summary.md").write_text(summ.to_markdown(index=False) + "\n", encoding="utf-8")
    print(summ.to_string(index=False))
    return df


if __name__ == "__main__":
    run()

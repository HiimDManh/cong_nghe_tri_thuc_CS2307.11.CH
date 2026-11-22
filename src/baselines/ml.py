"""Baseline học máy "hộp đen": LR, XGBoost, LightGBM, RF, MLP.

Công bằng thông tin: ML dùng CÙNG 13 nhóm biến đầu vào như BN (không thêm cột Home Credit khác), ở
hai dạng: (a) liên tục (`cont`) – giá trị gốc; (b) rời rạc (`disc`) – đúng trạng thái BN, one-hot.
Không resample mất cân bằng; mọi mô hình xuất xác suất và được đánh giá bằng chỉ số xác suất.
"""
from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from src.common import load_config, path

# Nhóm biến đầu vào (tên nút BN) -> cột ở dạng liên tục / rời rạc. Dùng chung cho che giấu thông tin
# (thí nghiệm 4) và gộp giải thích SHAP về đúng nhóm biến (thí nghiệm 7, 8).
GROUPS: dict[str, dict[str, list[str]]] = {
    "sector": {"cont": ["sector"], "disc": ["sector"]},
    "occupation_group": {"cont": ["occupation_group"], "disc": ["occupation_group"]},
    "education": {"cont": ["education"], "disc": ["education"]},
    "age_years": {"cont": ["age_years"], "disc": ["age_years"]},
    "years_employed": {"cont": ["years_employed", "not_working"], "disc": ["years_employed"]},
    "income": {"cont": ["income"], "disc": ["income"]},
    "n_children": {"cont": ["n_children"], "disc": ["n_children"]},
    "assets": {"cont": ["own_realty", "own_car"], "disc": ["assets"]},
    "annuity_to_income": {"cont": ["annuity_to_income"], "disc": ["annuity_to_income"]},
    "credit_to_income": {"cont": ["credit_to_income"], "disc": ["credit_to_income"]},
    "ext_score_mean": {"cont": ["ext_score_mean"], "disc": ["ext_score_mean"]},
    "bureau_inquiries_year": {"cont": ["bureau_inquiries_year"], "disc": ["bureau_inquiries_year"]},
    "region_rating": {"cont": ["region_rating"], "disc": ["region_rating"]},
}
CAT = ["sector", "occupation_group", "education"]
NUM = [c for g in GROUPS.values() for c in g["cont"] if c not in CAT]
DISC = [c for g in GROUPS.values() for c in g["disc"]]


def cont_frame(Xf: pd.DataFrame) -> pd.DataFrame:
    """Bảng đặc trưng liên tục cho ML. years_employed của người không đi làm = 0 + cờ not_working
    (để phân biệt với giá trị THIẾU thật – NaN – trong thí nghiệm che giấu thông tin)."""
    X = Xf.copy()
    if "not_working" not in X:
        X["not_working"] = X["years_employed"].isna().astype(float)
        X["years_employed"] = X["years_employed"].fillna(0.0)
    return X[NUM + CAT]


def disc_frame(Xd: pd.DataFrame) -> pd.DataFrame:
    return Xd[DISC].astype(object)


def group_of(feature_name: str) -> str:
    """'cat__sector_trade' / 'num__income' / 'sector_trade' -> nhóm biến gốc."""
    n = feature_name.split("__", 1)[-1]
    for g, cols in GROUPS.items():
        for c in cols["cont"] + cols["disc"]:
            if n == c or n.startswith(c + "_"):
                return g
    raise KeyError(feature_name)


def _cat_pipe() -> Pipeline:
    return Pipeline([("imp", SimpleImputer(strategy="constant", fill_value="missing")),
                     ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])


def preprocessor(kind: str, scale: bool) -> ColumnTransformer:
    """kind='cont': số (impute median, log thu nhập, chuẩn hóa nếu scale) + one-hot ngành/nghề/học vấn.
    kind='disc': one-hot mọi trạng thái BN."""
    if kind == "disc":
        return ColumnTransformer([("cat", _cat_pipe(), DISC)])
    num_steps = [("imp", SimpleImputer(strategy="median"))] if scale else []
    if scale:
        num_steps += [("log", FunctionTransformer(_log_income, feature_names_out="one-to-one")),
                      ("sc", StandardScaler())]
    num = Pipeline(num_steps) if num_steps else "passthrough"
    return ColumnTransformer([("num", num, NUM), ("cat", _cat_pipe(), CAT)])


def _log_income(a: np.ndarray) -> np.ndarray:
    a = np.array(a, dtype=float, copy=True)
    i = NUM.index("income")
    a[:, i] = np.log(np.maximum(a[:, i], 1.0))
    return a


class MLModel:
    """Bọc mô hình sklearn/XGBoost/LightGBM với cùng giao diện fit(Xf, Xd, y) / predict_proba(Xf, Xd)."""

    family = "ml"

    def __init__(self, name: str, algo: str, kind: str, monotone: bool = False, seed: int = 42) -> None:
        self.name, self.algo, self.kind, self.monotone, self.seed = name, algo, kind, monotone, seed
        self.cfg = load_config("eval")["ml"]
        self.pre: ColumnTransformer | None = None
        self.est = None
        self.best_iter: int | None = None

    def _X(self, Xf: pd.DataFrame, Xd: pd.DataFrame) -> pd.DataFrame:
        return cont_frame(Xf) if self.kind == "cont" else disc_frame(Xd)

    def _params(self, algo: str) -> dict:
        p = dict(self.cfg[algo])
        tuned = p.pop("tuned_params_file", None)
        if tuned and path(tuned).exists():
            p.update(json.loads(path(tuned).read_text()))
        return p

    def fit(self, Xf: pd.DataFrame, Xd: pd.DataFrame, y: np.ndarray) -> "MLModel":
        X = self._X(Xf, Xd)
        scale = self.algo in ("lr", "mlp", "rf")
        self.pre = preprocessor(self.kind, scale)
        if self.algo in ("xgboost", "lightgbm"):
            Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=self.cfg["inner_val_frac"], stratify=y,
                                                  random_state=self.seed)
            A, V = self.pre.fit_transform(Xtr), self.pre.transform(Xva)
            p = self._params(self.algo)
            es = p.pop("early_stopping_rounds")
            if self.algo == "xgboost":
                from xgboost import XGBClassifier

                if self.monotone:
                    names = list(self.pre.get_feature_names_out())
                    mono = self.cfg["monotone"]
                    p["monotone_constraints"] = tuple(mono.get(n.split("__", 1)[1], 0) for n in names)
                self.est = XGBClassifier(**p, tree_method="hist", eval_metric="logloss", early_stopping_rounds=es,
                                         random_state=self.seed, n_jobs=-1, verbosity=0)
                self.est.fit(A, ytr, eval_set=[(V, yva)], verbose=False)
                self.best_iter = int(self.est.best_iteration)
            else:
                import lightgbm as lgb

                self.est = lgb.LGBMClassifier(**p, random_state=self.seed, n_jobs=-1, verbose=-1)
                self.est.fit(A, ytr, eval_set=[(V, yva)], callbacks=[lgb.early_stopping(es, verbose=False)])
                self.best_iter = int(self.est.best_iteration_)
            return self
        A = self.pre.fit_transform(X)
        if self.algo == "lr":
            self.est = LogisticRegression(max_iter=2000, C=1.0)
        elif self.algo == "rf":
            self.est = RandomForestClassifier(**self.cfg["rf"], n_jobs=-1, random_state=self.seed)
        elif self.algo == "mlp":
            c = dict(self.cfg["mlp"])
            c["hidden_layer_sizes"] = tuple(c["hidden_layer_sizes"])
            self.est = MLPClassifier(**c, random_state=self.seed)
        self.est.fit(A, y)
        return self

    def transform(self, Xf: pd.DataFrame, Xd: pd.DataFrame) -> np.ndarray:
        return self.pre.transform(self._X(Xf, Xd))

    def predict_proba(self, Xf: pd.DataFrame, Xd: pd.DataFrame) -> np.ndarray:
        return self.est.predict_proba(self.transform(Xf, Xd))[:, 1]

    def feature_names(self) -> list[str]:
        return list(self.pre.get_feature_names_out())


def tune_xgboost(n_trials: int | None = None, timeout: int | None = None) -> dict:
    """Optuna (TPE) cho XGBoost trên seed đầu, fold 0: train của fold tách tiếp train/val nội bộ.
    KHÔNG dùng tập test. Lưu tham số tốt nhất -> experiments/tuning/xgboost.json."""
    import optuna
    from xgboost import XGBClassifier
    from sklearn.metrics import log_loss

    from src.data.home_credit import load_features
    from src.evaluation.cv import fold_data, load_splits

    cfg = load_config("eval")
    tcfg = cfg["tuning"]
    feat = load_features()
    seed = cfg["cv"]["seeds"][0]
    fd = fold_data(feat, load_splits(feat)[seed] != 0)
    X = cont_frame(fd.train_f)
    Xtr, Xva, ytr, yva = train_test_split(X, fd.y_train, test_size=0.2, stratify=fd.y_train, random_state=seed)
    pre = preprocessor("cont", scale=False)
    A, V = pre.fit_transform(Xtr), pre.transform(Xva)

    def objective(trial: "optuna.Trial") -> float:
        p = {"max_depth": trial.suggest_int("max_depth", 3, 8),
             "min_child_weight": trial.suggest_float("min_child_weight", 1, 100, log=True),
             "subsample": trial.suggest_float("subsample", 0.5, 1.0),
             "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
             "reg_lambda": trial.suggest_float("reg_lambda", 1e-2, 30, log=True),
             "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.15, log=True)}
        m = XGBClassifier(**p, n_estimators=2000, tree_method="hist", eval_metric="logloss",
                          early_stopping_rounds=100, random_state=seed, n_jobs=-1, verbosity=0)
        m.fit(A, ytr, eval_set=[(V, yva)], verbose=False)
        return log_loss(yva, m.predict_proba(V)[:, 1])

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=seed))
    t0 = time.time()
    study.optimize(objective, n_trials=n_trials or tcfg["n_trials"], timeout=timeout or tcfg["timeout_s"])
    out = path(cfg["ml"]["xgboost"]["tuned_params_file"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(study.best_params, indent=2))
    trials = study.trials_dataframe()
    trials.to_csv(out.with_name("xgboost_trials.csv"), index=False)
    print(f"[tune] {len(study.trials)} trial trong {time.time() - t0:.0f}s; logloss val tốt nhất "
          f"{study.best_value:.5f}; tham số -> {out}")
    return study.best_params

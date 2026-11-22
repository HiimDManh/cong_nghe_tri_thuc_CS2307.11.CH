"""Điểm vào thống nhất, dùng được cả khi không có `make` (Windows):

    python -m src.cli data     # tải dữ liệu thô
    python -m src.cli eda      # EDA German Credit + Home Credit -> reports/eda/
    python -m src.cli knowledge  # tải tri thức vĩ mô (World Bank, WHO) -> knowledge_base/
    python -m src.cli dag      # kiểm tra + vẽ DAG BN-Expert, mức ủng hộ của dữ liệu cho từng cạnh
    python -m src.cli train    # học BN-Expert(+Mono) trên toàn bộ dữ liệu -> models/*.json (cho demo)
    python -m src.cli tune     # Optuna cho XGBoost (≤ 25 trial, ~5 phút) -> experiments/tuning/
    python -m src.cli eval [thí nghiệm ...]  # thực nghiệm G4 -> experiments/, reports/ (mặc định: tất cả)
    python -m src.cli llm      # đánh giá độ trung thành của lời khuyên LLM -> experiments/llm_faithfulness/
    python -m src.cli report   # ghép chương + bảng số liệu -> reports/report.md
    python -m src.cli app      # chạy Streamlit demo
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from src.common import load_config, path, set_seed, utf8_stdout


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="src.cli")
    parser.add_argument("step", choices=["data", "eda", "knowledge", "dag", "train", "tune", "eval", "llm", "report", "app"])
    parser.add_argument("extra", nargs="*", help="eval: tên thí nghiệm")
    args = parser.parse_args(argv)
    utf8_stdout()
    set_seed(load_config("data")["seed"])

    if args.step == "data":
        from src.data.download import main as download

        download()
    elif args.step == "eda":
        from src.data.eda import run
        from src.data.eda_home_credit import run as run_hc

        run()
        if path("data", "raw", "application_train.csv").exists():
            run_hc()
    elif args.step == "knowledge":
        from src.knowledge.fetch_gso import main as fetch_gso
        from src.knowledge.fetch_macro import main as fetch_macro

        fetch_macro()
        fetch_gso()
    elif args.step == "train":
        from src.bn.train import main as train

        train()
    elif args.step == "tune":
        from src.baselines.ml import tune_xgboost

        tune_xgboost()
    elif args.step == "eval":
        from src.evaluation.run import main as run_eval

        run_eval(args.extra or None)
    elif args.step == "llm":
        from src.llm.evaluate import main as llm_eval

        llm_eval()
    elif args.step == "report":
        from src.evaluation.report import main as build_report

        build_report()
    elif args.step == "dag":
        from src.bn.structure import main as dag

        dag()
    elif args.step == "app":
        app = path("src", "app", "streamlit_app.py")
        if not app.exists():
            sys.exit("Chưa có Streamlit app (giai đoạn 5).")
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app)], check=True)
    else:
        sys.exit(f"Bước '{args.step}' chưa được cài đặt (xem docs/TASKS.md).")


if __name__ == "__main__":
    main()

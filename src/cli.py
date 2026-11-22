"""Điểm vào thống nhất, dùng được cả khi không có `make` (Windows):

    python -m src.cli data     # tải dữ liệu thô
    python -m src.cli eda      # EDA nhanh
    python -m src.cli train    # (giai đoạn 3)
    python -m src.cli eval     # (giai đoạn 4)
    python -m src.cli app      # chạy Streamlit demo (giai đoạn 5)
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from src.common import load_config, path, set_seed, utf8_stdout


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="src.cli")
    parser.add_argument("step", choices=["data", "eda", "train", "eval", "app"])
    args = parser.parse_args(argv)
    utf8_stdout()
    set_seed(load_config("data")["seed"])

    if args.step == "data":
        from src.data.download import main as download

        download()
    elif args.step == "eda":
        from src.data.eda import run

        run()
    elif args.step == "app":
        app = path("src", "app", "streamlit_app.py")
        if not app.exists():
            sys.exit("Chưa có Streamlit app (giai đoạn 5).")
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app)], check=True)
    else:
        sys.exit(f"Bước '{args.step}' chưa được cài đặt (xem docs/TASKS.md).")


if __name__ == "__main__":
    main()

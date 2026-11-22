"""Tải dữ liệu thô vào `data/raw/`.

- German Credit (OpenML `credit-g`): tải tự động, không cần tài khoản.
- Home Credit Default Risk (Kaggle): tải tay vào data/raw/, hoặc qua API nếu có token
  (`~/.kaggle/access_token`, biến `KAGGLE_API_TOKEN`, hoặc `kaggle.json` kiểu cũ – KHÔNG commit).
  Phải bấm "I understand and accept" luật cuộc thi trên Kaggle. Thiếu token -> in hướng dẫn, không lỗi.\n"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pandas as pd

from src.common import load_config, path, utf8_stdout


def download_german_credit(force: bool = False) -> Path:
    """Tải German Credit từ OpenML, lưu CSV vào data/raw/. Trả về đường dẫn file."""
    cfg = load_config("data")["datasets"]["german_credit"]
    out = path(load_config("data")["paths"]["raw"], cfg["raw_file"])
    if out.exists() and not force:
        print(f"[german_credit] đã có: {out}")
        return out
    from sklearn.datasets import fetch_openml

    ds = fetch_openml(name=cfg["openml_name"], version=cfg["openml_version"], as_frame=True, parser="auto")
    df: pd.DataFrame = ds.frame
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"[german_credit] đã lưu {df.shape} -> {out}")
    return out


def _kaggle_credentials_present() -> bool:
    """Có thông tin xác thực Kaggle ở bất kỳ dạng nào mà thư viện `kaggle` 2.x hỗ trợ không."""
    kdir = Path.home() / ".kaggle"
    return bool(
        os.environ.get("KAGGLE_API_TOKEN")
        or (os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"))
        or any((kdir / n).exists() for n in ("access_token", "access_token.txt", "kaggle.json"))
    )


def download_home_credit(force: bool = False) -> Path | None:
    """Tải application_train.csv của Home Credit qua Kaggle API. Trả về None nếu không tải được."""
    cfg = load_config("data")["datasets"]["home_credit"]
    raw_dir = path(load_config("data")["paths"]["raw"])
    out = raw_dir / cfg["raw_file"]
    if out.exists() and not force:
        print(f"[home_credit] đã có: {out}")
        return out
    guide = (
        "  Cách 1 (không cần token): tải tay application_train.csv tại\n"
        "          https://www.kaggle.com/competitions/home-credit-default-risk/data\n"
        f"          và đặt vào {out}\n"
        "  Cách 2: Kaggle > Settings > API > Generate New Token, lưu token vào\n"
        f"          {Path.home() / '.kaggle' / 'access_token'}  rồi chạy lại `python -m src.cli data`.\n"
        "  Cả hai cách đều phải bấm 'I understand and accept' luật cuộc thi trên Kaggle trước."
    )
    if not _kaggle_credentials_present():
        print("[home_credit] CHƯA có Kaggle token -> bỏ qua.\n" + guide)
        return None
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        raw_dir.mkdir(parents=True, exist_ok=True)
        api.competition_download_file(cfg["kaggle_competition"], cfg["raw_file"], path=str(raw_dir), force=force)
    except (Exception, SystemExit) as e:  # thư viện kaggle có thể gọi sys.exit khi lỗi xác thực
        print(f"[home_credit] tải thất bại ({type(e).__name__}: {e}).\n" + guide)
        return None
    zipped = raw_dir / f"{cfg['raw_file']}.zip"
    if zipped.exists():
        with zipfile.ZipFile(zipped) as z:
            z.extractall(raw_dir)
        zipped.unlink()
    print(f"[home_credit] đã lưu -> {out}")
    return out


def main() -> None:
    utf8_stdout()
    download_german_credit()
    download_home_credit()


if __name__ == "__main__":
    main()

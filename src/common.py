"""Tiện ích dùng chung: đường dẫn gốc repo, đọc cấu hình YAML, cố định seed."""
from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Any

import numpy as np
import yaml

ROOT: Path = Path(__file__).resolve().parents[1]


def load_config(name: str = "data") -> dict[str, Any]:
    """Đọc `configs/<name>.yaml` và trả về dict."""
    with open(ROOT / "configs" / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def path(*parts: str) -> Path:
    """Đường dẫn tuyệt đối tính từ gốc repo."""
    return ROOT.joinpath(*parts)


def utf8_stdout() -> None:
    """Ép stdout/stderr sang UTF-8 (console Windows mặc định cp1252 không in được tiếng Việt)."""
    import sys

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def set_seed(seed: int = 42) -> None:
    """Cố định seed cho random, numpy và biến môi trường PYTHONHASHSEED."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

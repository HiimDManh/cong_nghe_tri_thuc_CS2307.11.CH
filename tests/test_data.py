"""Kiểm tra dữ liệu German Credit sau khi tải (bỏ qua nếu chưa chạy `python -m src.cli data`)."""
import pytest

from src.common import load_config, path


@pytest.fixture(scope="module")
def german():
    cfg = load_config("data")
    f = path(cfg["paths"]["raw"], cfg["datasets"]["german_credit"]["raw_file"])
    if not f.exists():
        pytest.skip("Chưa tải German Credit")
    from src.data.eda import load_german

    return load_german()


def test_german_shape(german):
    assert german.shape == (1000, 21)


def test_german_default_rate(german):
    # Bộ dữ liệu chuẩn có 300 hồ sơ bad / 1000.
    assert german["default"].sum() == 300

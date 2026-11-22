# Trên Windows không có make: dùng trực tiếp `python -m src.cli <bước>`.
PY ?= python

.PHONY: data eda train eval app test

data:
	$(PY) -m src.cli data

eda:
	$(PY) -m src.cli eda

train:
	$(PY) -m src.cli train

eval:
	$(PY) -m src.cli eval

app:
	$(PY) -m src.cli app

test:
	$(PY) -m pytest -q

# Trên Windows không có make: dùng trực tiếp `python -m src.cli <bước>`.
PY ?= python

.PHONY: data eda knowledge dag train eval app test

data:
	$(PY) -m src.cli data

eda:
	$(PY) -m src.cli eda

knowledge:
	$(PY) -m src.cli knowledge

dag:
	$(PY) -m src.cli dag

train:
	$(PY) -m src.cli train

eval:
	$(PY) -m src.cli eval

app:
	$(PY) -m src.cli app

test:
	$(PY) -m pytest -q

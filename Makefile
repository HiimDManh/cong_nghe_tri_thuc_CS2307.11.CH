# Trên Windows không có make: dùng trực tiếp `python -m src.cli <bước>`.
PY ?= python

.PHONY: data eda knowledge dag train tune eval llm report app test

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

tune:
	$(PY) -m src.cli tune

eval:
	$(PY) -m src.cli eval

llm:
	$(PY) -m src.cli llm

report:
	$(PY) -m src.cli report

app:
	$(PY) -m src.cli app

test:
	$(PY) -m pytest -q

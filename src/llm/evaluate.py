"""Đánh giá lời khuyên LLM trên ~50 hồ sơ: độ trung thành tự động + file để nhóm chấm tay.

    python -m src.cli llm

Chạy mọi provider có key (gemini/groq/ollama) + `template` (mốc) + `template_corrupted` (đối chứng âm: lời
khuyên bị cố ý sửa sai số/hướng – để chứng minh bộ kiểm tra bắt được lỗi).
-> experiments/llm_faithfulness/results.csv, samples_for_rating.csv (cột trống cho người chấm).
"""
from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from src.bn.core import DiscreteBN
from src.common import load_config, path, utf8_stdout
from src.data.discretize import Discretizer
from src.data.home_credit import load_features
from src.llm.client import LLMClient, available_providers
from src.llm.facts import INPUTS, build_facts
from src.llm.faithfulness import check
from src.llm.prompt import template_advice


def sample_profiles(n: int, seed: int) -> list[dict[str, str]]:
    """Hồ sơ đa dạng: lấy mẫu phân tầng theo ngành từ Home Credit; 30% hồ sơ bị ẩn 1–3 biến (người dùng không biết)."""
    feat = load_features()
    disc = Discretizer().load(path("models", "discretizer.json"))
    X = disc.transform(feat)
    rng = np.random.default_rng(seed)
    per = max(1, n // X["sector"].nunique())
    idx = X.groupby("sector", group_keys=False).apply(lambda g: g.sample(per, random_state=seed)).index[:n]
    out = []
    for i in idx:
        prof = {k: X.at[i, k] for k in INPUTS}
        if rng.random() < 0.3:
            for k in rng.choice(INPUTS, rng.integers(1, 4), replace=False):
                prof[k] = None
        out.append({"id": int(feat.at[i, "id"]), **prof})
    return out


def corrupt(text: str, facts: dict) -> str:
    """Đối chứng âm: đổi điểm và nói ngược hướng yếu tố mạnh nhất."""
    t = text.replace(str(facts["diem"]), str(facts["diem"] + 37), 1)
    if facts["yeu_to_keo_diem_xuong"]:
        t = re.sub(r"kéo điểm xuống", "giúp tăng", t, count=1)
    return t


def main() -> None:
    utf8_stdout()
    cfg = load_config("llm")["evaluation"]
    bn = DiscreteBN.from_json(path("models", "bn_expert_mono.json"))
    profiles = sample_profiles(cfg["n_profiles"], cfg["seed"])
    providers = [p for p in available_providers() if p != "template"]
    clients = []
    for p in providers:
        clients.append(LLMClient(p))
        clients += [LLMClient(p, m["model"], m.get("extra")) for m in cfg.get("compare_models", {}).get(p, [])]
    print(f"[llm] {len(profiles)} hồ sơ; model: {[c.label for c in clients] or 'không có'} (+ template, đối chứng âm)")
    rows, rating = [], []
    for k, prof in enumerate(profiles):
        pid = prof.pop("id")
        facts = build_facts(bn, prof)
        base = template_advice(facts)
        outputs = [("template", "template", base, 0.0, None), ("template_corrupted", "template", corrupt(base, facts), 0.0, None)]
        for c in clients:
            a = c.advise(facts)
            outputs.append((c.label if a.error is None else f"{c.label}_failed", c.model, a.text, a.latency_s, a.error))
        for prov, model, text, lat, err in outputs:
            rows.append({"profile": k, "sk_id": pid, "provider": prov, "model": model, "latency_s": lat,
                         "error": err, "n_words": len(text.split()), **check(text, facts)})
            if prov not in ("template_corrupted",):
                rating.append({"profile": k, "provider": prov, "diem_bn": facts["diem"], "muc": facts["muc_rui_ro"],
                               "facts_json": json.dumps(facts, ensure_ascii=False), "loi_khuyen": text,
                               "nguoi_cham": "", "dung_du_kien_1_5": "", "de_hieu_1_5": "", "huu_ich_1_5": "",
                               "ghi_chu": ""})
        if (k + 1) % 10 == 0:
            print(f"[llm] {k + 1}/{len(profiles)}")
    out = path("experiments", "llm_faithfulness")
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "results.csv", index=False)
    pd.DataFrame(rating).to_csv(out / "samples_for_rating.csv", index=False, encoding="utf-8-sig")
    print(df.groupby("provider")[["number_precision", "fact_coverage", "direction_ok", "faithful"]].mean().round(3))

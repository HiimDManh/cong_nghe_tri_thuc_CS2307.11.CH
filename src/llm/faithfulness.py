"""Kiểm tra tự động độ trung thành của lời khuyên với dữ kiện BN (LLM không được bịa số).

1. number_precision: tỷ lệ con số trong lời khuyên khớp một con số trong dữ kiện (cho phép làm tròn).
2. fact_coverage: có nhắc (a) điểm, (b) mức rủi ro, (c) yếu tố kéo điểm xuống mạnh nhất (nếu có).
3. direction_ok: (trong phần mô tả yếu tố, trước mục "Nên làm gì") câu nhắc tới một yếu tố không được nói ngược hướng (yếu tố kéo xuống mà gọi là
   "giúp tăng/điểm mạnh", hoặc ngược lại) – luật heuristic, ghi rõ hạn chế trong báo cáo.
"""
from __future__ import annotations

import json
import re

NUM = re.compile(r"(?<![\w.])\d{1,3}(?:[.\s]\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?")
LIST_MARK = re.compile(r"^\s*(?:\d+[.)]|[-*•])\s+", re.M)
POS = ("giúp tăng", "điểm mạnh", "tích cực", "cộng điểm", "lợi thế", "giúp điểm")
NEG = ("kéo điểm xuống", "kéo xuống", "làm giảm", "tiêu cực", "bất lợi", "rủi ro cao", "trừ điểm")


def _to_float(s: str) -> float:
    s = s.strip()
    if re.fullmatch(r"\d{1,3}(?:[.\s]\d{3})+(?:,\d+)?", s):  # 1.500.000 hoặc 1 500 000
        s = re.sub(r"[.\s]", "", s).replace(",", ".")
    else:
        s = s.replace(",", ".")
    return float(s)


def numbers(text: str) -> list[float]:
    text = LIST_MARK.sub("", text)
    text = re.sub(r"\*\*", "", text)
    return [_to_float(m.group()) for m in NUM.finditer(text)]


def allowed_numbers(facts: dict) -> set[float]:
    s = json.dumps(facts, ensure_ascii=False)
    vals = {abs(v) for v in numbers(s)} | {300.0, 850.0}
    return vals


def _match(x: float, allowed: set[float]) -> bool:
    for a in allowed:
        if abs(x - a) <= 0.051 or (float(x).is_integer() and abs(x - a) < 0.5):
            return True
    return False


def check(text: str, facts: dict) -> dict:
    allowed = allowed_numbers(facts)
    nums = numbers(text)
    bad = [x for x in nums if not _match(abs(x), allowed)]
    prec = 1.0 if not nums else 1 - len(bad) / len(nums)
    low = text.lower()
    req = [str(facts["diem"]) in text, facts["muc_rui_ro"].lower() in low]
    if facts.get("yeu_to_keo_diem_xuong"):
        req.append(facts["yeu_to_keo_diem_xuong"][0]["label"].lower().split(" (")[0] in low)
    cov = sum(req) / len(req)
    direction_ok = True
    # chỉ xét phần mô tả yếu tố (trước mục khuyến nghị: ở đó "tăng thu nhập", "hạn chế…" là hành động, không phải hướng)
    head = re.split(r"nên làm gì|khuyến nghị", low, maxsplit=1)[0]
    sentences = re.split(r"(?<=[.!?\n])", head)
    for key, wrong in (("yeu_to_keo_diem_xuong", POS), ("yeu_to_giup_diem", NEG)):
        for c in facts.get(key, []):
            lab = re.compile(r"(?<![\w/])" + re.escape(c["label"].lower().split(" (")[0]) + r"(?![\w/])")
            for snt in sentences:
                if lab.search(snt) and any(w in snt for w in wrong) and not any(
                        w in snt for w in (NEG if wrong is POS else POS)):
                    direction_ok = False
    return {"n_numbers": len(nums), "unsupported_numbers": ";".join(f"{x:g}" for x in bad),
            "number_precision": prec, "fact_coverage": cov, "direction_ok": direction_ok,
            "faithful": bool(prec == 1.0 and cov == 1.0 and direction_ok)}

"""Ghép báo cáo: reports/chapters/*.md (văn bản) + reports/results/ (bảng, số do script sinh) -> reports/report.md.

Placeholder trong chương:
  {{table:main_cv}}            -> nội dung reports/results/main_cv.md
  {{num:auc.BN-Expert-Mono}}   -> giá trị trong reports/results/key_numbers.json
  {{fig:exp_roc.png|Chú thích}} -> ảnh reports/figures/exp_roc.png
  {{file:reports/bn/expert_params.md}} -> chèn nguyên file (đường dẫn từ gốc repo)
Comment HTML (<!-- gợi ý -->) bị bỏ khi ghép. Placeholder không tìm thấy -> ⟦THIẾU …⟧ trong báo cáo + cảnh báo (không bao giờ tự điền số).

    python -m src.cli report
"""
from __future__ import annotations

import json
import re

from src.common import path, utf8_stdout

PAT = re.compile(r"\{\{(table|num|fig|file):([^}|]+)(?:\|([^}]*))?\}\}")


def render(text: str, key: dict, missing: list[str]) -> str:
    def sub(m: re.Match) -> str:
        kind, arg, cap = m.group(1), m.group(2).strip(), (m.group(3) or "").strip()
        if kind == "num":
            if arg in key:
                return str(key[arg])
        elif kind == "table":
            f = path("reports", "results", f"{arg}.md")
            if f.exists():
                return f.read_text(encoding="utf-8")
        elif kind == "fig":
            if path("reports", "figures", arg).exists():
                return f"![{cap or arg}](figures/{arg})\n\n*Hình: {cap}*" if cap else f"![{arg}](figures/{arg})"
        elif kind == "file":
            f = path(*arg.split("/"))
            if f.exists():
                body = f.read_text(encoding="utf-8")
                return re.sub(r"^# ", "#### ", body, flags=re.M)
        missing.append(m.group(0))
        return f"⟦THIẾU {m.group(0)[2:-2]}⟧"

    text = re.sub(r"<!--.*?-->\n?", "", text, flags=re.S)  # ô gợi ý cho người viết không vào báo cáo
    return PAT.sub(sub, text)


def main() -> None:
    utf8_stdout()
    kf = path("reports", "results", "key_numbers.json")
    key = json.loads(kf.read_text(encoding="utf-8")) if kf.exists() else {}
    chapters = sorted(path("reports", "chapters").glob("*.md"))
    missing: list[str] = []
    parts = ["<!-- SINH TỰ ĐỘNG bởi `python -m src.cli report` từ reports/chapters/*.md + reports/results/. "
             "Sửa văn bản trong reports/chapters/, KHÔNG sửa file này. -->"]
    parts += [render(c.read_text(encoding="utf-8"), key, missing) for c in chapters]
    out = path("reports", "report.md")
    out.write_text("\n\n".join(parts), encoding="utf-8")
    print(f"[report] {len(chapters)} chương -> {out}")
    if missing:
        print(f"[report] CẢNH BÁO: {len(missing)} placeholder chưa có dữ liệu: {sorted(set(missing))[:10]}")

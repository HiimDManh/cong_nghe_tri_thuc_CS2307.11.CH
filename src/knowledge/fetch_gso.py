"""Trích số liệu Khảo sát mức sống dân cư (KSMS/VHLSS) 2024 của Cục Thống kê (NSO/GSO).

Nguồn: thông cáo báo chí KSMS 2024 (16/05/2025) và file biểu số liệu chính thức:
  https://www.nso.gov.vn/wp-content/uploads/2025/05/bieu-so-lieu-cong-bo-ksms2024.xlsx
- Biểu 4:  Thu nhập bình quân đầu người/tháng 2024 theo 5 nhóm thu nhập (nghìn đồng)
- Biểu 11: Chi tiêu cho đời sống bình quân đầu người/tháng 2024 theo 5 nhóm thu nhập (nghìn đồng)
-> knowledge_base/vn_income_spending_quintiles_2024.csv

Dùng cho: (1) demo quy đổi thu nhập VND -> ngũ phân vị (nút Thu nhập);
          (2) tỷ lệ chi tiêu/thu nhập theo nhóm -> CPT Chi phí sinh hoạt & suy luận ngược về chi tiêu.
"""
from __future__ import annotations

from datetime import date

import pandas as pd

from src.common import path, utf8_stdout

URL = "https://www.nso.gov.vn/wp-content/uploads/2025/05/bieu-so-lieu-cong-bo-ksms2024.xlsx"
PRESS = "https://nso.gov.vn/tin-tuc-thong-ke/2025/05/thong-cao-bao-chi-ket-qua-khao-sat-muc-song-dan-cu-nam-2024/"
ROWS = {"CẢ NƯỚC": "national", "Thành thị": "urban", "Nông thôn": "rural"}
SHEETS = {"4": "income_per_capita_month", "11": "living_expenditure_per_capita_month"}


def _download() -> pd.ExcelFile:
    import requests

    f = path("data", "raw", "ksms2024.xlsx")
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(URL, timeout=60)
        r.raise_for_status()
        f.write_bytes(r.content)
    return pd.ExcelFile(f)


def extract() -> pd.DataFrame:
    xl = _download()
    rows = []
    for sheet, indicator in SHEETS.items():
        d = pd.read_excel(xl, sheet_name=sheet, header=None)
        for _, r in d.iterrows():
            key = str(r.iloc[0]).strip()
            if key in ROWS:
                for q, v in zip(["all", "Q1", "Q2", "Q3", "Q4", "Q5"], r.iloc[1:7]):
                    rows.append({"indicator": indicator, "area": ROWS[key], "quintile": q,
                                 "value_thousand_vnd": round(float(v), 2), "year": 2024,
                                 "table": f"Biểu {sheet}", "source_url": URL, "press_release": PRESS,
                                 "retrieved": date.today().isoformat()})
    return pd.DataFrame(rows)


def main() -> None:
    utf8_stdout()
    df = extract()
    out = path("knowledge_base", "vn_income_spending_quintiles_2024.csv")
    df.to_csv(out, index=False)
    p = df[df.area == "national"].pivot(index="quintile", columns="indicator", values="value_thousand_vnd")
    p["spend_to_income"] = (p.iloc[:, 1] / p.iloc[:, 0]).round(3)
    print(f"[gso] {len(df)} dòng -> {out}\n{p}")


if __name__ == "__main__":
    main()

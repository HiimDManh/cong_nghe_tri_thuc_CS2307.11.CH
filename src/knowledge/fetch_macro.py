"""Tải chỉ số vĩ mô Việt Nam từ World Bank API -> knowledge_base/macro_vn_worldbank.csv.

Dùng làm căn cứ cho CPT các nút tri thức chuyên gia (Lạm phát, Chu kỳ kinh tế, Rủi ro thất nghiệp,
Biến cố sức khỏe). Mỗi dòng có `source_url` và ngày truy xuất để trích dẫn.
"""
from __future__ import annotations

from datetime import date

import pandas as pd

from src.common import path, utf8_stdout

COUNTRY = "VNM"
YEARS = range(2000, 2025)
INDICATORS = {
    "FP.CPI.TOTL.ZG": "Lạm phát, giá tiêu dùng (% năm)",
    "SL.UEM.TOTL.ZS": "Tỷ lệ thất nghiệp (% lực lượng lao động, ước tính ILO)",
    "NY.GDP.MKTP.KD.ZG": "Tăng trưởng GDP (% năm)",
    "SH.XPD.OOPC.CH.ZS": "Chi y tế tự chi trả (% tổng chi y tế hiện hành)",
}


def fetch() -> pd.DataFrame:
    import wbgapi as wb

    rows = []
    for code, name in INDICATORS.items():
        for rec in wb.data.fetch(code, COUNTRY, time=YEARS):
            if rec["value"] is None:
                continue
            rows.append({
                "indicator_code": code,
                "indicator_name": name,
                "country": COUNTRY,
                "year": int(str(rec["time"]).removeprefix("YR")),
                "value": round(float(rec["value"]), 4),
                "source_url": f"https://data.worldbank.org/indicator/{code}?locations=VN",
                "retrieved": date.today().isoformat(),
            })
    return pd.DataFrame(rows).sort_values(["indicator_code", "year"])


WHO_GHO = "https://ghoapi.azureedge.net/api/"
WHO_INDICATORS = {  # SDG 3.8.2 – chi tiêu y tế thảm họa (World Bank đã lưu trữ series SH.UHC.OOPC.*)
    "FINPROTECTION_CATA_TOT_10_POP": "Dân số có chi y tế tự trả > 10% tổng chi tiêu/thu nhập hộ (%)",
    "FINPROTECTION_CATA_TOT_25_POP": "Dân số có chi y tế tự trả > 25% tổng chi tiêu/thu nhập hộ (%)",
}


def fetch_health() -> pd.DataFrame:
    """Chi tiêu y tế thảm họa của VN từ WHO GHO (có phân tách tuổi, thành thị/nông thôn, hộ gia đình)."""
    import requests

    rows = []
    for code, name in WHO_INDICATORS.items():
        r = requests.get(WHO_GHO + code, params={"$filter": f"SpatialDim eq '{COUNTRY}'"}, timeout=60)
        r.raise_for_status()
        for d in r.json()["value"]:
            if d.get("NumericValue") is None:
                continue
            rows.append({
                "indicator_code": code, "indicator_name": name, "country": COUNTRY,
                "year": int(d["TimeDim"]), "breakdown": d.get("Dim1"), "value": round(float(d["NumericValue"]), 2),
                "source_url": f"https://www.who.int/data/gho/data/indicators (API: {WHO_GHO}{code})",
                "retrieved": date.today().isoformat(),
            })
    return pd.DataFrame(rows).sort_values(["indicator_code", "breakdown", "year"])


def main() -> None:
    utf8_stdout()
    h = fetch_health()
    out_h = path("knowledge_base", "health_catastrophic_vn_who.csv")
    h.to_csv(out_h, index=False)
    print(f"[health] {len(h)} dòng -> {out_h}")
    print(h[h.breakdown.isin(["RESIDENCEAREATYPE_TOTL", "AGEGROUP_AGELT60", "AGEGROUP_AGE60+"])]
          .pivot_table(index="year", columns=["indicator_code", "breakdown"], values="value").tail(6).to_string())
    df = fetch()
    out = path("knowledge_base", "macro_vn_worldbank.csv")
    df.to_csv(out, index=False)
    print(f"[macro] {len(df)} dòng -> {out}")
    print(df.pivot(index="year", columns="indicator_code", values="value").tail(12).to_string())


if __name__ == "__main__":
    main()

"""Demo Streamlit – Dự báo khả năng tài chính cá nhân theo ngành nghề (Mạng Bayes).

    python -m src.cli app        # hoặc: streamlit run src/app/streamlit_app.py

Mô hình chính: BN-Expert-Mono (models/bn_expert_mono.json, học trên toàn bộ Home Credit).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import streamlit as st

from src.app.convert import UserInput, from_row, gso_quintile_bounds, to_profile
from src.app.labels import node_vi, state_vi
from src.baselines.fico import FicoScorer
from src.bn.backward import backward_posterior, counterfactual_search
from src.bn.core import DiscreteBN
from src.bn.model import risk_band, to_score
from src.common import load_config, path
from src.llm.client import LLMClient, available_providers
from src.llm.facts import INPUTS, build_facts, contributions
from src.llm.faithfulness import check

st.set_page_config(page_title="Dự báo tài chính cá nhân – Mạng Bayes", page_icon="📊", layout="wide")
UNK = "— Không rõ —"


# ----------------------------------------------------------------------------- tải mô hình
@st.cache_resource
def load_models() -> dict:
    m = {"BN-Expert-Mono": DiscreteBN.from_json(path("models", "bn_expert_mono.json")),
         "BN-Expert": DiscreteBN.from_json(path("models", "bn_expert.json"))}
    try:
        import xgboost as xgb

        b = xgb.Booster()
        b.load_model(path("models", "xgb_disc.json"))
        m["xgb"] = (b, json.loads(path("models", "xgb_disc_features.json").read_text(encoding="utf-8")))
    except Exception:
        m["xgb"] = None
    return m


def xgb_proba(model, profile: dict) -> float | None:
    if model is None:
        return None
    import xgboost as xgb

    booster, names = model
    row = np.zeros((1, len(names)))
    for j, n in enumerate(names):
        col_state = n.split("__", 1)[1]
        for k, v in profile.items():
            if col_state == f"{k}_{v if v is not None else 'missing'}":
                row[0, j] = 1.0
    return float(booster.predict(xgb.DMatrix(row, feature_names=None))[0])


def fico_score(profile: dict) -> float:
    X = pd.DataFrame([{k: v for k, v in profile.items()}])
    for c in ("ext_score_mean", "annuity_to_income", "credit_to_income", "age_years", "bureau_inquiries_year", "assets"):
        if c not in X:
            X[c] = None
    return float(FicoScorer().score(X)[0])


def opts(node: str, bn: DiscreteBN, exclude: tuple[str, ...] = ()) -> list[str]:
    return [UNK] + [s for s in bn.states[node] if s not in exclude]


def pick(label: str, node: str, bn: DiscreteBN, default: str | None, key: str, exclude: tuple[str, ...] = ()) -> str | None:
    o = opts(node, bn, exclude)
    i = o.index(default) if default in o else 0
    v = st.selectbox(label, o, index=i, key=key, format_func=lambda s: s if s == UNK else state_vi(node, s))
    return None if v == UNK else v


def num(label: str, default: float | None, key: str, **kw) -> float | None:
    c1, c2 = st.columns([4, 1])
    with c2:
        unknown = st.checkbox("?", value=default is None, key=key + "_unk", help="Không rõ / không muốn khai")
    with c1:
        v = st.number_input(label, value=float(default) if default is not None else float(kw.get("min_value", 0)),
                            key=key, disabled=unknown, **kw)
    return None if unknown else v


# ----------------------------------------------------------------------------- giao diện
models = load_models()
with st.sidebar:
    st.header("Cài đặt")
    model_name = st.radio("Mô hình BN", ["BN-Expert-Mono", "BN-Expert"],
                          help="Mono: có ràng buộc đơn điệu chuyên gia (DSTI ↑ → rủi ro không giảm; lịch sử tín dụng tốt "
                               "hơn → rủi ro không tăng). Đây là mô hình chính.")
    provider = st.selectbox("Nguồn lời khuyên (LLM)", available_providers(),
                            help="Cần GEMINI_API_KEY / GROQ_API_KEY trong .env hoặc Secrets. 'template' = không dùng LLM.")
    samples_f = path("data", "samples", "profiles.csv")
    sample = None
    if samples_f.exists():
        sp = pd.read_csv(samples_f, dtype=str, keep_default_na=False)
        name = st.selectbox("Nạp hồ sơ mẫu", ["(tự nhập)"] + sp["name"].tolist())
        if name != "(tự nhập)":
            sample = sp[sp["name"] == name].iloc[0].to_dict()
    st.caption("Dữ liệu học: Home Credit (307.511 hồ sơ). Tri thức vĩ mô: World Bank, WHO, GSO KSMS 2024. "
               "Đây là mô hình minh họa cho đồ án, không phải quyết định cho vay.")

bn: DiscreteBN = models[model_name]
u0 = from_row(sample) if sample else UserInput(sector="trade_hospitality", occupation_group="service_sales",
                                               education="secondary_or_lower", age=28, working=True, years_employed=2,
                                               household_income_m=18, household_size=3, personal_income_m=10,
                                               n_children=1, own_house=False, own_car=False, monthly_installment_m=2.5,
                                               total_debt_m=60, credit_history="fair", inquiries="1", region="2")
sk = (sample or {}).get("name", "manual")

st.title("📊 Dự báo khả năng tài chính cá nhân theo ngành nghề")
st.caption("Mạng Bayes: Ngành → Thu nhập → Biến cố → Khả năng vỡ nợ · suy luận xuôi (điểm 300–850) · suy luận ngược "
           "(cần thay đổi gì để đạt mục tiêu) · LLM diễn giải. Mọi trường đều có thể để **Không rõ** – Mạng Bayes tự "
           "lấy trung bình theo xác suất.")

with st.form("profile"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Nghề nghiệp")
        sector = pick("Ngành", "sector", bn, u0.sector, f"sector_{sk}", exclude=("not_working",))
        occ = pick("Nhóm nghề", "occupation_group", bn, u0.occupation_group, f"occ_{sk}")
        edu = pick("Học vấn", "education", bn, u0.education, f"edu_{sk}")
        working = st.radio("Tình trạng", ["Đang đi làm", "Không đi làm (hưu trí/thất nghiệp)"],
                           index=0 if u0.working is not False else 1, key=f"work_{sk}", horizontal=True)
        years = num("Thâm niên công việc hiện tại (năm)", u0.years_employed, f"years_{sk}", min_value=0.0,
                    max_value=50.0, step=0.5)
        age = num("Tuổi", u0.age, f"age_{sk}", min_value=18.0, max_value=90.0, step=1.0)
    with c2:
        st.subheader("Thu nhập & gia đình")
        hh_inc = num("Thu nhập cả hộ / tháng (triệu đồng)", u0.household_income_m, f"hh_{sk}", min_value=0.0, step=1.0)
        hh_size = num("Số người trong hộ", u0.household_size, f"hs_{sk}", min_value=1.0, max_value=20.0, step=1.0)
        p_inc = num("Thu nhập cá nhân / tháng (triệu đồng)", u0.personal_income_m, f"pi_{sk}", min_value=0.0, step=0.5)
        kids = num("Số con", u0.n_children, f"kids_{sk}", min_value=0.0, max_value=15.0, step=1.0)
        house = st.selectbox("Sở hữu nhà", [UNK, "Có", "Không"], key=f"house_{sk}",
                             index={None: 0, True: 1, False: 2}[u0.own_house])
        car = st.selectbox("Sở hữu xe ô tô", [UNK, "Có", "Không"], key=f"car_{sk}",
                           index={None: 0, True: 1, False: 2}[u0.own_car])
    with c3:
        st.subheader("Khoản vay & tín dụng")
        inst = num("Tổng tiền trả góp / tháng (triệu đồng)", u0.monthly_installment_m, f"inst_{sk}", min_value=0.0, step=0.5)
        debt = num("Tổng dư nợ (triệu đồng)", u0.total_debt_m, f"debt_{sk}", min_value=0.0, step=5.0)
        hist = pick("Lịch sử trả nợ (tự đánh giá)", "ext_score_mean", bn, u0.credit_history, f"hist_{sk}")
        inq = pick("Số lần hỏi vay / tra cứu tín dụng trong 12 tháng", "bureau_inquiries_year", bn, u0.inquiries,
                   f"inq_{sk}", exclude=("unknown",))
        region = pick("Khu vực sống", "region_rating", bn, u0.region, f"reg_{sk}")
    submitted = st.form_submit_button("Tính điểm", type="primary", width="stretch")

yn = {UNK: None, "Có": True, "Không": False}
u = UserInput(sector=sector, occupation_group=occ, education=edu, age=age, working=working == "Đang đi làm",
              years_employed=years, household_income_m=hh_inc, household_size=int(hh_size) if hh_size else None,
              personal_income_m=p_inc, n_children=int(kids) if kids is not None else None, own_house=yn[house],
              own_car=yn[car], monthly_installment_m=inst, total_debt_m=debt, credit_history=hist, inquiries=inq,
              region=region)
profile = to_profile(u)
ev = {k: v for k, v in profile.items() if v is not None}

with st.expander("Trạng thái BN sau quy đổi (giả định quy đổi)", expanded=False):
    b = [round(x / 1000, 2) for x in gso_quintile_bounds()]
    st.markdown(f"- Thu nhập: **bình quân đầu người của hộ** so với ranh giới ngũ phân vị VN 2024 (GSO KSMS 2024; "
                f"ranh giới = trung điểm giữa trung bình 2 nhóm kề nhau – *giả định*): {b} triệu/người/tháng.\n"
                "- DSTI = trả góp / thu nhập cá nhân; LTI = dư nợ / (12 × thu nhập cá nhân).\n"
                "- Lịch sử trả nợ tự đánh giá ↔ ngũ phân vị điểm tín dụng ngoài của Home Credit (*giả định*).\n"
                "- Khu vực: 1 = đô thị lớn, 2 = đô thị khác, 3 = nông thôn/vùng khó khăn (*giả định* ↔ xếp hạng vùng Home Credit).")
    st.dataframe(pd.DataFrame([{"Nút": node_vi()[k], "Trạng thái": state_vi(k, v)} for k, v in profile.items()]),
                 hide_index=True, width="stretch")

p = float(bn.predict_proba(pd.DataFrame([ev]) if ev else pd.DataFrame(index=[0]))[0])
score = float(to_score(p))
fs = fico_score(profile)
px = xgb_proba(models["xgb"], profile)

tabs = st.tabs(["Kết quả", "Đồ thị nhân quả", "Suy luận ngược", "What-if biến cố", "Lời khuyên (LLM)", "Tri thức & CPT"])

# ----------------------------------------------------------------------------- 1. kết quả
with tabs[0]:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Điểm {model_name}", f"{score:.0f}", help="Thang 300–850; neo p=50% → 400, p=0,5% → 800 (PDO ≈ 52)")
    m2.metric("Mức rủi ro", risk_band(score))
    m3.metric("Xác suất vỡ nợ", f"{100 * p:.1f}%")
    m4.metric("Số trường không rõ", f"{sum(v is None for k, v in profile.items() if k in INPUTS)}/{len(INPUTS)}")
    st.markdown("**So sánh với mô hình khác**")
    comp = [{"Mô hình": model_name, "Điểm": round(score), "P(vỡ nợ)": f"{100 * p:.1f}%",
             "Ghi chú": "Mạng Bayes – suy luận xác suất, chịu được thiếu thông tin"},
            {"Mô hình": "FICO rule-based (đề tài cũ)", "Điểm": round(fs), "P(vỡ nợ)": "–",
             "Ghi chú": "Luật cố định 35/30/15/10/10; biến thiếu nhận điểm trung tính 0,5"}]
    if px is not None:
        comp.append({"Mô hình": "XGBoost (hộp đen)", "Điểm": round(float(to_score(px))), "P(vỡ nợ)": f"{100 * px:.1f}%",
                     "Ghi chú": "Cùng đầu vào rời rạc; không giải thích được bằng nhân quả, không suy luận ngược"})
    st.dataframe(pd.DataFrame(comp), hide_index=True, width="stretch")
    st.markdown("**Yếu tố tác động** (điểm so với một người có cùng các đặc điểm khác nhưng yếu tố này ở mức phổ biến)")
    contrib = contributions(bn, ev)
    if contrib:
        cdf = pd.DataFrame(contrib)
        cdf["Yếu tố"] = cdf["label"] + ": " + cdf["state"]
        import altair as alt

        chart = alt.Chart(cdf).mark_bar(cornerRadiusEnd=4, height=14).encode(
            x=alt.X("points:Q", title="Đóng góp (điểm)"), y=alt.Y("Yếu tố:N", sort="x", title=None),
            color=alt.condition("datum.points < 0", alt.value("#eb6834"), alt.value("#2a78d6")),
            tooltip=["Yếu tố", "points"]).properties(height=32 * len(cdf) + 20)
        st.altair_chart(chart, width="stretch")

# ----------------------------------------------------------------------------- 2. đồ thị
with tabs[1]:
    st.caption("Nút xanh = quan sát được (học từ dữ liệu); nút cam = tri thức chuyên gia (CPT từ World Bank/WHO/GSO + "
               "giả định). Viền đậm = đã có bằng chứng. Số trong nút = xác suất hậu nghiệm với hồ sơ hiện tại.")
    marg = bn.marginals(ev)
    cfg = load_config("bn_expert")
    lines = ["digraph G {", 'rankdir=LR; node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10];']
    for n, a in cfg["nodes"].items():
        dist = marg[n]
        if n == "default":
            txt = f"P(vỡ nợ) = {100 * dist[1]:.1f}%"
            color = "#f6c9b6"
        elif a["layer"] == "expert":
            k = int(np.argmax(dist)) if len(dist) > 2 else 1
            txt = f"P({state_vi(n, bn.states[n][k])}) = {100 * dist[k]:.1f}%"
            color = "#fde2b8"
        else:
            k = int(np.argmax(dist))
            txt = state_vi(n, bn.states[n][k]) + ("" if n in ev else f" ({100 * dist[k]:.0f}%)")
            color = "#cfe0f6"
        pen = "2.5" if n in ev else "0.8"
        lines.append(f'"{n}" [label="{a["label"]}\\n{txt}", fillcolor="{color}", penwidth={pen}];')
    for p_, c_, *_ in cfg["edges"]:
        lines.append(f'"{p_}" -> "{c_}";')
    lines.append("}")
    st.graphviz_chart("\n".join(lines), width="stretch")

# ----------------------------------------------------------------------------- 3. suy luận ngược
with tabs[2]:
    st.markdown("**Mục tiêu điểm tín dụng** – tìm thay đổi ít tốn kém nhất (can thiệp do() trên các yếu tố bạn điều chỉnh "
                "được). Chi phí mỗi bậc là *giả định* thể hiện độ khó (configs/backward.yaml).")
    tgt = st.slider("Điểm mục tiêu", 400, 800, int(min(800, max(400, round(score / 10) * 10 + 40))), step=10)
    cf = counterfactual_search(bn, ev, target_score=tgt)
    if cf["already_met"]:
        st.success(f"Hồ sơ đã đạt {tgt} điểm (hiện {score:.0f}).")
    elif cf["plans"]:
        st.dataframe(pd.DataFrame([{"Phương án": " + ".join(pl.describe()), "Điểm đạt được": round(pl.score),
                                    "Chi phí (giả định)": pl.cost} for pl in cf["plans"]]),
                     hide_index=True, width="stretch")
    else:
        b_ = cf["best_possible"]
        st.warning(f"Không đạt được {tgt} điểm chỉ bằng các thay đổi trong tầm tay; tối đa ≈ {b_.score:.0f} điểm với: "
                   + "; ".join(b_.describe()))
    st.caption(f"Đã đánh giá {cf['n_evaluated']:,} tổ hợp thay đổi bằng suy luận chính xác.")
    st.divider()
    st.markdown("**Điều kiện cần (Bayes ngược)** – trong những người giống bạn, những người đạt mục tiêu thường có:")
    goal_name = st.radio("Mục tiêu", ["Không vỡ nợ", "Sở hữu nhà", "Sở hữu cả nhà và xe"], horizontal=True)
    goal = {"Không vỡ nợ": {"default": "0"}, "Sở hữu nhà": {"assets": "realty"},
            "Sở hữu cả nhà và xe": {"assets": "both"}}[goal_name]
    levers = ["income", "annuity_to_income", "credit_to_income", "living_cost", "ext_score_mean", "years_employed"]
    bp = backward_posterior(bn, ev, goal, levers=levers)
    for lv, df in bp.items():
        df = df.copy()
        df["state"] = df["state"].map(lambda s: state_vi(lv, s))
        df.columns = ["Mức", "P(mức | hồ sơ)", "P(mức | hồ sơ, đạt mục tiêu)", "Hệ số nâng (lift)"]
        with st.expander(node_vi()[lv]):
            st.dataframe(df, hide_index=True, width="stretch")

# ----------------------------------------------------------------------------- 4. what-if
with tabs[3]:
    st.markdown("Bật biến cố để xem điểm thay đổi thế nào (nút tri thức: Mất việc, Sức khỏe, Lạm phát, Chu kỳ kinh tế, "
                "Chi phí sinh hoạt → Hụt dòng tiền → Vỡ nợ).")
    w = {}
    c1, c2, c3 = st.columns(3)
    not_working = profile.get("years_employed") == "not_working"
    if c1.checkbox("Mất việc", disabled=not_working,
                   help="Không áp dụng cho người không đi làm (bằng chứng bất khả)" if not_working else None):
        w["job_loss"] = "yes"
    if c1.checkbox("Biến cố sức khỏe (chi y tế > 10% chi tiêu hộ)"):
        w["health_shock"] = "yes"
    infl = c2.selectbox("Lạm phát", [UNK, "low", "moderate", "high"], format_func=lambda s: s if s == UNK else state_vi("inflation", s))
    if infl != UNK:
        w["inflation"] = infl
    if c2.checkbox("Kinh tế suy giảm (tăng trưởng GDP < 5%)"):
        w["econ_cycle"] = "downturn"
    lc = c3.selectbox("Chi phí sinh hoạt", [UNK, "low", "normal", "high"], format_func=lambda s: s if s == UNK else state_vi("living_cost", s))
    if lc != UNK:
        w["living_cost"] = lc
    p2 = float(bn.predict_proba(pd.DataFrame([{**ev, **w}]))[0])
    s2 = float(to_score(p2))
    a, b2 = st.columns(2)
    a.metric("Điểm khi có biến cố", f"{s2:.0f}", f"{s2 - score:+.0f}")
    b2.metric("Xác suất vỡ nợ", f"{100 * p2:.1f}%", f"{100 * (p2 - p):+.1f} điểm %", delta_color="inverse")
    m2_ = bn.marginals({**ev, **w})
    st.caption(f"P(hụt dòng tiền) = {100 * m2_['cashflow_shock'][1]:.1f}% · P(mất việc) = {100 * m2_['job_loss'][1]:.1f}% · "
               f"λ = {bn.meta.get('lambda')} (giả định, xem phân tích độ nhạy trong báo cáo).")

# ----------------------------------------------------------------------------- 5. LLM
with tabs[4]:
    st.markdown("LLM **chỉ diễn đạt** các dữ kiện do Mạng Bayes tính (điểm, đóng góp, what-if, kế hoạch) – không tự tính xác "
                "suất. Mỗi lời khuyên được kiểm tra tự động: mọi con số phải có trong dữ kiện.")
    if st.button("Tạo lời khuyên", type="primary"):
        with st.spinner("Đang tính dữ kiện và gọi LLM…"):
            others = {"FICO": fs} | ({"XGBoost": float(to_score(px))} if px is not None else {})
            facts = build_facts(bn, ev, others=others)
            adv = LLMClient(provider).advise(facts)
            chk = check(adv.text, facts)
        if adv.error:
            st.warning(f"{adv.error} – dùng lời khuyên mẫu (template).")
        st.markdown(adv.text)
        ok = "✅ Trung thành với dữ kiện" if chk["faithful"] else "⚠️ Có điểm chưa khớp dữ kiện"
        st.caption(f"{ok} · nguồn: {adv.provider} ({adv.model}){' · cache' if adv.cached else ''} · "
                   f"số khớp {chk['number_precision']:.0%}, bao phủ {chk['fact_coverage']:.0%}"
                   + (f" · số không có trong dữ kiện: {chk['unsupported_numbers']}" if chk["unsupported_numbers"] else ""))
        with st.expander("Dữ kiện gửi cho LLM (JSON)"):
            st.json(facts)

# ----------------------------------------------------------------------------- 6. tri thức
with tabs[5]:
    cfg = load_config("bn_expert")
    node = st.selectbox("Nút", list(cfg["nodes"]), format_func=lambda n: f"{node_vi()[n]} ({n})")
    a = cfg["nodes"][node]
    st.markdown(f"**Lớp:** {'tri thức chuyên gia' if a['layer'] == 'expert' else 'dữ liệu'} · **Cha:** "
                f"{', '.join(node_vi()[x] for x in bn.parents[node]) or '(không)'}")
    if a.get("cpt_source"):
        st.info("Nguồn CPT: " + a["cpt_source"])
    cpt = bn.cpts[node]
    ps = bn.parents[node]
    if cpt.size <= 2000:
        idx = pd.MultiIndex.from_product([[state_vi(x, s) for s in bn.states[x]] for x in ps],
                                         names=[node_vi()[x] for x in ps]) if ps else None
        df = pd.DataFrame(cpt.reshape(-1, bn.card(node)), columns=[state_vi(node, s) for s in bn.states[node]], index=idx)
        st.dataframe(df.round(4), width="stretch")
    else:
        st.caption(f"CPT có {cpt.size:,} ô – quá lớn để hiển thị; xem lát cắt theo hồ sơ ở tab Kết quả.")
    st.markdown("**Cạnh và lý do (đã được nhóm duyệt)**")
    st.dataframe(pd.DataFrame([{"Từ": node_vi()[e[0]], "Đến": node_vi()[e[1]], "Lý do": e[2], "Bằng chứng": e[3]}
                               for e in cfg["edges"]]), hide_index=True, width="stretch")
    st.markdown("**Khác biệt so với đề tài FICO rule-based cũ**")
    st.markdown("""| | FICO rule-based (cũ) | Mạng Bayes (đồ án này) |
|---|---|---|
| Tri thức | Trọng số cố định 35/30/15/10/10 | Đồ thị nhân quả + CPT học từ dữ liệu & tri thức vĩ mô |
| Đầu ra | Điểm tất định | Xác suất vỡ nợ → điểm, có độ bất định |
| Thiếu thông tin | Gán điểm trung tính | Lấy biên chính xác theo xác suất |
| Biến cố (mất việc, sức khỏe) | Không mô hình hóa | Nút tri thức, what-if |
| Suy luận ngược | Không | Bayes ngược + phản thực do() |
| Ngành nghề | Không dùng | Ngành → Nghề → Thu nhập → Ổn định việc làm |""")

"""Suy luận ngược trên BN: từ mục tiêu (điểm tín dụng / tài sản) -> điều kiện cần về thu nhập & chi tiêu.

Ba công cụ:
1. `backward_posterior`: P(đòn bẩy | mục tiêu đạt, hồ sơ) – "người giống bạn mà KHÔNG vỡ nợ thường có …".
2. `map_conditions`: MAP query (pgmpy) – tổ hợp đòn bẩy khả dĩ nhất khi mục tiêu đạt.
3. `counterfactual_search`: tìm thay đổi ít tốn kém nhất trên đòn bẩy (do-intervention) để
   P(vỡ nợ) ≤ ngưỡng tương ứng điểm mục tiêu. Duyệt lưới đầy đủ (≤ vài nghìn tổ hợp, suy luận theo lô).
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.bn.core import DiscreteBN
from src.bn.model import score_to_p, to_score
from src.common import load_config


def _levers() -> dict:
    return load_config("backward")["levers"]


def intervene(bn: DiscreteBN, nodes: list[str]) -> DiscreteBN:
    """Graph surgery: cắt mọi cạnh vào `nodes`, đặt CPT đều. Quan sát nút gốc này ≡ do(nút = giá trị)."""
    parents = {n: ([] if n in nodes else list(ps)) for n, ps in bn.parents.items()}
    cpts = dict(bn.cpts)
    for n in nodes:
        cpts[n] = np.full(bn.card(n), 1.0 / bn.card(n))
    return DiscreteBN(bn.states, parents, cpts, dict(bn.meta))


def _ordered(bn: DiscreteBN, lever: str) -> list[str]:
    return _levers()[lever].get("ordered_states", bn.states[lever])


def _options(bn: DiscreteBN, lever: str, current: str | None) -> list[tuple[str | None, int]]:
    """Các lựa chọn (trạng thái mới, số bậc) cho một đòn bẩy, kể cả 'giữ nguyên' (None, 0)."""
    spec = _levers()[lever]
    order = _ordered(bn, lever)
    opts: list[tuple[str | None, int]] = [(None, 0)]
    if current not in order:  # chưa biết giá trị hiện tại -> chỉ đề xuất mức đích, tính 1 bậc
        return opts + [(s, 1) for s in order]
    i = order.index(current)
    step = 1 if spec["direction"] == "up" else -1
    for k in range(1, spec["max_steps"] + 1):
        j = i + step * k
        if 0 <= j < len(order):
            opts.append((order[j], k))
    return opts


@dataclass
class Plan:
    changes: dict[str, tuple[str | None, str]]  # lever -> (từ, sang)
    cost: float
    p_default: float
    score: float

    def describe(self) -> list[str]:
        from src.app.labels import state_vi

        lv = _levers()
        return [f"{lv[k]['label']}: {state_vi(k, a)} → {state_vi(k, b)}" for k, (a, b) in self.changes.items()]


def counterfactual_search(bn: DiscreteBN, profile: dict[str, str], target_score: float | None = None,
                          target_p: float | None = None, levers: list[str] | None = None,
                          top_k: int | None = None) -> dict:
    """Tìm các kế hoạch thay đổi đòn bẩy rẻ nhất để đạt điểm mục tiêu.

    Trả về: baseline (p, điểm), danh sách kế hoạch đạt mục tiêu (sắp theo chi phí rồi p),
    và kế hoạch tốt nhất có thể nếu không có kế hoạch nào đạt.
    """
    if target_p is None:
        target_p = score_to_p(target_score)
    levers = levers or list(_levers())
    top_k = top_k or load_config("backward")["top_k"]
    base_ev = pd.DataFrame([{k: v for k, v in profile.items() if k != "default"}])
    p0 = float(bn.predict_proba(base_ev)[0])

    option_lists = [_options(bn, l, profile.get(l)) for l in levers]
    combos = list(itertools.product(*option_lists))
    lv = _levers()
    # gom theo tập đòn bẩy bị can thiệp -> mỗi nhóm 1 mạng đã cắt cạnh, suy luận theo lô
    groups: dict[tuple[str, ...], list[int]] = {}
    for i, c in enumerate(combos):
        key = tuple(l for l, (s, _) in zip(levers, c) if s is not None)
        groups.setdefault(key, []).append(i)
    probs = np.empty(len(combos))
    for key, idxs in groups.items():
        net = intervene(bn, list(key)) if key else bn
        rows = []
        for i in idxs:
            ev = {k: v for k, v in profile.items() if k != "default"}
            for l, (s, _) in zip(levers, combos[i]):
                if s is not None:
                    ev[l] = s
            rows.append(ev)
        probs[idxs] = net.predict_proba(pd.DataFrame(rows))
    costs = np.array([sum(lv[l]["cost"] * k for l, (_, k) in zip(levers, c)) for c in combos])

    def plan(i: int) -> Plan:
        ch = {l: (profile.get(l), s) for l, (s, _) in zip(levers, combos[i]) if s is not None}
        return Plan(ch, float(costs[i]), float(probs[i]), float(to_score(probs[i])))

    ok = np.flatnonzero(probs <= target_p)
    ok = ok[np.lexsort((probs[ok], costs[ok]))]
    # bỏ kế hoạch bị trội (chi phí ≥ và p ≥ một kế hoạch rẻ hơn đã chọn)
    chosen: list[int] = []
    for i in ok:
        if not any(costs[j] <= costs[i] and probs[j] <= probs[i] and j != i for j in chosen):
            chosen.append(i)
        if len(chosen) >= top_k:
            break
    best = int(np.argmin(probs))
    return {
        "baseline": {"p_default": p0, "score": float(to_score(p0))},
        "target": {"p_default": target_p, "score": float(to_score(target_p))},
        "already_met": p0 <= target_p,
        "plans": [plan(i) for i in chosen],
        "best_possible": plan(best),
        "n_evaluated": len(combos),
    }


def backward_posterior(bn: DiscreteBN, profile: dict[str, str], goal: dict[str, str],
                       levers: list[str] | None = None) -> dict[str, pd.DataFrame]:
    """So sánh P(đòn bẩy | hồ sơ) với P(đòn bẩy | hồ sơ, mục tiêu đạt) – Bayes ngược chiều nhân quả.

    `goal` ví dụ {"default": "0"} (không vỡ nợ) hoặc {"assets": "both"} (có nhà và xe).
    Không đưa đòn bẩy của chính hồ sơ vào bằng chứng (để xem 'cần' ở mức nào).
    """
    levers = levers or list(_levers())
    base = {k: v for k, v in profile.items() if k not in levers and k not in goal}
    res = {}
    for l in levers:
        prior = bn.query(pd.DataFrame([base]), l)[0]
        post = bn.query(pd.DataFrame([{**base, **goal}]), l)[0]
        res[l] = pd.DataFrame({"state": bn.states[l], "P(·|hồ sơ)": prior.round(4),
                               "P(·|hồ sơ, mục tiêu)": post.round(4), "lift": (post / prior).round(3)})
    return res


def map_conditions(bn: DiscreteBN, profile: dict[str, str], goal: dict[str, str],
                   levers: list[str] | None = None) -> dict[str, str]:
    """MAP query: argmax_{đòn bẩy} P(đòn bẩy | hồ sơ, mục tiêu) (pgmpy VariableElimination)."""
    from pgmpy.inference import VariableElimination

    levers = levers or list(_levers())
    ev = {k: v for k, v in profile.items() if k not in levers and k not in goal and v is not None}
    ev.update(goal)
    return VariableElimination(bn.to_pgmpy()).map_query(variables=levers, evidence=ev, show_progress=False)

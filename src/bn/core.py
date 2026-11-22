"""Mạng Bayes rời rạc gọn nhẹ: học CPT (BDeu), suy luận CHÍNH XÁC theo lô bằng numpy.einsum.

Vì sao tự cài: thí nghiệm cần hàng trăm nghìn truy vấn với bằng chứng thiếu tùy ý; VariableElimination
của pgmpy chạy từng dòng sẽ quá chậm. Kết quả được kiểm chứng khớp với pgmpy (tests/test_bn.py).
pgmpy vẫn dùng cho MAP query và học cấu trúc (`to_pgmpy`).

Quy ước: `cpts[node]` có shape (*card(parents), card(node)), tổng theo trục cuối = 1.
Bằng chứng: DataFrame với giá trị trạng thái (chuỗi); NaN / cột vắng = không quan sát.
"""
from __future__ import annotations

import json
import string
from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

LETTERS = string.ascii_letters.replace("b", "")  # 'b' dành cho trục batch


@dataclass
class DiscreteBN:
    states: dict[str, list[str]]
    parents: dict[str, list[str]]
    cpts: dict[str, np.ndarray] = field(default_factory=dict)
    meta: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ cấu trúc
    @property
    def graph(self) -> nx.DiGraph:
        g = nx.DiGraph()
        g.add_nodes_from(self.states)
        g.add_edges_from((p, c) for c, ps in self.parents.items() for p in ps)
        return g

    @property
    def nodes(self) -> list[str]:
        return list(nx.topological_sort(self.graph))

    def card(self, n: str) -> int:
        return len(self.states[n])

    def validate(self) -> None:
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Có chu trình")
        for n in self.states:
            cpt = self.cpts[n]
            exp = tuple(self.card(p) for p in self.parents[n]) + (self.card(n),)
            if cpt.shape != exp:
                raise ValueError(f"{n}: shape {cpt.shape} != {exp}")
            if not np.allclose(cpt.sum(-1), 1.0, atol=1e-8) or (cpt < 0).any():
                raise ValueError(f"{n}: CPT không hợp lệ")

    # ------------------------------------------------------------------ học tham số
    def codes(self, s: pd.Series, n: str) -> np.ndarray:
        """Mã số trạng thái; -1 nếu thiếu/không thuộc tập trạng thái."""
        return pd.Categorical(s, categories=self.states[n]).codes.astype(np.int64)

    def counts(self, data: pd.DataFrame, n: str) -> np.ndarray:
        cols = self.parents[n] + [n]
        shape = tuple(self.card(c) for c in cols)
        codes = np.stack([self.codes(data[c], c) for c in cols])
        ok = (codes >= 0).all(0)
        flat = np.ravel_multi_index(codes[:, ok], shape)
        return np.bincount(flat, minlength=int(np.prod(shape))).reshape(shape).astype(float)

    def fit_node(self, data: pd.DataFrame, n: str, ess: float = 10.0, prior: str = "m_estimate") -> None:
        """Ước lượng tham số Bayes cho một nút.

        prior="m_estimate" (mặc định): θ_ijk = (N_ijk + m·P(k)) / (N_ij + m), P(k) = phân phối biên của nút
            (Cestnik 1990). Tổ hợp cha chưa gặp -> trả về phân phối biên thay vì phân phối đều.
        prior="bdeu": Dirichlet đều α = ess/(q·r) (BDeu chuẩn, dùng để đối chiếu với pgmpy).
        """
        N = self.counts(data, n)
        r = self.card(n)
        q = int(np.prod(N.shape[:-1])) if N.ndim > 1 else 1
        if prior == "bdeu":
            num = N + ess / (q * r)
        elif prior == "m_estimate":
            marg = N.reshape(-1, r).sum(0) + 0.5
            num = N + ess * marg / marg.sum()
        else:
            raise ValueError(prior)
        self.cpts[n] = num / num.sum(-1, keepdims=True)
        self.meta.setdefault("counts", {})[n] = N.sum(-1)  # N_ij để dùng cho ràng buộc đơn điệu

    def fit(self, data: pd.DataFrame, nodes: list[str] | None = None, ess: float = 10.0,
            prior: str = "m_estimate") -> "DiscreteBN":
        for n in nodes or list(self.states):
            self.fit_node(data, n, ess, prior)
        return self

    # ------------------------------------------------------------------ suy luận
    def _relevant(self, observed: set[str], target: str) -> list[str]:
        """Bỏ nút 'cằn' (không quan sát, không có hậu duệ được quan sát, không phải đích) – tổng CPT = 1."""
        g = self.graph
        keep = set()
        for n in observed | {target}:
            keep |= {n} | nx.ancestors(g, n)
        return [n for n in self.nodes if n in keep]

    def _query_pattern(self, codes: dict[str, np.ndarray], observed: frozenset[str], target: str) -> np.ndarray:
        """Suy luận cho một nhóm dòng có CÙNG tập biến quan sát.

        Biến quan sát: lấy lát CPT theo từng dòng (gather) -> nhân tử có trục batch.
        Biến ẩn: cộng dồn bằng einsum (thường chỉ vài biến -> rẻ).
        """
        nodes = self._relevant(set(observed), target)
        hidden = [n for n in nodes if n not in observed]
        idx = {n: LETTERS[i] for i, n in enumerate(hidden)}
        b = len(next(iter(codes.values()))) if codes else 1
        ops, subs = [], []
        for n in nodes:
            vars_ = self.parents[n] + [n]
            obs_axes = [i for i, v in enumerate(vars_) if v in observed]
            hid_axes = [i for i, v in enumerate(vars_) if v not in observed]
            cpt = self.cpts[n]
            if obs_axes:
                cpt = np.transpose(cpt, obs_axes + hid_axes)[tuple(codes[vars_[i]] for i in obs_axes)]
                subs.append("b" + "".join(idx[vars_[i]] for i in hid_axes))
            else:
                subs.append("".join(idx[vars_[i]] for i in hid_axes))
            ops.append(cpt)
        ops.append(np.ones(b))
        subs.append("b")
        expr = ",".join(subs) + "->b" + idx[target]
        path = np.einsum_path(expr, *ops, optimize="greedy")[0]
        joint = np.einsum(expr, *ops, optimize=path)
        z = joint.sum(1, keepdims=True)
        # bằng chứng bất khả (P(e)=0, vd. 'mất việc' khi không đi làm) -> NaN tường minh
        return np.divide(joint, z, out=np.full_like(joint, np.nan), where=z > 0)

    def query(self, evidence: pd.DataFrame, target: str = "default", chunk: int = 50000) -> np.ndarray:
        """P(target | bằng chứng) cho từng dòng -> mảng (n, card(target)). Dòng được gom theo mẫu thiếu."""
        n_rows = len(evidence)
        out = np.zeros((n_rows, self.card(target)))
        cols = [n for n in self.states if n != target and n in evidence]
        all_codes = {n: self.codes(evidence[n], n) for n in cols}
        mask = np.stack([all_codes[n] >= 0 for n in cols], 1) if cols else np.zeros((n_rows, 0), bool)
        patterns, inv = np.unique(mask, axis=0, return_inverse=True)
        inv = np.asarray(inv).ravel()
        for k, pat in enumerate(patterns):
            rows = np.flatnonzero(inv == k)
            observed = frozenset(n for n, o in zip(cols, pat) if o)
            for s in range(0, len(rows), chunk):
                r = rows[s:s + chunk]
                codes = {n: all_codes[n][r] for n in observed}
                if not codes:
                    out[r] = self._query_pattern({}, observed, target)[0]
                else:
                    out[r] = self._query_pattern(codes, observed, target)
        return out

    def predict_proba(self, evidence: pd.DataFrame, target: str = "default", positive: str = "1") -> np.ndarray:
        return self.query(evidence, target)[:, self.states[target].index(positive)]

    def marginals(self, evidence: dict[str, str] | None = None) -> dict[str, np.ndarray]:
        """Phân phối hậu nghiệm của MỌI nút cho một hồ sơ (dùng cho demo / tô màu đồ thị)."""
        ev = pd.DataFrame([evidence or {}])
        res = {}
        for n in self.states:
            if evidence and n in evidence and evidence[n] is not None:
                v = np.zeros(self.card(n))
                v[self.states[n].index(evidence[n])] = 1.0
                res[n] = v
            else:
                res[n] = self.query(ev, n)[0]
        return res

    # ------------------------------------------------------------------ chuyển đổi / lưu
    def to_pgmpy(self):
        from pgmpy.factors.discrete import TabularCPD
        from pgmpy.models import DiscreteBayesianNetwork

        m = DiscreteBayesianNetwork([(p, c) for c, ps in self.parents.items() for p in ps])
        m.add_nodes_from(self.states)
        for n in self.states:
            ps = self.parents[n]
            cpt = self.cpts[n]
            vals = cpt.reshape(-1, self.card(n)).T  # cột: tổ hợp cha theo thứ tự C (cha đầu thay đổi chậm nhất)
            m.add_cpds(TabularCPD(n, self.card(n), vals, evidence=ps or None,
                                  evidence_card=[self.card(p) for p in ps] or None,
                                  state_names={v: self.states[v] for v in [n, *ps]}))
        m.check_model()
        return m

    def to_json(self, f: Path) -> None:
        f.parent.mkdir(parents=True, exist_ok=True)
        data = {"states": self.states, "parents": self.parents,
                "cpts": {n: np.round(c, 8).tolist() for n, c in self.cpts.items()},
                "meta": {k: v for k, v in self.meta.items() if k != "counts"}}
        f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def from_json(cls, f: Path) -> "DiscreteBN":
        d = json.loads(f.read_text(encoding="utf-8"))
        bn = cls(d["states"], d["parents"], {n: np.array(c) for n, c in d["cpts"].items()}, d.get("meta", {}))
        for n, c in bn.cpts.items():  # chuẩn hóa lại sau khi làm tròn
            bn.cpts[n] = c / c.sum(-1, keepdims=True)
        return bn

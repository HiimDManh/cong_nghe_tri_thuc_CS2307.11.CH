"""LLMClient: Gemini / Groq / Ollama qua REST (không cần SDK), cache theo hash prompt, dự phòng template.

Key chỉ đọc từ biến môi trường hoặc `.env` / `st.secrets` (không bao giờ ghi ra log, cache hay repo).
Gemini nhận key qua header `x-goog-api-key` (không đặt trong URL để tránh lộ trong log).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass

import requests

from src.common import load_config, path
from src.llm.prompt import SYSTEM, template_advice, user_prompt


@dataclass
class Advice:
    text: str
    provider: str
    model: str
    latency_s: float
    cached: bool = False
    error: str | None = None


def _env(name: str) -> str | None:
    try:
        from dotenv import load_dotenv

        load_dotenv(path(".env"))
    except ImportError:
        pass
    v = os.environ.get(name)
    if not v:
        try:
            import streamlit as st

            v = st.secrets.get(name)  # Streamlit Cloud: Settings › Secrets
        except Exception:
            v = None
    return v or None


def available_providers() -> list[str]:
    out = []
    if _env("GEMINI_API_KEY"):
        out.append("gemini")
    if _env("GROQ_API_KEY"):
        out.append("groq")
    if _env("OLLAMA_HOST"):
        out.append("ollama")
    return out + ["template"]


class LLMClient:
    def __init__(self, provider: str | None = None) -> None:
        self.cfg = load_config("llm")
        avail = available_providers()
        want = provider or _env("LLM_PROVIDER") or avail[0]
        self.provider = want if want in avail else "template"
        self.model = self.cfg["providers"].get(self.provider, {}).get("model", "template")

    # ------------------------------------------------------------------ cache
    def _cache_file(self, system: str, user: str):
        h = hashlib.sha256(json.dumps([self.provider, self.model, self.cfg["temperature"], system, user],
                                      ensure_ascii=False).encode()).hexdigest()[:24]
        d = path(self.cfg["cache_dir"])
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{h}.json"

    # ------------------------------------------------------------------ gọi API
    def _call(self, system: str, user: str) -> str:
        c, p = self.cfg, self.cfg["providers"][self.provider]
        if self.provider == "gemini":
            r = requests.post(p["url"].format(model=self.model), timeout=c["timeout_s"],
                              headers={"x-goog-api-key": _env("GEMINI_API_KEY"), "Content-Type": "application/json"},
                              json={"systemInstruction": {"parts": [{"text": system}]},
                                    "contents": [{"role": "user", "parts": [{"text": user}]}],
                                    "generationConfig": {"temperature": c["temperature"],
                                                         "maxOutputTokens": c["max_tokens"]}})
            r.raise_for_status()
            parts = r.json()["candidates"][0]["content"]["parts"]
            return "".join(x.get("text", "") for x in parts).strip()
        if self.provider == "groq":
            r = requests.post(p["url"], timeout=c["timeout_s"],
                              headers={"Authorization": f"Bearer {_env('GROQ_API_KEY')}"},
                              json={"model": self.model, "temperature": c["temperature"], "max_tokens": c["max_tokens"],
                                    "messages": [{"role": "system", "content": system},
                                                 {"role": "user", "content": user}]})
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        if self.provider == "ollama":
            r = requests.post(p["url"].format(host=_env("OLLAMA_HOST").rstrip("/")), timeout=c["timeout_s"] * 3,
                              json={"model": self.model, "stream": False,
                                    "options": {"temperature": c["temperature"]},
                                    "messages": [{"role": "system", "content": system},
                                                 {"role": "user", "content": user}]})
            r.raise_for_status()
            return r.json()["message"]["content"].strip()
        raise ValueError(self.provider)

    def advise(self, facts: dict, use_cache: bool = True) -> Advice:
        """Lời khuyên cho dữ kiện BN. Lỗi mạng/quota -> trả lời khuyên template kèm thông báo lỗi."""
        if self.provider == "template":
            return Advice(template_advice(facts), "template", "template", 0.0)
        user = user_prompt(facts)
        f = self._cache_file(SYSTEM, user)
        if use_cache and f.exists():
            d = json.loads(f.read_text(encoding="utf-8"))
            return Advice(d["text"], self.provider, self.model, d["latency_s"], cached=True)
        t = time.time()
        try:
            text = self._call(SYSTEM, user)
        except Exception as e:  # không để lộ key: chỉ giữ loại lỗi + mã HTTP
            code = getattr(getattr(e, "response", None), "status_code", "")
            return Advice(template_advice(facts), "template", "template", 0.0,
                          error=f"{self.provider} lỗi {type(e).__name__} {code}".strip())
        lat = time.time() - t
        f.write_text(json.dumps({"text": text, "latency_s": lat}, ensure_ascii=False), encoding="utf-8")
        return Advice(text, self.provider, self.model, lat)

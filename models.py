import time
import asyncio
import os
from dataclasses import dataclass

import anthropic
import google.generativeai as genai
from groq import Groq


# ---------------------------------------------------------------------------
# Konfigurasi model & harga
# ---------------------------------------------------------------------------
PRICING = {
    "claude": {
        "model": "claude-haiku-4-5-20251001",
        "label": "Claude Haiku",
        "input_per_1k": 0.00025,
        "output_per_1k": 0.00125,
        "color": "#D97706",
    },
    "gemini": {
        "model": "gemini-2.5-flash",
        "label": "Gemini 2.5 Flash",
        "input_per_1k": 0.0,   # gratis di free tier
        "output_per_1k": 0.0,
        "color": "#2563EB",
    },
    "groq": {
        "model": "llama-3.1-8b-instant",
        "label": "LLaMA 3.1 (Groq)",
        "input_per_1k": 0.0,   # gratis di free tier
        "output_per_1k": 0.0,
        "color": "#7C3AED",
    },
}


@dataclass
class ModelResult:
    label: str
    model_id: str
    output: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    color: str
    error: str = ""


def _calc_cost(pricing: dict, input_tokens: int, output_tokens: int) -> float:
    cost = (input_tokens / 1000) * pricing["input_per_1k"]
    cost += (output_tokens / 1000) * pricing["output_per_1k"]
    return round(cost, 6)


# ---------------------------------------------------------------------------
# Claude (Anthropic)
# ---------------------------------------------------------------------------
def call_claude(prompt: str, max_tokens: int = 1024) -> ModelResult:
    p = PRICING["claude"]
    try:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        t0 = time.perf_counter()
        response = client.messages.create(
            model=p["model"],
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        latency = (time.perf_counter() - t0) * 1000
        in_tok = response.usage.input_tokens
        out_tok = response.usage.output_tokens
        return ModelResult(
            label=p["label"],
            model_id=p["model"],
            output=response.content[0].text,
            latency_ms=round(latency, 1),
            input_tokens=in_tok,
            output_tokens=out_tok,
            cost_usd=_calc_cost(p, in_tok, out_tok),
            color=p["color"],
        )
    except Exception as e:
        return ModelResult(
            label=p["label"], model_id=p["model"],
            output="", latency_ms=0, input_tokens=0, output_tokens=0,
            cost_usd=0, color=p["color"], error=str(e),
        )


# ---------------------------------------------------------------------------
# Gemini Flash (Google)
# ---------------------------------------------------------------------------
def call_gemini(prompt: str, max_tokens: int = 1024) -> ModelResult:
    p = PRICING["gemini"]
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            p["model"],
            generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens),
        )
        t0 = time.perf_counter()
        response = model.generate_content(prompt)
        latency = (time.perf_counter() - t0) * 1000
        in_tok = response.usage_metadata.prompt_token_count or 0
        out_tok = response.usage_metadata.candidates_token_count or 0
        return ModelResult(
            label=p["label"],
            model_id=p["model"],
            output=response.text,
            latency_ms=round(latency, 1),
            input_tokens=in_tok,
            output_tokens=out_tok,
            cost_usd=_calc_cost(p, in_tok, out_tok),
            color=p["color"],
        )
    except Exception as e:
        return ModelResult(
            label=p["label"], model_id=p["model"],
            output="", latency_ms=0, input_tokens=0, output_tokens=0,
            cost_usd=0, color=p["color"], error=str(e),
        )


# ---------------------------------------------------------------------------
# LLaMA 3 via Groq
# ---------------------------------------------------------------------------
def call_groq(prompt: str, max_tokens: int = 1024) -> ModelResult:
    p = PRICING["groq"]
    try:
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        t0 = time.perf_counter()
        response = client.chat.completions.create(
            model=p["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        latency = (time.perf_counter() - t0) * 1000
        in_tok = response.usage.prompt_tokens
        out_tok = response.usage.completion_tokens
        return ModelResult(
            label=p["label"],
            model_id=p["model"],
            output=response.choices[0].message.content,
            latency_ms=round(latency, 1),
            input_tokens=in_tok,
            output_tokens=out_tok,
            cost_usd=_calc_cost(p, in_tok, out_tok),
            color=p["color"],
        )
    except Exception as e:
        return ModelResult(
            label=p["label"], model_id=p["model"],
            output="", latency_ms=0, input_tokens=0, output_tokens=0,
            cost_usd=0, color=p["color"], error=str(e),
        )


# ---------------------------------------------------------------------------
# Dispatcher 
# ---------------------------------------------------------------------------
def run_all(prompt: str, max_tokens: int = 1024) -> list[ModelResult]:
    import concurrent.futures
    callers = [call_claude, call_gemini, call_groq]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fn, prompt, max_tokens) for fn in callers]
        results = [f.result() for f in futures]
    return results
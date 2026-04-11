"""
Utility: Generate a new JSON file with Vietnamese translations for fields marked with [VI]

Reads tarot-cards.json and writes tarot-cards.vi.json. For any string value that appears to be
placeholder English with a leading [VI], it will ask the local Ollama model to translate into Vietnamese.

Safe behavior:
- Skips fields that already look Vietnamese (do not start with "[VI]")
- Retries on transient errors

Usage (from backend/):
  python generate_vi_json.py

Environment:
  Uses OLLAMA_URL and OLLAMA_MODEL from app.core.config.settings
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, List

import httpx

try:
    # Allow running both as module and script
    from app.core.config import settings
except Exception:
    # Fallback defaults
    class _Settings:
        OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
        OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
        OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "180"))

    settings = _Settings()  # type: ignore

SOURCE_FILE = os.path.join(os.path.dirname(__file__), "tarot-cards.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "tarot-cards.vi.json")


def needs_translation(value: Any) -> bool:
    if isinstance(value, str):
        v = value.strip()
        return v.startswith("[VI]")
    return False


def strip_marker(value: str) -> str:
    # Remove leading [VI] marker if present
    v = value.strip()
    if v.startswith("[VI]"):
        return v[len("[VI]") :].strip()
    return v


async def translate_text(client: httpx.AsyncClient, text: str) -> str:
    # Build a concise translation prompt
    prompt = (
        "Bạn là dịch giả. Hãy dịch sang TIẾNG VIỆT, giữ nguyên cấu trúc và dấu chấm phẩy khi có.\n"
        "YÊU CẦU: Chỉ trả về BẢN DỊCH thuần túy, KHÔNG thêm lời dẫn.\n\n"
        f"Văn bản:\n{text}\n\nBản dịch tiếng Việt:"
    )
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 512,
            "top_k": 40,
            "top_p": 0.9,
            "temperature": 0.7,
            "num_ctx": 2048,
            "keep_alive": "3m",
        },
    }
    for attempt in range(1, 4):
        try:
            res = await client.post(f"{settings.OLLAMA_URL}/api/generate", json=payload)
            res.raise_for_status()
            data = res.json()
            out = data.get("response", "").strip()
            if out:
                return out
        except Exception as e:  # noqa: BLE001
            if attempt == 3:
                # Fallback: return stripped original without marker
                return strip_marker(text)
            await asyncio.sleep(0.5 * attempt)
    return strip_marker(text)


async def process_card(client: httpx.AsyncClient, card: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(card)

    # Fields that are strings
    string_fields = [
        "meaning_upright_vi",
        "meaning_reversed_vi",
        "name_vi",
    ]
    for field in string_fields:
        val = updated.get(field)
        if isinstance(val, str) and needs_translation(val):
            updated[field] = await translate_text(client, strip_marker(val))

    # Array fields of strings
    array_fields = [
        "keywords_vi",
        "meanings_light",  # may be EN already; do not touch unless marked
        "meanings_shadow",
        "fortune_telling",
        "questions_to_ask",
    ]
    for field in array_fields:
        val = updated.get(field)
        if isinstance(val, list):
            new_items: List[str] = []
            for item in val:
                if isinstance(item, str) and needs_translation(item):
                    new_items.append(await translate_text(client, strip_marker(item)))
                else:
                    new_items.append(item)
            updated[field] = new_items

    return updated


async def main() -> None:
    if not os.path.exists(SOURCE_FILE):
        raise FileNotFoundError(f"Source file not found: {SOURCE_FILE}")

    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected JSON array of tarot cards")

    timeout = httpx.Timeout(connect=10.0, read=settings.OLLAMA_TIMEOUT, write=10.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        out: List[Dict[str, Any]] = []
        for idx, card in enumerate(data, start=1):
            updated = await process_card(client, card)
            out.append(updated)
            if idx % 10 == 0:
                print(f"Processed {idx}/{len(data)} cards...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f" Wrote translated file: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())



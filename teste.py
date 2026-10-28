import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / "./.env/chave.env")

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise RuntimeError("Não encontrei OPENROUTER_API_KEY em chave.env")

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model": "openrouter/free",
    "stream": True,
    "messages": [
        {
            "role": "system",
            "content": (
                "Responda em português com recomendações práticas e uma justificativa breve. "
                "Não apresente raciocínio interno detalhado. "
                "Revise a ortografia e a gramática antes de responder. "
                "Use português brasileiro natural e explique siglas técnicas."
            ),
        },
        {
            "role": "user",
            "content": "Minha empresa está com gargalos na produção. O que devo fazer?",
        },
    ],
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    stream=True,
    timeout=60,
)

print("Status:", response.status_code)

if not response.ok:
    try:
        error_details = response.json()
    except ValueError:
        error_details = response.text
    print("Detalhes:", error_details)
else:
    print("Resposta: ", end="", flush=True)

    for raw_line in response.iter_lines():
        if not raw_line:
            continue

        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line.startswith("data:"):
            continue

        chunk_text = line[len("data:"):].strip()
        if chunk_text == "[DONE]":
            break

        try:
            chunk = json.loads(chunk_text)
        except json.JSONDecodeError:
            continue

        if "error" in chunk:
            print("\nErro:", chunk["error"])
            break

        choices = chunk.get("choices", [])
        if not choices:
            continue

        text_chunk = choices[0].get("delta", {}).get("content")
        if text_chunk:
            print(text_chunk, end="", flush=True)

    print()
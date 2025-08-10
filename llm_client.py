import yaml
import requests
import os
from dotenv import load_dotenv

load_dotenv()

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def call_openai(prompt):
    import openai
    client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content

def call_local_llm(prompt):
    url = os.getenv("LOCAL_LLM_URL") or config.get("local_api_url")
    if not url:
        raise RuntimeError("Local LLM URL not configured. Set LOCAL_LLM_URL or config.yaml local_api_url")
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "local-model",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        j = res.json()
        return j["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise RuntimeError(
            f"Local LLM unreachable at {url}. If you’re on a hosted environment, "
            f"'localhost' will not reach your machine. Use a reachable URL."
        ) from e

def call_llm(prompt, model=None):
    selected_model = (model or config.get("llm_provider", "openai")).lower()
    if selected_model == "openai":
        return call_openai(prompt)
    elif selected_model == "local":
        return call_local_llm(prompt)
    else:
        raise ValueError(f"Unknown model provider: {selected_model}")

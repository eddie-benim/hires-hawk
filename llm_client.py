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
    url = config["local_api_url"]
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "local-model",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    res = requests.post(url, json=payload, headers=headers)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

def call_llm(prompt, model=None):
        selected_model = model or config["llm_provider"]
    if selected_model == "openai":
        return call_openai(prompt)
    else:
        return call_local_llm(prompt)

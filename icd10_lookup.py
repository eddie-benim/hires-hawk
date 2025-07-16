import requests
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def lookup_icd10_api(disease):
    url = config["icd10_api_url"]
    # Try full disease name
    params = {"terms": disease, "maxList": 1}
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data and data[0] and data[1]:
            code = data[1][0]
            # Try to get description from extra fields or display fields if present
            desc = None
            if len(data) > 3 and data[3] and len(data[3]) > 0:
                desc = data[3][0][0] if isinstance(data[3][0], list) else data[3][0]
            return code, desc
    except Exception as e:
        print(f"ICD-10 API error (full name): {e}")
    # Try keywords (split disease name)
    for keyword in disease.split():
        params = {"terms": keyword, "maxList": 1}
        try:
            resp = requests.get(url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if data and data[0] and data[1]:
                code = data[1][0]
                desc = None
                if len(data) > 3 and data[3] and len(data[3]) > 0:
                    desc = data[3][0][0] if isinstance(data[3][0], list) else data[3][0]
                return code, desc
        except Exception as e:
            print(f"ICD-10 API error (keyword: {keyword}): {e}")
    return None, None

def get_icd10_code(disease, fallback_llm=None):
    code, desc = lookup_icd10_api(disease)
    if code:
        return code, desc
    if fallback_llm:
        # Ask LLM for code and description
        prompt = (
            f"What is the ICD-10 code and description for the disease: '{disease}'? "
            "Respond in the format: CODE | Description. If not found, reply: N/A | N/A."
        )
        try:
            llm_resp = fallback_llm(prompt)
            if '|' in llm_resp:
                code, desc = [x.strip() for x in llm_resp.split('|', 1)]
                if code and desc and code != 'N/A':
                    return code, desc
        except Exception as e:
            print(f"LLM ICD-10 fallback error: {e}")
    return None, None

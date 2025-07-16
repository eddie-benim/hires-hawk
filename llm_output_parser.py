import re
import ast
import json

def parse_disease_list(raw_llm_output):
    """
    Robustly parse the LLM output to extract a list of disease names.
    Handles code blocks, extra quotes, and common formatting issues.
    """
    cleaned = raw_llm_output.strip()
    # Remove code block markers
    cleaned = re.sub(r"^```[a-zA-Z]*", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned)
    cleaned = cleaned.strip()
    # Remove leading/trailing quotes
    cleaned = cleaned.strip('"\''"\n ")
    # Remove any 'python' or language tags
    cleaned = re.sub(r"^python", "", cleaned, flags=re.IGNORECASE).strip()
    # Try JSON
    try:
        diseases = json.loads(cleaned)
        if isinstance(diseases, list):
            return [str(d).strip('"\' ') for d in diseases]
    except Exception:
        pass
    # Try Python literal
    try:
        diseases = ast.literal_eval(cleaned)
        if isinstance(diseases, list):
            return [str(d).strip('"\' ') for d in diseases]
    except Exception:
        pass
    # Try comma-separated
    try:
        # Remove brackets if present
        cleaned = cleaned.strip('[]')
        diseases = [d.strip('"\' ') for d in cleaned.split(',') if d.strip()]
        if diseases:
            return diseases
    except Exception:
        pass
    # Fallback: return as single disease if not empty
    if cleaned:
        return [cleaned]
    return []

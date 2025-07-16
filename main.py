import streamlit as st
from llm_client import call_llm
from icd10_lookup import get_icd10_code

st.set_page_config(layout="wide")
st.title("HiRes Hawk: Highlighting Resident Reports")

st.markdown("Paste a radiology report below. The app will extract positive diseases and enumerate them with ICD-10 codes.")

report = st.text_area("Radiology Report", height=300)

if st.button("Analyze Report") and report.strip():
    # Placeholder LLM prompt for extracting diseases
    prompt = (
        "Extract all positive diseases mentioned in the following radiology report. "
        "List them as a Python list of disease names, no explanations.\n\n"
        f"{report}"
    )
    import ast, json
    raw_llm_output = call_llm(prompt)
    diseases = []
    try:
        # Try JSON
        diseases = json.loads(raw_llm_output)
        if not isinstance(diseases, list):
            raise ValueError
    except Exception:
        try:
            # Try Python literal (list)
            diseases = ast.literal_eval(raw_llm_output)
            if not isinstance(diseases, list):
                raise ValueError
        except Exception:
            try:
                # Try comma-separated string
                diseases = [d.strip() for d in raw_llm_output.split(',') if d.strip()]
                if len(diseases) < 1:
                    raise ValueError
            except Exception:
                st.error("Failed to parse LLM output. Please check your LLM configuration.")
                st.info(f"Raw LLM output: {raw_llm_output}")
                diseases = []

    results = []
    for idx, disease in enumerate(diseases, 1):
        code, desc = get_icd10_code(disease, fallback_llm=call_llm)
        results.append((idx, disease, code or "N/A", desc or "N/A"))

    col1, col2 = st.columns([2, 1])
    with col1:
        highlighted = report
        for idx, disease, _, _ in results:
            highlighted = highlighted.replace(disease, f"**[{idx}] {disease}**")
        st.markdown(highlighted)
    import pandas as pd
    with col2:
        st.markdown("### Positive Diseases")
        df = pd.DataFrame(
            [(disease, code, desc) for idx, disease, code, desc in results],
            columns=["Disease", "ICD-10", "Description"]
        )
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True)

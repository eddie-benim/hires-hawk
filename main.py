import streamlit as st
from llm_client import call_llm
from icd10_lookup import get_icd10_code

st.set_page_config(layout="wide")
st.title("HiRes Hawk: Highlighting Resident Reports")

st.markdown("Paste a radiology report below. The app will extract positive diseases and enumerate them with ICD-10 codes.")

report = st.text_area("Radiology Report", height=300)

if "history" not in st.session_state:
    st.session_state["history"] = []

if st.button("Analyze Report") and report.strip():
    prompt = (
        "Extract all positive diseases mentioned in the following radiology report. "
        "List them as a Python list of disease names, no explanations.\n\n"
        f"{report}"
    )
    from llm_output_parser import parse_disease_list
    raw_llm_output = call_llm(prompt)
    diseases = parse_disease_list(raw_llm_output)
    if not diseases:
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

st.markdown("## Prompt History")
for item in st.session_state["history"][::-1]:
    if item[0] == "Single":
        _, prompt, output = item
        with st.expander("Single Model Prompt"):
            st.code(prompt, language="markdown")
            st.text_area("LLM Output", value=output, height=150, disabled=True)
    elif item[0] == "Compare":
        _, prompt, out1, out2 = item
        with st.expander("Compared Models Prompt"):
            st.code(prompt, language="markdown")
            col1, col2 = st.columns(2)
            with col1:
                st.text_area("Primary Model Output", value=out1, height=150, disabled=True)
            with col2:
                st.text_area("Comparison Model Output", value=out2, height=150, disabled=True)

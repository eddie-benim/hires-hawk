import streamlit as st
from llm_client import call_llm
from icd10_lookup import get_icd10_code

st.set_page_config(layout="wide")
st.title("HiRes Hawk: Highlighting Resident Reports")

st.markdown("Paste a radiology report below. The app will extract positive diseases and enumerate them with ICD-10 codes.")

compare_mode = st.checkbox("Compare Two Models Side-by-Side")
if compare_mode:
    llm_model_1 = st.selectbox("Primary Model", ["openai", "local"], key="model_1")
    llm_model_2 = st.selectbox("Comparison Model", ["openai", "local"], key="model_2")
else:
    llm_model = st.selectbox("Choose LLM Provider", ["openai", "local"])
    st.markdown(f"<div style='background-color:#f0f0f0;padding:10px;border-radius:5px;margin-bottom:10px'><strong>Current LLM Provider:</strong> {llm_model}</div>", unsafe_allow_html=True)

report = st.text_area("Radiology Report", height=300)

if "history" not in st.session_state:
    st.session_state["history"] = []

prompt_template = (
    "Extract all positive diseases mentioned in the following radiology report. "
    "List them as a Python list of disease names, no explanations.\n\n"
    "{report}"
)
default_prompt = prompt_template.format(report=report)
prompt = st.text_area("Prompt", value=default_prompt, height=200)

if st.button("Analyze Report") and report.strip():
    from llm_output_parser import parse_disease_list
    if compare_mode:
        raw_llm_output_1 = call_llm(prompt, model=llm_model_1)
        raw_llm_output_2 = call_llm(prompt, model=llm_model_2)
        st.session_state["history"].append(("Compare", prompt, raw_llm_output_1, raw_llm_output_2))
        diseases_1 = parse_disease_list(raw_llm_output_1)
        diseases_2 = parse_disease_list(raw_llm_output_2)
    else:
        raw_llm_output_1 = call_llm(prompt, model=llm_model)
        st.session_state["history"].append(("Single", prompt, raw_llm_output_1))
        diseases_1 = parse_disease_list(raw_llm_output_1)
        diseases_2 = None

    if compare_mode:
        col1, col2 = st.columns(2)
        for label, diseases, model, col in [("Primary", diseases_1, llm_model_1, col1), ("Comparison", diseases_2, llm_model_2, col2)]:
            with col:
                st.markdown(f"### {label} Model: {model}")
                results = []
                for idx, disease in enumerate(diseases or [], 1):
                    code, desc = get_icd10_code(disease, fallback_llm=call_llm)
                    results.append((idx, disease, code or "N/A", desc or "N/A"))
                highlighted = report
                for idx, disease, _, _ in results:
                    highlighted = highlighted.replace(disease, f"**[{idx}] {disease}**")
                st.markdown(highlighted)
                import pandas as pd
                df = pd.DataFrame(
                    [(disease, code, desc) for idx, disease, code, desc in results],
                    columns=["Disease", "ICD-10", "Description"]
                )
                df.index = df.index + 1
                st.dataframe(df, use_container_width=True)
    else:
        results = []
        for idx, disease in enumerate(diseases_1, 1):
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

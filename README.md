# HiRes Hawk

A Streamlit web app for highlighting positive diseases in radiology reports, enumerating them, and displaying ICD-10 codes/descriptions.

## Features
- Paste a radiology report and extract positive diseases.
- Enumerated table of diseases with ICD-10 codes/descriptions.
- Configurable LLM backend (OpenAI or local LMstudio).
- English only for now.

## Setup

1. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```

2. Configure your LLM provider and API keys in `config.yaml`.

3. Run the app:
   ```
   streamlit run main.py
   ```
# hires-hawk

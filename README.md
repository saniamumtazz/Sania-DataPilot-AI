# Sania's DataPilot AI — Intelligent Data Analysis Workspace

**Created & developed by: Sania Mumtaz**  
**Domain:** Data Analytics · Generative AI · Agentic Workflow  
**Live framework:** Streamlit

Sania's DataPilot AI is a portfolio project that helps users explore CSV and Excel datasets, inspect data quality, clean records, generate visualizations, and produce a downloadable executive report. An optional Groq API integration adds natural-language AI interpretation. Core analytics work without an API key.

## Features
- CSV, XLSX and XLS upload
- Dataset overview: rows, columns, missing values, duplicates and memory use
- Column-level quality profile
- Duplicate removal and median imputation for numeric columns
- Automatic chart selection for date, category and numeric data
- Five-stage agent workflow display: Planner, Analyst, Coder, Visualizer and Reporter
- Optional Groq-powered recommendations
- Downloadable Markdown report and JSON workflow log
- Streamlit-ready single-file application for simple deployment

## Technology stack
Python · Streamlit · Pandas · NumPy · Plotly · Groq API (optional)

## Run locally

```bash
# 1. Clone your repository
git clone https://github.com/YOUR_GITHUB_USERNAME/Sania-DataPilot-AI.git
cd Sania-DataPilot-AI

# 2. Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 3. Install packages
pip install -r requirements.txt

# 4. Run the application
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Create a **public** GitHub repository named `Sania-DataPilot-AI`.
2. Extract this ZIP and upload the **contents** of this folder to the repository root (do not upload the ZIP itself).
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Select **New app** and choose your repository.
5. Set branch to `main` and main file path to `app.py`.
6. Click **Deploy**.

## Optional Groq API setup
The app works without an API key. To enable AI-generated interpretation, create a Groq API key and add it under Streamlit Cloud → your app → Settings → Secrets:

```toml
GROQ_API_KEY = "your_actual_api_key"
```

Never commit API keys, `.env` files or `secrets.toml` to GitHub.

## Project ownership and customization
This project displays **Sania Mumtaz** as its creator in the application interface and documentation. Review, understand, and customize the code before presenting it in interviews; be prepared to explain data cleaning, profiling, chart selection, the optional LLM integration, and deployment.

## Repository structure

```text
Sania-DataPilot-AI/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
└── .streamlit/
    └── config.toml
```

---
Built with Python and Streamlit · Portfolio project by Sania Mumtaz.

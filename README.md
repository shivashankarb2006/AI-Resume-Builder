# AI Resume Builder

<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/3135/3135768.png" width="100" alt="AI Resume Builder Logo" />
</p>

<p align="center">
  <b>Create an ATS-friendly resume tailored to your dream job with AI.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Anthropic-Claude_3.5_Sonnet-purple?logo=anthropic" alt="Claude API" />
  <img src="https://img.shields.io/badge/Tests-Pytest_Passing-success?logo=pytest" alt="Pytest Passing" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License" />
</p>

---

## 📌 Overview

**AI Resume Builder** is an open-source, production-ready web application that helps software engineers, students, and professionals craft Applicant Tracking System (ATS) compliant resumes tailored to specific job descriptions.

Powered by **Anthropic Claude 3.5 Sonnet** and built with **Streamlit**, the application adheres to strict anti-hallucination rules: **it never invents qualifications, fake metrics, or unearned skills**. Instead, it converts candidate facts into high-impact, action-oriented bullet points, detects keyword gaps against target job postings, calculates an ATS compatibility score, and exports recruiter-ready Microsoft Word (`.docx`), print-ready PDF, and plain text formats.

---

## ✨ Features

- **🛡️ 100% Fact-Preserving AI:** Built with 17 non-negotiable system prompts ensuring Claude never fabricates companies, degrees, percentages, or skills.
- **🎯 Dynamic Job Matching:** Tailors phrasing and highlights genuine candidate experiences that match target job requirements.
- **📊 ATS Compatibility Analyzer:**
  - Granular score breakdown out of 100 (*Keyword Match, Skills Alignment, Experience Relevance, Structure, and Completeness*).
  - Side-by-side keyword inspection (Matched vs. Missing job requirements).
  - Transparent ethical suggestions (never recommends adding skills dishonestly).
- **📥 Multi-Format Resume Export:**
  - **Microsoft Word (`.docx`):** ATS-compliant single-column layout with standard 0.6" margins, Arial typography, and subtle divider rules.
  - **Printable Vector PDF:** Standalone HTML template with `@media print` rules for browser-direct vector PDF printing (`Ctrl + P`).
  - **ATS Plain Text (`.txt`):** Unformatted plain text designed for pasting directly into job application text fields (Workday, Taleo, Greenhouse).
  - **GitHub Markdown (`.md`):** Clean markdown view for developer profiles.
- **⚡ Instant Demo / Mock Mode:** Allows testing the full generation, scoring, and download workflow offline without requiring an active Claude API key.
- **🔒 Production Security:** Multi-tier secret resolution supporting `.env` files, Streamlit Cloud Secrets, and session-only keys with zero data leakage.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend & UI** | [Streamlit](https://streamlit.io/) | Fast, reactive Python web dashboard with custom SaaS styling |
| **AI & LLM** | [Anthropic Claude](https://www.anthropic.com/) | Claude 3.5 Sonnet (`claude-3-5-sonnet-20241022`) via official Python SDK |
| **Document Generation** | [python-docx](https://python-docx.readthedocs.io/) | Low-level XML-based Microsoft Word (`.docx`) builder |
| **Templating Engine** | [Jinja2](https://palletsprojects.com/p/jinja/) | Dynamic HTML/CSS resume document generation |
| **Testing** | [pytest](https://pytest.org/) | Comprehensive unit test suite with 100% passing tests |
| **Environment Config** | [python-dotenv](https://github.com/theskumar/python-dotenv) | Secure local environment variable management |

---

## 🏗️ Architecture

```text
                    ┌─────────────────────────┐
                    │     User / Candidate    │
                    └────────────┬────────────┘
                                 │
                                 ▼
             ┌─────────────────────────────────────────┐
             │       Streamlit Multi-Tab Form          │
             │   (Personal, Education, Skills, Exp)    │
             └───────────────────┬─────────────────────┘
                                 │
                       [ Input Validation ]
                       (src/validators.py)
                                 │
                ┌────────────────┴────────────────┐
                ▼                                 ▼
     ┌───────────────────────┐       ┌────────────────────────┐
     │ Claude API (Prompts)  │       │   ATS Rule Analyzer    │
     │  (src/claude_api.py)  │       │  (src/ats_analyzer.py) │
     └──────────┬────────────┘       └───────────┬────────────┘
                │                                │
                ▼                                ▼
     ┌───────────────────────┐       ┌────────────────────────┐
     │ Structured JSON Model │       │  ATS Score Breakdown   │
     │  (Zero Hallucinations)│       │  & Keyword Gap Badges  │
     └──────────┬────────────┘       └────────────────────────┘
                │
                ▼
     ┌────────────────────────────────────────────────────────┐
     │                 Multi-Format Exporters                 │
     │   • src/docx_generator.py   ➔  ATS DOCX (.docx)        │
     │   • templates/resume.html   ➔  Vector PDF (Printable)  │
     │   • src/resume_generator.py ➔  Plain Text (.txt)       │
     └────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```text
AI-Resume-Builder/
│
├── app.py                      # Main Streamlit application and UI router
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation & setup guide
├── .gitignore                  # Git safeguard preventing secret & venv leakage
├── .env.example                # Example environment variables template
│
├── .streamlit/
│   └── config.toml             # Streamlit brand theme & security settings
│
├── src/
│   ├── __init__.py             # Python package marker
│   ├── validators.py           # Email, URL, and profile validation
│   ├── prompts.py              # Strict anti-hallucination Claude prompts
│   ├── claude_api.py           # Anthropic SDK client, JSON parser & mock mode
│   ├── resume_generator.py     # Multi-format renderer (Text, HTML, Markdown)
│   ├── ats_analyzer.py         # Keyword matcher, ATS scoring & suggestions
│   └── docx_generator.py       # ATS-compliant Microsoft Word generator
│
├── templates/
│   └── resume_template.html    # Print-ready ATS HTML/CSS resume template
│
└── tests/
    ├── __init__.py             # Test suite marker
    ├── test_validators.py      # Input validation unit tests
    ├── test_claude_api.py      # Prompt & API error handling unit tests
    ├── test_resume_generator.py# Rendering pipeline unit tests
    ├── test_docx_generator.py  # DOCX structure & corruption tests
    └── test_ats_analyzer.py    # Keyword matching & ATS scoring tests
```

---

## ⚙️ Installation & Local Setup

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed
- Git installed
- Windows PowerShell, macOS Terminal, or Linux Bash

### Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/AI-Resume-Builder.git
cd AI-Resume-Builder
```

### Step 2: Create a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to create your local `.env`:

```bash
# On Windows PowerShell:
Copy-Item .env.example .env

# On macOS / Linux:
cp .env.example .env
```

Open `.env` in your code editor and insert your Anthropic Claude API key:
```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```
*(Note: If you don't have an API key yet, you can toggle **🧪 Demo / Mock Mode** directly in the sidebar to test the entire application for free!)*

### Step 5: Launch the Application
```powershell
streamlit run app.py
```
Open `http://localhost:8501` in your browser!

---

## 🧪 Running Automated Tests

The application includes a comprehensive test suite covering all modules:

```powershell
# Run all tests:
pytest

# Run tests with detailed output:
pytest -v
```

All 17 unit tests run in less than 2 seconds with zero network dependencies.

---

## 🚀 Deployment to Streamlit Community Cloud

Deploying to **Streamlit Community Cloud** takes less than 3 minutes:

1. **Push your code to GitHub:**
   Make sure `.env` is ignored (already in `.gitignore`):
   ```powershell
   git add .
   git commit -m "feat: complete production AI Resume Builder"
   git push -u origin main
   ```

2. **Sign in to Streamlit Community Cloud:**
   Visit [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.

3. **Create New App:**
   - **Repository:** Select `your-username/AI-Resume-Builder`
   - **Branch:** `main`
   - **Main file path:** `app.py`

4. **Configure Secrets:**
   Click **Advanced Settings ➔ Secrets** and paste your Anthropic API Key in TOML format:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-your-actual-api-key-here"
   ```

5. **Deploy:**
   Click **Deploy!** Your app will build and go live with a public URL!

---

## 🔒 Security & Privacy

- **No Hard-coded Secrets:** API keys are never stored in source code, logs, or repositories.
- **Git Safeguards:** `.gitignore` excludes `.env`, `.streamlit/secrets.toml`, and virtual environment directories.
- **Input Sanitization:** User inputs are sanitized to prevent injection attacks and null-byte exploits.
- **Client Session Isolation:** Data entered by users stays strictly in their local browser session (`st.session_state`) and is never permanently stored on external databases.

---

## 🔮 Future Roadmap

- [ ] Multiple ATS-approved typography themes (Times New Roman, Calibri, Georgia)
- [ ] Cover letter generator tailored to target job requirements
- [ ] LinkedIn profile summary optimizer
- [ ] Interactive skill-gap learning resource recommendations
- [ ] Multi-language resume translation support

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

# AI Resume Builder — ATS-Friendly Resume Generator

> **Build an ATS-friendly resume with AI — locally, securely, and with zero paid cloud API dependencies.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red.svg)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/AI-Ollama%20(llama3.2)-orange.svg)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Overview

**AI Resume Builder** is an open-source, local-first web application designed to help students, recent graduates, and software engineers craft clean, high-impact, ATS-optimized resumes.

Unlike traditional AI resume tools that transmit personal career information to third-party paid cloud APIs (OpenAI, Claude, etc.), **this application operates 100% locally on your computer** using **Ollama** and lightweight open-source models like `llama3.2`. Your data stays on your machine at all times.

---

## ✨ Key Features

- **🔒 100% Local & Private:** Runs entirely on your machine via Ollama. No API keys, no monthly fees, and no external data leaks.
- **🛡️ Strict Anti-Hallucination AI:** Enhances phrasing and action verbs without inventing fake credentials, metrics, companies, or technologies.
- **⚡ Multiple Professional ATS Templates:**
  - **Classic ATS:** Timeless single-column layout with traditional typography. Highest ATS parse rate.
  - **Modern Professional:** Clean visual hierarchy with subtle slate/navy accents.
  - **Technical Specialist:** Tailored for Software Engineers, IT, and AI/ML candidates with prominent technical skills and project highlights.
- **🎯 Job Description Keyword Matcher:** Paste any job posting to identify matching skills, discover missing keywords, and tailor your bullet points truthfully.
- **📊 Transparent ATS Heuristic Score:** Objective 0–100 score evaluating Section Completeness, Action Verbs, Technical Depth, and Formatting Hygiene.
- **📑 Multi-Format Export:**
  - **PDF Export:** Clean ReportLab engine with exact A4 margins, clickable links, and multi-page numbering.
  - **Word (.docx) Export:** Editable Microsoft Word document with proper XML headings, bullet points, and hyperlinks.
- **👀 Live In-App Preview:** Real-time paper-like rendering that instantly updates as you edit.
- **📋 1-Click Demo Profile:** Instant demo profile loaded with realistic Computer Science student data.

---

## 🏗️ Architecture

```
User Input (Browser)
       │
       ▼
Streamlit Frontend (app.py)
       │
       ├──► Pydantic Data Validation (models/resume_schema.py)
       │
       ├──► Local AI Layer (ai/ollama_client.py & ai/prompts.py)
       │         │
       │         ▼
       │     Ollama LLM (llama3.2 running locally on localhost:11434)
       │         │
       │         ▼
       │     Structured Resume Data & Improved Bullet Points
       │
       ├──► ATS Scoring & Keyword Matcher (ai/analyzer.py)
       │
       └──► Resume Rendering & Export Engines
                 │
                 ├──► Live HTML Preview (resume/renderer.py)
                 ├──► ReportLab PDF Generator (resume/pdf_generator.py)
                 └──► python-docx Generator (resume/docx_generator.py)
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **UI Framework** | Streamlit | Responsive, interactive, card-based web interface |
| **Language** | Python 3.11+ | Core application logic and data pipelines |
| **AI Inference** | Ollama (`llama3.2`) | Local LLM inference for summary & bullet point synthesis |
| **Data Schema** | Pydantic v2 | Data validation, type safety, and serialization |
| **PDF Engine** | ReportLab | Flowable-based, ATS-compliant A4 PDF generation |
| **DOCX Engine** | python-docx | Editable Word document generation with native hyperlinks |
| **Testing** | Pytest | Automated test suite for validation and export engines |

---

## 🚀 Beginner Setup Guide (Windows)

Follow these exact steps to set up and run the project on Windows:

### Step 1: Install Ollama & Pull the Model

1. Download and install Ollama from [https://ollama.com/download](https://ollama.com/download).
2. Open PowerShell or Terminal and download the recommended lightweight model:
   ```powershell
   ollama pull llama3.2
   ```
3. Ensure Ollama is running (you should see the Ollama llama icon in your Windows system tray, or run `ollama serve`).

### Step 2: Open the Project Folder

Open your terminal or PowerShell and navigate to the project directory:
```powershell
cd "c:\Users\hp\OneDrive\Desktop\AI Resume Builder"
```

### Step 3: Create a Virtual Environment

```powershell
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

```powershell
.venv\Scripts\Activate.ps1
```
*(If you encounter an execution policy message in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 5: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 6: Start the Application

```powershell
streamlit run app.py
```

### What You Should See:
- Your default web browser will open automatically to `http://localhost:8501`.
- In the sidebar, the status badge will display **`● Ollama Online`** with `llama3.2` selected.
- Click **"📋 Load Demo"** in the sidebar to immediately see a pre-filled resume and test PDF/DOCX downloads!

---

## ⚙️ Configuration (`.env`)

No API keys are required! You can configure Ollama parameters using `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT_SECONDS=90
```

---

## 🧪 Running Automated Tests

To run the automated test suite:

```powershell
python -m pytest tests/ -v
```

All 21 unit tests cover:
- Email, URL, and Phone validation routines
- Filename sanitization and bullet point formatters
- Pydantic schema validation and JSON serialization
- PDF generation across all 3 templates (Classic, Modern, Technical)
- DOCX generation across all 3 templates
- ATS heuristic scoring and Job Matcher algorithms

---

## 📂 Project Structure

```
AI Resume Builder/
├── app.py                      # Main Streamlit web application
├── config.py                   # Centralized configuration & settings
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
├── README.md                   # Full documentation & guides
├── .env.example                # Example environment file
├── .gitignore                  # Git ignore rules
│
├── ai/
│   ├── __init__.py
│   ├── base.py                 # Abstract AI provider interface
│   ├── ollama_client.py        # Ollama HTTP client with error handling
│   ├── prompts.py              # Dedicated anti-hallucination system prompts
│   ├── resume_generator.py     # Section generation & bullet improvement
│   └── analyzer.py             # ATS scoring heuristic & Job Matcher
│
├── models/
│   ├── __init__.py
│   └── resume_schema.py        # Pydantic v2 data models
│
├── resume/
│   ├── __init__.py
│   ├── templates.py            # Resume styling & theme tokens
│   ├── renderer.py             # HTML/CSS live preview renderer
│   ├── pdf_generator.py        # ReportLab PDF generator
│   └── docx_generator.py       # python-docx Word generator
│
├── utils/
│   ├── __init__.py
│   ├── validation.py           # Email, URL, and input validation
│   ├── helpers.py              # Filename & string helpers
│   └── sample_data.py          # Demo profile dataset
│
├── assets/
│   └── custom.css              # Custom UI styling
│
└── tests/
    ├── __init__.py
    ├── test_validation.py      # Input validation tests
    ├── test_resume_schema.py   # Schema & serialization tests
    ├── test_generators.py      # PDF & DOCX export tests
    └── test_analyzer.py        # ATS scoring & keyword tests
```

---

## 🌐 Cloud Deployment Notice

Because this application relies on a **locally running Ollama instance**, deploying to Streamlit Community Cloud without modifications will not connect to your computer's local Ollama server.

### Future Cloud Deployment Options:
1. **Host Ollama on a Remote GPU Server:** Point `OLLAMA_BASE_URL` to a self-hosted cloud endpoint (e.g. RunPod, Vast.ai, AWS EC2).
2. **Provider Swapping:** The AI layer uses an abstract provider interface (`ai/base.py`), enabling straightforward integration with OpenAI-compatible endpoints or free HuggingFace endpoints without rewriting application logic.

---

## 💼 Portfolio & Resume Highlights

### Recruiter-Ready Summary
> *"Built an end-to-end, privacy-focused AI Resume Builder in Python and Streamlit powered by local LLMs via Ollama. Features automated ATS keyword matching, multi-template styling, transparent scoring heuristics, and dual export to ReportLab PDF and python-docx."*

### Resume Bullet Points
- Engineered a full-stack local AI Resume Generator using **Streamlit**, **Python**, and **Ollama**, ensuring 100% data privacy with zero external API dependencies.
- Implemented an ATS optimization engine featuring keyword gap analysis against job descriptions and a defensible 0–100 heuristic scoring algorithm.
- Designed dual export pipelines utilizing **ReportLab** (A4 PDF with custom flowables and hyperlinks) and **python-docx** (native Word typography and styles).
- Architected strict prompt engineering guards and Pydantic validation schemas to guarantee grounded outputs and eliminate AI hallucinations.

---

## 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

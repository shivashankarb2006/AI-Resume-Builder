# Deployment Guide — AI Resume Builder

This guide explains how to deploy the **AI Resume Builder** to public cloud platforms.

---

## ⚠️ Important Note Regarding Local Ollama & Cloud

When you deploy a Streamlit app to the cloud (such as **Streamlit Community Cloud** or **Render**), the application code executes on a remote cloud server. 

By default, the cloud server **cannot connect to `http://localhost:11434`** because `localhost` on the cloud refers to the cloud container, not your personal computer!

### What Works on the Cloud Without Ollama:
- ✅ Full Resume Form Entry & Editing
- ✅ Real-time ATS Resume Live Preview (all 3 templates)
- ✅ 0–100 Defensible ATS Heuristic Scoring
- ✅ Job Description Keyword & Skill Matching (Matching vs. Missing skills)
- ✅ 1-Click Demo Data Loading
- ✅ High-Quality PDF Export via ReportLab
- ✅ Editable Word (.docx) Export via python-docx

### For the AI Features (Summary Generation & Bullet Improvement) on Cloud:
You have two straightforward, free options explained below: **Cloudflare / Ngrok Tunnel** (connecting your local Ollama) or **Streamlit Community Cloud with Tunnel**.

---

## Option 1: Streamlit Community Cloud (Recommended & 100% Free)

### Step 1: Push Code to GitHub
Ensure all your project code is pushed to your GitHub repository:
```powershell
git add -A
git commit -m "Add cloud deployment configuration"
git push origin main
```

### Step 2: Sign in to Streamlit Community Cloud
1. Visit [share.streamlit.io](https://share.streamlit.io/) and click **Sign in with GitHub**.
2. Click **Create app** (or **New app**).

### Step 3: Configure Your App
- **Repository:** `shivashankarb2006/AI-Resume-Builder` (or your repo name)
- **Branch:** `main`
- **Main file path:** `app.py`
- **App URL:** (Choose a custom subdomain or use the default)

### Step 4: Click Deploy!
Streamlit will install dependencies from `requirements.txt` and launch your app in ~1-2 minutes.

---

## How to Enable AI on Your Cloud Deployment (Free Tunneling)

If you want the AI "Generate with AI" buttons to work on your public Streamlit Cloud link:

### Using Free Cloudflare Tunnel (No Account Needed):
1. Download `cloudflared` from Cloudflare or via winget:
   ```powershell
   winget install Cloudflare.cloudflared
   ```
2. In PowerShell, run:
   ```powershell
   cloudflared tunnel --url http://localhost:11434
   ```
3. Cloudflare will give you a public URL (e.g. `https://random-words.trycloudflare.com`).
4. On your deployed Streamlit Cloud app:
   - In the sidebar, expand **🌐 Cloud / Endpoint Settings**.
   - Paste the `https://random-words.trycloudflare.com` URL into **Ollama Server URL**.
   - Your deployed cloud app will now generate AI summaries and bullets using your PC's Ollama!

*(Alternatively, configure `OLLAMA_BASE_URL` in Streamlit Cloud under **App Settings → Secrets**).*

---

## Option 2: Docker Container Deployment

If deploying to Docker Desktop, AWS EC2, or a VPS:

### Build the Docker Image:
```bash
docker build -t ai-resume-builder .
```

### Run the Container:
```bash
# To connect to Ollama running on the host machine:
docker run -p 8501:8501 -e OLLAMA_BASE_URL="http://host.docker.internal:11434" ai-resume-builder
```

Open `http://localhost:8501` in your browser.

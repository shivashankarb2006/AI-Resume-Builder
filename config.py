"""
Application Configuration for AI Resume Builder.
Centralizes all settings, environment variables, model choices, and template definitions.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if it exists
load_dotenv(BASE_DIR / ".env")

# Ollama Configuration
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT_SECONDS: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "90"))

# Application Metadata
APP_TITLE: str = "AI Resume Builder"
APP_SUBTITLE: str = "Build an ATS-friendly resume with AI — locally and securely."
APP_VERSION: str = "1.0.0"
PRIVACY_STATEMENT: str = (
    "🔒 Your resume data is processed locally using Ollama and is not sent to a cloud AI API by this application."
)

# Suggested lightweight local models suitable for student laptops
RECOMMENDED_MODELS = [
    "llama3.2",
    "llama3.2:3b",
    "llama3.2:1b",
    "mistral",
    "gemma2:2b",
    "qwen2.5:3b",
    "deepseek-r1:1.5b",
]

# Resume Template Identifiers
TEMPLATE_CLASSIC_ATS: str = "Classic ATS"
TEMPLATE_MODERN_PROFESSIONAL: str = "Modern Professional"
TEMPLATE_TECHNICAL_SPECIALIST: str = "Technical Specialist"

RESUME_TEMPLATES = [
    TEMPLATE_CLASSIC_ATS,
    TEMPLATE_MODERN_PROFESSIONAL,
    TEMPLATE_TECHNICAL_SPECIALIST,
]

# Available Resume Sections for User Selection
AVAILABLE_SECTIONS = [
    "Professional Summary",
    "Education",
    "Skills",
    "Experience",
    "Projects",
    "Certifications",
    "Achievements",
    "Relevant Coursework",
    "Volunteer Experience",
]

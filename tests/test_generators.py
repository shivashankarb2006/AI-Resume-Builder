"""
Unit tests for PDF, DOCX, and HTML generators.
Verifies binary output validity, non-empty outputs, and cross-template support.
"""
import io
import pytest
from models.resume_schema import ResumeData, PersonalInfo
from utils.sample_data import get_sample_resume_data
from resume.pdf_generator import generate_resume_pdf
from resume.docx_generator import generate_resume_docx
from resume.renderer import render_resume_html
from resume.templates import RESUME_TEMPLATES


def test_pdf_generation_minimal():
    minimal_resume = ResumeData(
        personal_info=PersonalInfo(full_name="Minimal Candidate", email="min@example.com")
    )
    pdf_bytes = generate_resume_pdf(minimal_resume)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    # PDF magic bytes
    assert pdf_bytes.startswith(b"%PDF")


def test_pdf_generation_full_sample_all_templates():
    sample = get_sample_resume_data()
    for tpl in RESUME_TEMPLATES:
        sample.selected_template = tpl
        pdf_bytes = generate_resume_pdf(sample)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 2000
        assert pdf_bytes.startswith(b"%PDF")


def test_docx_generation_minimal():
    minimal_resume = ResumeData(
        personal_info=PersonalInfo(full_name="Minimal Candidate", email="min@example.com")
    )
    docx_bytes = generate_resume_docx(minimal_resume)
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 500
    # DOCX is a zip archive, check zip magic bytes PK
    assert docx_bytes.startswith(b"PK")


def test_docx_generation_full_sample_all_templates():
    sample = get_sample_resume_data()
    for tpl in RESUME_TEMPLATES:
        sample.selected_template = tpl
        docx_bytes = generate_resume_docx(sample)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 2000
        assert docx_bytes.startswith(b"PK")


def test_html_renderer_output():
    sample = get_sample_resume_data()
    for tpl in RESUME_TEMPLATES:
        sample.selected_template = tpl
        html = render_resume_html(sample)
        assert "Alex Chen (Demo)" in html
        assert "California State University" in html
        assert "Python" in html
        assert "PROFESSIONAL SUMMARY" in html

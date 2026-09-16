"""
Unit tests for Resume Pydantic models and schemas.
"""
import pytest
from models.resume_schema import (
    ResumeData,
    PersonalInfo,
    EducationEntry,
    SkillsData,
    SkillCategory,
    ExperienceEntry,
    ProjectEntry,
    CertificationEntry,
    AchievementEntry,
)
from utils.sample_data import get_sample_resume_data


def test_empty_resume_data_defaults():
    resume = ResumeData()
    assert resume.personal_info.is_empty() is True
    assert resume.education == []
    assert resume.skills.is_empty() is True
    assert resume.experience == []
    assert resume.projects == []
    assert resume.certifications == []
    assert resume.achievements == []
    assert resume.selected_template == "Classic ATS"
    assert len(resume.enabled_sections) > 0


def test_is_empty_checks():
    # PersonalInfo
    p_empty = PersonalInfo()
    assert p_empty.is_empty() is True

    p_valid = PersonalInfo(full_name="Alex Chen", email="alex@example.com")
    assert p_valid.is_empty() is False

    # EducationEntry
    e_empty = EducationEntry()
    assert e_empty.is_empty() is True

    e_valid = EducationEntry(institution="UC Berkeley", degree="B.S.")
    assert e_valid.is_empty() is False

    # ExperienceEntry
    exp_empty = ExperienceEntry()
    assert exp_empty.is_empty() is True

    exp_valid = ExperienceEntry(company="Tech Corp", role="Intern")
    assert exp_valid.is_empty() is False

    # ProjectEntry
    proj_empty = ProjectEntry()
    assert proj_empty.is_empty() is True

    proj_valid = ProjectEntry(name="AI Resume Builder")
    assert proj_valid.is_empty() is False

    # SkillsData
    skills_empty = SkillsData()
    assert skills_empty.is_empty() is True

    skills_valid = SkillsData(programming_languages=["Python"])
    assert skills_valid.is_empty() is False

    skills_custom = SkillsData(
        custom_categories=[SkillCategory(category_name="Cloud", skills=["AWS"])]
    )
    assert skills_custom.is_empty() is False


def test_sample_resume_data_integrity():
    sample = get_sample_resume_data()
    assert not sample.personal_info.is_empty()
    assert len(sample.education) == 1
    assert len(sample.experience) == 1
    assert len(sample.projects) == 2
    assert len(sample.skills.programming_languages) >= 3
    assert len(sample.certifications) == 1
    assert len(sample.achievements) == 2
    assert sample.summary != ""
    assert sample.target_job.title != ""


def test_resume_serialization_roundtrip():
    sample = get_sample_resume_data()
    json_str = sample.model_dump_json()
    assert isinstance(json_str, str)

    # Reconstruct
    reloaded = ResumeData.model_validate_json(json_str)
    assert reloaded.personal_info.full_name == sample.personal_info.full_name
    assert reloaded.skills.programming_languages == sample.skills.programming_languages
    assert len(reloaded.projects) == len(sample.projects)

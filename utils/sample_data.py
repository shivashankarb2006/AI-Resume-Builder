"""
Fictional demo data for testing and one-click preview in AI Resume Builder.
Represents a realistic Computer Science student profile seeking a software engineering internship.
"""
from models.resume_schema import (
    ResumeData,
    PersonalInfo,
    EducationEntry,
    SkillsData,
    ExperienceEntry,
    ProjectEntry,
    CertificationEntry,
    AchievementEntry,
    TargetJob,
)


def get_sample_resume_data() -> ResumeData:
    """Return a fully populated fictional sample ResumeData object."""
    return ResumeData(
        personal_info=PersonalInfo(
            full_name="Alex Chen (Demo)",
            email="alex.chen.demo@example.com",
            phone="+1 (555) 234-5678",
            location="San Jose, CA",
            linkedin_url="https://linkedin.com/in/alexchen-demo",
            github_url="https://github.com/alexchen-demo",
            portfolio_url="https://alexchen-portfolio.demo.dev",
        ),
        summary=(
            "Motivated Computer Science undergraduate with hands-on experience in full-stack web development, "
            "Python automation, and applied machine learning. Demonstrated ability to design RESTful APIs, "
            "optimize SQL queries, and collaborate in agile engineering teams through an internship and competitive hackathons."
        ),
        education=[
            EducationEntry(
                institution="California State University",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                start_year="2022",
                end_year="2026",
                gpa="3.85 / 4.0",
                relevant_coursework="Data Structures, Algorithms, Object-Oriented Programming, Database Systems, Operating Systems",
            )
        ],
        skills=SkillsData(
            programming_languages=["Python", "Java", "C++", "JavaScript", "SQL"],
            frameworks=["Streamlit", "Flask", "FastAPI", "React", "Node.js"],
            tools=["Git", "GitHub", "Docker", "VS Code", "Postman", "Linux"],
            ai_ml=["PyTorch", "Scikit-Learn", "Ollama", "Pandas", "NumPy"],
            databases=["PostgreSQL", "MySQL", "MongoDB", "SQLite"],
        ),
        experience=[
            ExperienceEntry(
                company="Apex Cloud Technologies",
                role="Software Engineering Intern",
                location="San Jose, CA",
                start_date="Jun 2024",
                end_date="Aug 2024",
                is_current=False,
                responsibilities="Built internal microservices using Python and FastAPI. Wrote automated unit and integration tests. Collaborated with senior engineers in bi-weekly agile sprints.",
                achievements="Reduced API response latency by optimizing database queries and indexes. Increased test suite coverage across core service modules.",
                improved_bullets=[
                    "Architected high-throughput RESTful endpoints using FastAPI and PostgreSQL, supporting internal service orchestration.",
                    "Engineered optimized SQL query execution paths and database indexes, reducing median endpoint latency.",
                    "Authored comprehensive PyTest test suites, expanding code coverage across key business logic modules.",
                    "Collaborated in bi-weekly agile sprints, actively participating in code reviews and sprint planning sessions.",
                ],
            )
        ],
        projects=[
            ProjectEntry(
                name="AI Document Retrieval & Q&A Engine",
                description="A local semantic search and document question-answering tool built with Python, Ollama, and vector embeddings.",
                technologies=["Python", "Ollama", "LangChain", "Streamlit", "ChromaDB"],
                github_url="https://github.com/alexchen-demo/doc-retrieval-ai",
                demo_url="https://doc-retrieval.demo.dev",
                key_contributions="Implemented document chunking and embedding pipelines. Built an intuitive Streamlit interface for PDF ingestion and query response generation.",
                improved_bullets=[
                    "Engineered a local retrieval-augmented generation (RAG) pipeline utilizing Ollama and vector embeddings to extract answers from uploaded PDFs.",
                    "Constructed an interactive Streamlit UI with file drag-and-drop, real-time chunking visualization, and response streaming.",
                    "Implemented text sanitization and caching routines to eliminate redundant LLM inference passes for duplicate queries.",
                ],
            ),
            ProjectEntry(
                name="Distributed Task Queue & Notification Service",
                description="Asynchronous job worker system for scheduled background tasks and real-time webhook dispatching.",
                technologies=["Java", "Spring Boot", "Redis", "Docker", "PostgreSQL"],
                github_url="https://github.com/alexchen-demo/task-queue-service",
                demo_url="",
                key_contributions="Created Redis pub/sub queue consumer, managed worker pool concurrency, and containerized the service with Docker Compose.",
                improved_bullets=[
                    "Developed asynchronous message processing workers in Java and Spring Boot with Redis message queuing.",
                    "Configured Docker Compose multi-container environments enabling reproducible local deployment and database seeding.",
                    "Implemented exponential backoff retry policies for failed external webhook requests to guarantee message delivery.",
                ],
            ),
        ],
        certifications=[
            CertificationEntry(
                name="AWS Certified Cloud Practitioner",
                issuer="Amazon Web Services",
                issue_date="Nov 2023",
                credential_url="https://aws.amazon.com/verification/demo-cert-123",
            )
        ],
        achievements=[
            AchievementEntry(
                title="1st Place Winner — Campus Hackathon 2024",
                issuer_or_event="University ACM Chapter",
                date="Mar 2024",
                description="Led a team of 4 to create an accessible campus navigation assistant within 36 hours.",
            ),
            AchievementEntry(
                title="Dean's Honor List",
                issuer_or_event="College of Engineering",
                date="2022 - 2024",
                description="Awarded for maintaining a semester GPA above 3.75 for four consecutive terms.",
            ),
        ],
        target_job=TargetJob(
            title="Software Engineering Intern",
            job_description=(
                "We are seeking a Software Engineering Intern to join our engineering team. "
                "The ideal candidate has strong programming skills in Python, Java, or C++, "
                "experience with relational databases like PostgreSQL or MySQL, familiarity with Git version control, "
                "and an interest in building scalable web APIs and machine learning applications. "
                "Responsibilities include contributing to backend services, writing automated unit tests, "
                "and collaborating with cross-functional teams in an agile environment."
            ),
        ),
        selected_template="Classic ATS",
        enabled_sections=[
            "Professional Summary",
            "Education",
            "Skills",
            "Experience",
            "Projects",
            "Certifications",
            "Achievements",
        ],
    )

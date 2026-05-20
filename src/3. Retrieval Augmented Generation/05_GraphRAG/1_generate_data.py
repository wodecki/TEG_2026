"""
GraphRAG Data Generation - Single Integrated Module
==================================================

Generates realistic programmer profiles and PDF CVs for GraphRAG educational demonstration.
Uses LLM to create unique, unstructured CVs in markdown format, then converts to PDF.

CRITICAL: No fallbacks, no mock data. All dependencies must be available.
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import os
import json
import random
import toml
from datetime import date, datetime, timedelta
from faker import Faker
from typing import List
from langchain_openai import ChatOpenAI
import markdown
from weasyprint import HTML, CSS

fake = Faker()


class GraphRAGDataGenerator:
    """Integrated generator for programmer profiles and realistic PDF CVs."""

    def __init__(self, config_path: str = "utils/config.toml"):
        """Initialize with required dependencies - fail fast if missing."""
        # Load configuration
        self.config = self._load_config(config_path)

        # Validate environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=api_key
        )

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from TOML file."""
        if not os.path.exists(config_path):
            raise ValueError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = toml.load(f)

        return config

    def generate_programmer_profiles(self, num_profiles: int) -> List[dict]:
        """Generate realistic programmer profiles."""
        if num_profiles <= 0:
            raise ValueError("Number of profiles must be positive")

        profiles = []
        for i in range(num_profiles):
            profile = {
                "id": i + 1,
                "name": fake.name(),
                "email": fake.email(),
                "location": fake.city(),
                "skills": self._generate_skills(),
                "projects": self._generate_projects(),
                "certifications": self._generate_certifications(),
            }
            profiles.append(profile)

        return profiles

    def _generate_skills(self) -> List[dict]:
        """Generate realistic programming skills with proficiency levels."""
        all_skills = [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
            "React", "Vue.js", "Angular", "Node.js", "Django", "Flask", "FastAPI",
            "PostgreSQL", "MongoDB", "Redis", "MySQL",
            "AWS", "Docker", "Kubernetes", "Jenkins", "Git",
            "Machine Learning", "Data Science", "DevOps", "Microservices"
        ]

        proficiency_levels = [
            "Beginner", "Intermediate", "Advanced", "Expert"
        ]

        num_skills = random.randint(5, 12)
        selected_skills = random.sample(all_skills, num_skills)

        skills_with_proficiency = []
        for skill in selected_skills:
            # Weight proficiency levels from config
            proficiency = random.choices(
                proficiency_levels,
                weights=self.config['skills']['proficiency_weights']
            )[0]

            skills_with_proficiency.append({
                "name": skill,
                "proficiency": proficiency
            })

        return skills_with_proficiency

    def _generate_projects(self) -> List[str]:
        """Generate realistic project names."""
        project_types = [
            "E-commerce Platform", "Data Analytics Dashboard", "Mobile App",
            "API Gateway", "Machine Learning Pipeline", "Web Application",
            "Microservices Architecture", "Real-time Chat System",
            "Content Management System", "Payment Processing System"
        ]
        num_projects = random.randint(2, 5)
        return random.sample(project_types, num_projects)

    def _generate_certifications(self) -> List[str]:
        """Generate realistic certifications."""
        certs = [
            "AWS Certified Solutions Architect",
            "Google Cloud Professional",
            "Certified Kubernetes Administrator",
            "Microsoft Azure Developer",
            "Scrum Master Certification",
            "Docker Certified Associate"
        ]
        num_certs = random.randint(0, 3)
        return random.sample(certs, num_certs) if num_certs > 0 else []

    def generate_projects(self, num_projects: int = 20, programmer_profiles: List[dict] = None) -> List[dict]:
        """Generate realistic project data with programmer assignments."""
        if num_projects <= 0:
            raise ValueError("Number of projects must be positive")

        project_types = [
            "E-commerce Platform", "Data Analytics Dashboard", "Mobile App Development",
            "API Gateway Implementation", "Machine Learning Pipeline", "Web Application",
            "Microservices Architecture", "Real-time Chat System", "Content Management System",
            "Payment Processing System", "DevOps Automation", "Cloud Migration",
            "Security Audit System", "Inventory Management", "Customer Portal"
        ]

        clients = [
            "TechCorp", "DataSystems Inc", "CloudNative Solutions", "FinTech Innovations",
            "HealthTech Partners", "RetailMax", "LogisticsPro", "EduTech Solutions",
            "MediaStream", "GreenEnergy Co", "SmartCity Initiative", "BioTech Labs"
        ]

        projects = []

        # If programmer profiles provided, use their skills for requirements
        if programmer_profiles:
            # Collect all unique skills from programmer profiles
            available_skills = set()
            for profile in programmer_profiles:
                for skill in profile['skills']:
                    available_skills.add(skill['name'])
            skill_names = list(available_skills)
        else:
            # Fallback to default skill list
            skill_names = [
                "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
                "React", "Vue.js", "Angular", "Node.js", "Django", "Flask", "FastAPI",
                "PostgreSQL", "MongoDB", "Redis", "MySQL", "AWS", "Docker", "Kubernetes",
                "Jenkins", "Git", "Machine Learning", "Data Science", "DevOps", "Microservices"
            ]

        for i in range(num_projects):
            start_date = fake.date_between(start_date='-2y', end_date='+6m')
            duration_months = random.randint(3, 18)

            # Some projects are completed, some ongoing, some planned
            status_weights = [50, 30, 15, 5]  # completed, active, planned, on_hold
            status = random.choices(
                ["completed", "active", "planned", "on_hold"],
                weights=status_weights
            )[0]

            if status == "completed":
                end_date = start_date + timedelta(days=duration_months * 30)
            elif status == "active":
                end_date = None
            else:
                end_date = None

            # Generate skill requirements based on available programmer skills
            requirements = []
            if programmer_profiles:
                # Generate requirements that can be satisfied by some programmers
                num_requirements = random.randint(
                    self.config['project_requirements']['min_requirements'],
                    self.config['project_requirements']['max_requirements']
                )
                required_skills = random.sample(skill_names, num_requirements)

                for skill in required_skills:
                    # Use config for mandatory probability and proficiency levels
                    is_mandatory = random.random() < self.config['project_requirements']['mandatory_probability']
                    requirements.append({
                        "skill_name": skill,
                        "min_proficiency": random.choice(self.config['skills']['proficiency_levels']),
                        "is_mandatory": is_mandatory
                    })
            else:
                # Fallback to original logic if no profiles
                num_requirements = random.randint(3, 8)
                required_skills = random.sample(skill_names, num_requirements)

                for skill in required_skills:
                    requirements.append({
                        "skill_name": skill,
                        "min_proficiency": random.choice(["Beginner", "Intermediate", "Advanced", "Expert"]),
                        "is_mandatory": random.choice([True, True, False])
                    })

            project = {
                "id": f"PRJ-{i+1:03d}",
                "name": f"{random.choice(project_types)} for {random.choice(clients)}",
                "client": random.choice(clients),
                "description": f"Development of {random.choice(project_types).lower()} with focus on scalability and performance",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat() if end_date else None,
                "estimated_duration_months": duration_months,
                "budget": random.randint(50000, 500000) if random.choice([True, False]) else None,
                "status": status,
                "team_size": random.randint(2, 8),
                "requirements": requirements,
                "assigned_programmers": []
            }
            projects.append(project)

        # Assign programmers to projects if profiles provided
        if programmer_profiles:
            projects = self._assign_programmers_to_projects(projects, programmer_profiles)

        return projects

    def _assign_programmers_to_projects(self, projects: List[dict], programmer_profiles: List[dict]) -> List[dict]:
        """Assign programmers to projects based on skill matching, leaving some unassigned."""

        # Create a list to track programmer availability periods
        programmer_assignments = {p['id']: [] for p in programmer_profiles}

        # Helper function to check if programmer has required skill at minimum proficiency
        def has_skill_requirement(programmer, skill_name, min_proficiency):
            proficiency_levels = {"Beginner": 1, "Intermediate": 2, "Advanced": 3, "Expert": 4}
            min_level = proficiency_levels[min_proficiency]

            for skill in programmer['skills']:
                if skill['name'] == skill_name:
                    programmer_level = proficiency_levels[skill['proficiency']]
                    return programmer_level >= min_level
            return False

        # Helper function to check if programmer is available during project period
        def is_available(programmer_id, start_date, end_date):
            assignments = programmer_assignments[programmer_id]
            project_start = datetime.fromisoformat(start_date).date()
            project_end = datetime.fromisoformat(end_date).date() if end_date else None

            for assignment in assignments:
                assign_start = datetime.fromisoformat(assignment['assignment_start_date']).date()
                assign_end = datetime.fromisoformat(assignment['assignment_end_date']).date() if assignment['assignment_end_date'] else None

                # Check for overlap
                if assign_end is None:  # Ongoing assignment
                    if project_end is None or project_start <= assign_start:
                        return False
                elif project_end is None:  # Ongoing project
                    if assign_end >= project_start:
                        return False
                else:  # Both have end dates
                    if not (project_end < assign_start or project_start > assign_end):
                        return False
            return True

        # Process only active and completed projects for assignments
        assignable_projects = [p for p in projects if p['status'] in ['active', 'completed']]

        # Assign programmers to projects (configurable percentage to leave some available)
        assignment_probability = self.config['assignment']['assignment_probability']

        for project in assignable_projects:
            if random.random() > assignment_probability:
                continue  # Skip this project to leave programmers available

            assigned_count = 0
            max_assignments = min(project['team_size'], len(programmer_profiles))

            # Get mandatory requirements
            mandatory_requirements = [req for req in project['requirements'] if req['is_mandatory']]

            # Try to find programmers matching mandatory skills
            eligible_programmers = []
            for programmer in programmer_profiles:
                matches_mandatory = True
                for req in mandatory_requirements:
                    if not has_skill_requirement(programmer, req['skill_name'], req['min_proficiency']):
                        matches_mandatory = False
                        break

                if matches_mandatory and is_available(programmer['id'], project['start_date'], project['end_date']):
                    eligible_programmers.append(programmer)

            # Randomly select from eligible programmers
            selected_programmers = random.sample(
                eligible_programmers,
                min(max_assignments, len(eligible_programmers))
            )

            # Create assignments
            for programmer in selected_programmers:
                # Calculate assignment dates based on project dates
                assignment_start = project['start_date']

                # Always calculate assignment end date (before project end)
                if project['status'] == 'completed':
                    # For completed projects, assignment ends before or at project end
                    project_end = datetime.fromisoformat(project['end_date']).date()
                    project_start = datetime.fromisoformat(project['start_date']).date()
                    project_duration = (project_end - project_start).days

                    # Assignment ends configurable days before project end (but at least 1 day after start)
                    days_before_end = min(
                        random.randint(
                            self.config['assignment']['assignment_end_days_before_min'],
                            self.config['assignment']['assignment_end_days_before_max']
                        ),
                        max(1, project_duration - 1)
                    )
                    assignment_end_date = project_end - timedelta(days=days_before_end)
                    assignment_end = assignment_end_date.isoformat()

                elif project['status'] == 'active':
                    # For active projects, calculate end date based on estimated duration
                    project_start = datetime.fromisoformat(project['start_date']).date()
                    estimated_end = project_start + timedelta(days=project['estimated_duration_months'] * 30)

                    # Assignment ends configurable days before estimated project end
                    days_before_end = random.randint(
                        self.config['assignment']['assignment_end_days_before_min'],
                        self.config['assignment']['assignment_end_days_before_max']
                    )
                    assignment_end_date = estimated_end - timedelta(days=days_before_end)
                    assignment_end = assignment_end_date.isoformat()

                else:
                    # For other statuses, use project end date if available
                    if project['end_date']:
                        project_end = datetime.fromisoformat(project['end_date']).date()
                        project_start = datetime.fromisoformat(project['start_date']).date()
                        project_duration = (project_end - project_start).days
                        days_before_end = min(
                            random.randint(
                                self.config['assignment']['assignment_end_days_before_min'],
                                self.config['assignment']['assignment_end_days_before_max']
                            ),
                            max(1, project_duration - 1)
                        )
                        assignment_end_date = project_end - timedelta(days=days_before_end)
                        assignment_end = assignment_end_date.isoformat()
                    else:
                        # Fallback: use estimated duration
                        project_start = datetime.fromisoformat(project['start_date']).date()
                        estimated_end = project_start + timedelta(days=project['estimated_duration_months'] * 30)
                        days_before_end = random.randint(
                            self.config['assignment']['assignment_end_days_before_min'],
                            self.config['assignment']['assignment_end_days_before_max']
                        )
                        assignment_end_date = estimated_end - timedelta(days=days_before_end)
                        assignment_end = assignment_end_date.isoformat()

                assignment = {
                    "programmer_name": programmer['name'],
                    "programmer_id": programmer['id'],
                    "assignment_start_date": assignment_start,
                    "assignment_end_date": assignment_end
                }

                project['assigned_programmers'].append(assignment)
                programmer_assignments[programmer['id']].append(assignment)
                assigned_count += 1

        return projects

    def generate_rfps(self, num_rfps: int = 3) -> List[dict]:
        """Generate realistic RFP (Request for Proposal) data."""
        if num_rfps <= 0:
            raise ValueError("Number of RFPs must be positive")

        rfp_types = [
            "Enterprise Web Application", "Mobile App Development", "Data Analytics Platform",
            "Cloud Migration Project", "E-commerce Modernization", "API Integration Platform",
            "Machine Learning Implementation", "DevOps Automation", "Security Enhancement"
        ]

        clients = [
            "Global Finance Corp", "MedTech Industries", "Retail Solutions Ltd",
            "Manufacturing Plus", "Education Network", "Energy Systems Co"
        ]

        budget_ranges = [
            "$100K - $250K", "$250K - $500K", "$500K - $1M", "$1M - $2M"
        ]

        skill_names = [
            "Python", "JavaScript", "TypeScript", "Java", "React", "Angular",
            "Node.js", "Django", "AWS", "Docker", "Kubernetes", "PostgreSQL",
            "MongoDB", "Machine Learning", "DevOps", "Microservices"
        ]

        rfps = []
        for i in range(num_rfps):
            start_date = fake.date_between(start_date='+1m', end_date='+6m')

            # Generate skill requirements
            num_requirements = random.randint(4, 10)
            requirements = []
            required_skills = random.sample(skill_names, num_requirements)

            for skill in required_skills:
                requirements.append({
                    "skill_name": skill,
                    "min_proficiency": random.choice(["Intermediate", "Advanced", "Expert"]),
                    "is_mandatory": random.choice([True, True, False]),
                    "preferred_certifications": random.sample([
                        "AWS Certified Solutions Architect",
                        "Google Cloud Professional",
                        "Certified Kubernetes Administrator"
                    ], random.randint(0, 2))
                })

            rfp = {
                "id": f"RFP-{i+1:03d}",
                "title": f"{random.choice(rfp_types)} Development",
                "client": random.choice(clients),
                "description": f"Seeking experienced development team for {random.choice(rfp_types).lower()}",
                "project_type": random.choice(rfp_types),
                "duration_months": random.randint(6, 24),
                "team_size": random.randint(3, 12),
                "budget_range": random.choice(budget_ranges),
                "start_date": start_date.isoformat(),
                "requirements": requirements,
                "location": fake.city(),
                "remote_allowed": random.choice([True, True, False])  # More likely to allow remote
            }
            rfps.append(rfp)

        return rfps

    def generate_rfp_markdown(self, rfp: dict) -> str:
        """Generate realistic RFP document in markdown format using LLM."""

        # Format requirements for the prompt
        requirements_text = []
        for req in rfp['requirements']:
            cert_text = f" (Preferred certifications: {', '.join(req['preferred_certifications'])})" if req['preferred_certifications'] else ""
            mandatory_text = "REQUIRED" if req['is_mandatory'] else "Preferred"
            requirements_text.append(f"- {mandatory_text}: {req['skill_name']} - {req['min_proficiency']} level{cert_text}")

        prompt = f"""
Create a professional RFP (Request for Proposal) document in markdown format with the following details:

Project: {rfp['title']}
Client: {rfp['client']}
Project Type: {rfp['project_type']}
Description: {rfp['description']}
Duration: {rfp['duration_months']} months
Team Size: {rfp['team_size']} people
Budget Range: {rfp['budget_range']}
Start Date: {rfp['start_date']}
Location: {rfp['location']}
Remote Work: {"Allowed" if rfp['remote_allowed'] else "Not allowed"}

Technical Requirements:
{chr(10).join(requirements_text)}

Requirements:
1. Use proper markdown formatting (headers, lists, emphasis)
2. Structure as a professional PRD (Product Requirements Document)
3. Include sections like: Executive Summary, Project Overview, Technical Requirements, Expected Team Profile, Timeline, Budget, Proposal Guidelines
4. Create realistic business context and objectives
5. Add specific deliverables and milestones
6. Include detailed descriptions of the expected programmer profiles
7. Make it sound professional and business-oriented
8. Add acceptance criteria and evaluation process
9. Include contact information and proposal submission guidelines

Focus on creating a comprehensive PRD that clearly outlines what the client needs and what kind of development team they're looking for.

IMPORTANT: Return ONLY the RFP content in markdown format. Do NOT include any code block markers like ```markdown or ``` in your response.
"""

        response = self.llm.invoke(prompt)
        content = response.content

        # Clean up markdown artifacts
        content = content.replace("```markdown", "").replace("```", "")
        content = content.strip()

        if not content:
            raise ValueError(f"LLM returned empty content for RFP {rfp['id']}")

        return content

    def generate_cv_markdown(self, profile: dict) -> str:
        """Generate realistic CV in markdown format using LLM."""

        # Format skills with proficiency levels for the prompt
        skills_text = []
        for skill in profile['skills']:
            skills_text.append(f"{skill['name']} ({skill['proficiency']})")

        prompt = f"""
Create a professional CV in markdown format for a programmer with the following details:

Name: {profile['name']}
Email: {profile['email']}
Location: {profile['location']}
Skills: {', '.join(skills_text)}
Projects: {', '.join(profile['projects'])}
Certifications: {', '.join(profile['certifications'])}

Requirements:
1. Use proper markdown formatting (headers, lists, emphasis)
2. Create realistic content with specific details and achievements
3. Include sections like: Summary, Experience, Skills, Projects, Education, etc.
4. Make it unique and personal - vary the structure and tone
5. Add realistic company names, dates, and project descriptions
6. Include specific metrics and achievements where appropriate
7. IMPORTANT: Use the proficiency levels provided for each skill (Beginner, Intermediate, Advanced, Expert) in your skills sections

Make each CV feel authentic and written by a real person, not a template.
Use markdown syntax like # for headers, - for bullet points, **bold**, etc.
Incorporate the skill proficiency levels naturally in the CV (e.g., "Advanced Python", "Expert React developer", etc.).

IMPORTANT: Return ONLY the CV content in markdown format. Do NOT include any code block markers like ```markdown or ``` in your response.
"""

        response = self.llm.invoke(prompt)
        content = response.content

        # Clean up markdown artifacts
        content = content.replace("```markdown", "").replace("```", "")
        content = content.strip()

        if not content:
            raise ValueError(f"LLM returned empty content for {profile['name']}")

        return content

    def save_cv_as_pdf(self, markdown_content: str, filename: str, output_dir: str) -> str:
        """Convert markdown CV to PDF."""
        os.makedirs(output_dir, exist_ok=True)

        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content)

        # Professional CSS styling
        css_content = """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
        h2 { color: #34495e; margin-top: 30px; }
        h3 { color: #7f8c8d; }
        strong { color: #2c3e50; }
        ul { margin-left: 20px; }
        """

        # Generate PDF
        pdf_path = os.path.join(output_dir, f"{filename}.pdf")
        HTML(string=html_content).write_pdf(
            pdf_path,
            stylesheets=[CSS(string=css_content)]
        )

        return pdf_path

    def generate_all_data(self, num_programmers: int = 10, num_projects: int = 20, num_rfps: int = 3) -> dict:
        """Generate all data: profiles, CVs, projects, and RFPs."""
        if num_programmers <= 0:
            raise ValueError("Number of programmers must be positive")

        print(f"Generating {num_programmers} programmer profiles and CVs...")

        # Create output directories from config
        programmers_dir = self.config['output']['programmers_dir']
        rfps_dir = self.config['output']['rfps_dir']
        projects_dir = self.config['output']['projects_dir']

        os.makedirs(programmers_dir, exist_ok=True)
        os.makedirs(rfps_dir, exist_ok=True)
        os.makedirs(projects_dir, exist_ok=True)

        # Generate programmer profiles
        profiles = self.generate_programmer_profiles(num_programmers)

        # Generate CVs
        generated_cv_files = []
        for i, profile in enumerate(profiles, 1):
            print(f"Generating CV {i}/{num_programmers}: {profile['name']}")

            # Generate markdown CV
            cv_markdown = self.generate_cv_markdown(profile)

            # Save as PDF
            safe_name = profile['name'].replace(" ", "_").replace(".", "")
            filename = f"cv_{profile['id']:03d}_{safe_name}"

            file_path = self.save_cv_as_pdf(cv_markdown, filename, programmers_dir)
            generated_cv_files.append(file_path)

        # Generate projects with programmer assignments
        print(f"Generating {num_projects} project records with programmer assignments...")
        projects = self.generate_projects(num_projects, profiles)

        # Generate RFPs
        print(f"Generating {num_rfps} RFP records and PDFs...")
        rfps = self.generate_rfps(num_rfps)

        # Generate RFP PDFs
        generated_rfp_files = []
        for i, rfp in enumerate(rfps, 1):
            print(f"Generating RFP PDF {i}/{num_rfps}: {rfp['title']}")

            # Generate markdown RFP
            rfp_markdown = self.generate_rfp_markdown(rfp)

            # Save as PDF
            safe_title = rfp['title'].replace(" ", "_").replace(".", "").replace("/", "_")
            filename = f"rfp_{rfp['id']}_{safe_title}"

            file_path = self.save_cv_as_pdf(rfp_markdown, filename, rfps_dir)
            generated_rfp_files.append(file_path)

        # Save all data as JSON files in their respective directories
        profiles_path = os.path.join(programmers_dir, "programmer_profiles.json")
        with open(profiles_path, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, default=str)

        projects_path = os.path.join(projects_dir, "projects.json")
        with open(projects_path, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, default=str)

        rfps_path = os.path.join(rfps_dir, "rfps.json")
        with open(rfps_path, 'w', encoding='utf-8') as f:
            json.dump(rfps, f, indent=2, default=str)

        print(f"✅ Generated {len(generated_cv_files)} CVs in {programmers_dir}/")
        print(f"✅ Generated {len(generated_rfp_files)} RFP PDFs in {rfps_dir}/")
        print(f"✅ Saved {len(profiles)} profiles to {profiles_path}")
        print(f"✅ Saved {len(projects)} projects to {projects_path}")
        print(f"✅ Saved {len(rfps)} RFPs to {rfps_path}")

        return {
            "profiles": profiles,
            "projects": projects,
            "rfps": rfps,
            "cv_files": generated_cv_files,
            "rfp_files": generated_rfp_files,
            "profiles_file": profiles_path,
            "projects_file": projects_path,
            "rfps_file": rfps_path
        }


def main():
    """Generate data for GraphRAG demonstration."""
    try:
        generator = GraphRAGDataGenerator()
        # Load generation parameters from config
        config = generator.config['generation']
        result = generator.generate_all_data(
            config['num_programmers'],
            config['num_projects'],
            config['num_rfps']
        )

        print(f"\nGenerated files:")
        print(f"📄 CV Files:")
        for file_path in result["cv_files"]:
            print(f"  - {file_path}")

        print(f"\n📋 RFP Files:")
        for file_path in result["rfp_files"]:
            print(f"  - {file_path}")

        print(f"\n📊 Data Files:")
        print(f"  - {result['profiles_file']}")
        print(f"  - {result['projects_file']}")
        print(f"  - {result['rfps_file']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Ensure all dependencies are installed: uv sync")
        print("Ensure OPENAI_API_KEY is set in .env file")
        raise


if __name__ == "__main__":
    main()
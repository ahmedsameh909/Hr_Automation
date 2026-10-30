import random
import xml.etree.ElementTree as ET
from xml.dom import minidom
from faker import Faker

fake = Faker()

# Requisition selection choices from your Python model
SENIORITY_LEVELS = ['junior', 'mid', 'senior', 'lead']
EMPLOYMENT_TYPES = ['full_time', 'part_time', 'contract', 'freelance']
WORK_ARRANGEMENTS = ['on_site', 'remote', 'hybrid']
BUDGET_STATUSES = ['draft', 'pending', 'approved', 'rejected']
ENGLISH_LEVELS = ['beginner', 'intermediate', 'fluent', 'advanced', 'native']
AD_LANGUAGES = ['en', 'ar']

# Applicant selection choices from your Python model
APPLICANT_STATUSES = ['new', 'under_review', 'shortlisted', 'rejected', 'hired']

JOB_TITLES = [
    'Data Scientist', 'Odoo ERP Developer', 'Python Backend Engineer',
    'DevOps Specialist', 'Full Stack Developer', 'AI Automation Engineer',
    'Business Analyst', 'Database Administrator', 'QA Automation Engineer',
    'Frontend Developer (OWL/JS)', 'HR Manager', 'Talent Acquisition Lead',
    'Legal Operations Specialist', 'Financial Analyst', 'Cloud Architect',
    'Scrum Master', 'Product Manager', 'Cybersecurity Analyst',
    'Technical Support Engineer', 'UI/UX Designer'
]

DEPARTMENTS = ['Engineering', 'People & Culture', 'Product', 'Finance', 'Legal Operations', 'IT & Infrastructure']

def create_field(parent, name, text):
    field = ET.SubElement(parent, 'field', name=name)
    field.text = str(text) if text is not None else ''
    return field

def generate_xml(num_requisitions=20, applicants_per_req=10):
    odoo = ET.Element('odoo', noupdate="1")
    
    req_ids = []
    
    # 1. Generate Job Requisitions
    for i in range(1, num_requisitions + 1):
        req_xml_id = f"demo_hr_requisition_{i:03d}"
        req_ids.append(req_xml_id)
        
        title = JOB_TITLES[(i - 1) % len(JOB_TITLES)]
        min_exp = random.randint(0, 5)
        max_exp = min_exp + random.randint(2, 5)
        
        record = ET.SubElement(odoo, 'record', id=req_xml_id, model='hr.job.requisition')
        create_field(record, 'job_id', f"JOB-2026-{i:03d}")
        create_field(record, 'job_title', title)
        create_field(record, 'department_name', random.choice(DEPARTMENTS))
        create_field(record, 'recruiter_email', fake.company_email())
        create_field(record, 'seniority_level', random.choice(SENIORITY_LEVELS))
        create_field(record, 'employment_type', random.choice(EMPLOYMENT_TYPES))
        create_field(record, 'number_of_openings', random.randint(1, 5))
        create_field(record, 'reason_for_opening', random.choice(['Team expansion', 'Backfill', 'New initiative', 'Workload increase']))
        create_field(record, 'work_arrangement', random.choice(WORK_ARRANGEMENTS))
        create_field(record, 'country_name', fake.country())
        create_field(record, 'city', fake.city())
        create_field(record, 'expected_start_date', '2026-12-01')
        create_field(record, 'application_deadline', '2026-11-25')
        create_field(record, 'budget_approval_status', random.choice(BUDGET_STATUSES))
        create_field(record, 'salary_range', f"USD {random.randint(40, 120)}k - {random.randint(130, 200)}k")
        create_field(record, 'approver_name', fake.name())
        create_field(record, 'min_years_experience', min_exp)
        create_field(record, 'max_years_experience', max_exp)
        create_field(record, 'english_level', random.choice(ENGLISH_LEVELS))
        create_field(record, 'required_education', "Bachelor's degree in Computer Science or related technical field.")
        create_field(record, 'required_tools', "Python, SQL, Git, Docker, PostgreSQL")
        create_field(record, 'required_technical_skills', "System architecture, API design, database query optimization")
        create_field(record, 'required_soft_skills', "Problem solving, teamwork, cross-functional communication")
        create_field(record, 'role_summary', f"Responsible for leading core initiatives in our {title} domain.")
        create_field(record, 'key_responsibilities', "Design, build, and maintain scalable operational tools and modules.")
        create_field(record, 'advertisement_language', random.choice(AD_LANGUAGES))
        create_field(record, 'publishing_channels', "Company careers page, LinkedIn, local tech portals")
        create_field(record, 'additional_notes', "Generated demo requisition for system load testing.")

    # 2. Generate Job Applicants (10 per requisition = 200 total)
    app_counter = 1
    for req_xml_id in req_ids:
        for _ in range(applicants_per_req):
            app_xml_id = f"demo_hr_applicant_{app_counter:04d}"
            
            record = ET.SubElement(odoo, 'record', id=app_xml_id, model='hr.job.applicant')
            
            # Many2one reference to requisition
            ref_field = ET.SubElement(record, 'field', name='job_requisition_id', ref=req_xml_id)
            
            create_field(record, 'application_id', f"APP-2026-{app_counter:04d}")
            create_field(record, 'full_name', fake.name())
            create_field(record, 'email', fake.email())
            create_field(record, 'phone_number', fake.phone_number())
            create_field(record, 'location', f"{fake.city()}, {fake.country()}")
            create_field(record, 'linkedin_url', "https://www.linkedin.com/in/demo-profile")
            create_field(record, 'portfolio_url', "https://github.com/demo-applicant")
            create_field(record, 'current_job_title', fake.job())
            create_field(record, 'years_experience', round(random.uniform(0.5, 12.0), 1))
            create_field(record, 'education_level', random.choice(["B.S. Computer Science", "M.S. Data Science", "B.A. Business", "Self-Taught"]))
            create_field(record, 'english_level', random.choice(['Intermediate', 'Fluent', 'Advanced', 'Native']))
            create_field(record, 'technical_skills', "Python, SQL, Odoo ORM, PostgreSQL, Docker, Linux, Git")
            create_field(record, 'other_tools', "VS Code, n8n, Supabase, Power BI")
            create_field(record, 'years_automation_experience', round(random.uniform(0.0, 5.0), 1))
            create_field(record, 'preferred_work_arrangement', random.choice(['Remote', 'Hybrid', 'On-site']))
            create_field(record, 'earliest_start_date', '2026-11-15')
            create_field(record, 'expected_salary', f"USD {random.randint(50000, 140000)}")
            create_field(record, 'status', random.choice(APPLICANT_STATUSES))
            create_field(record, 'score', random.randint(50, 98))
            create_field(record, 'score_summary', "Strong domain background with solid technical expertise across core stacks.")
            create_field(record, 'strengths', "Fast learner, hands-on framework experience, clean code structure.")
            create_field(record, 'gaps', "Slightly less experience in enterprise legacy integration.")
            create_field(record, 'evidence', "Demonstrated through project portfolio and open source commits.")
            create_field(record, 'motivation', "Seeking to scale complex technical systems and business workflows.")
            create_field(record, 'consent', "Demonstration applicant record.")
            
            app_counter += 1

    # Pretty format XML string
    rough_string = ET.tostring(odoo, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")

    with open("hr_automation_demo.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"Successfully generated hr_automation_demo.xml with {num_requisitions} Requisitions and {app_counter - 1} Applicants.")

if __name__ == "__main__":
    generate_xml(num_requisitions=20, applicants_per_req=10)
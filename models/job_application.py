from odoo import models, fields

class HrJobRequisition(models.Model):
    _name = 'hr.job.requisition'
    _description = 'HR Job Requisition Request'
    _rec_name = 'job_id'
    _order = 'submitted_at desc'

    _sql_constraints = [
        ('hr_job_requisition_job_id_unique', 'unique(job_id)', 'Job ID must be unique.'),
    ]

    job_id = fields.Char(string='Job ID', required=True, index=True, copy=False)
    application_url = fields.Char(string='Application URL')
    submitted_at = fields.Datetime(string='Submitted At', default=fields.Datetime.now)
    job_description = fields.Text(string='Job Description')

    recruiter_email = fields.Char(string="Recruiter's Email")
    department_name = fields.Char(string='Department or Team')
    job_title = fields.Char(string='Job Title', required=True)
    alternative_job_title = fields.Char(string='Alternative Job Title')
    
    seniority_level = fields.Selection([
        ('junior', 'Junior'),
        ('mid', 'Mid-Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
    ], string='Seniority Level', default='junior')

    employment_type = fields.Selection([
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
    ], string='Employment Type', default='part_time')

    number_of_openings = fields.Integer(string='Number of Openings', default=1)
    reason_for_opening = fields.Char(string='Reason for Opening')

    work_arrangement = fields.Selection([
        ('on_site', 'On-site'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ], string='Work Arrangement', default='on_site')
    
    country_name = fields.Char(string='Country / City')
    city = fields.Char(string='City')
    expected_start_date = fields.Date(string='Expected Start Date')
    application_deadline = fields.Date(string='Application Deadline')

    budget_approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft')
    
    salary_range = fields.Char(string='Salary Range or Job Grade')
    approver_name = fields.Char(string='Approver Name or Email')

    min_years_experience = fields.Integer(string='Min Years of Experience', default=0)
    max_years_experience = fields.Integer(string='Max Years of Experience', default=0)
    additional_experience_req = fields.Text(string='Additional Experience Requirements')
    required_education = fields.Text(string='Required Education or Certifications')
    
    english_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('fluent', 'Fluent'),
        ('advanced', 'Advanced'),
        ('native', 'Native'),
    ], string='Required English Level', default='intermediate')
    
    other_languages = fields.Char(string='Other Required Languages')
    required_tools = fields.Text(string='Required Tools or Systems')

    # Technical Skills Fields
    required_technical_skills = fields.Text(string='Required Technical Skills')
    additional_technical_skills = fields.Text(string='Additional Technical Skills')
    must_have_skills = fields.Text(string='Must-have Skills')

    # Soft Skills Fields
    required_soft_skills = fields.Text(string='Required Soft Skills')
    additional_soft_skills = fields.Text(string='Additional Soft Skills')
    most_important_soft_skills = fields.Char(string='Most Important Soft Skills')
    
    role_summary = fields.Text(string='Role Summary')
    key_responsibilities = fields.Text(string='Key Responsibilities')
    additional_candidate_req = fields.Text(string='Additional Candidate Requirements')
    specific_instructions = fields.Text(string='Specific Instructions for JD')

    advertisement_language = fields.Selection([
        ('en', 'English'),
        ('ar', 'Arabic'),
    ], string='Advertisement Language', default='en')
    
    publishing_channels = fields.Text(string='Publishing Channels')
    additional_notes = fields.Text(string='Additional Notes for Recruitment Team')
    applicant_ids = fields.One2many('hr.job.applicant', 'job_requisition_id', string='Applicants')


class HrJobChannel(models.Model):
    _name = 'hr.job.channel'
    _description = 'Recruitment Publishing Channel'

    name = fields.Char(string='Channel Name', required=True)
    description = fields.Text(string='Channel Description')


class HrJobApplicant(models.Model):
    _name = 'hr.job.applicant'
    _description = 'Job Applicant'
    _rec_name = 'full_name'
    _order = 'submitted_at desc, id desc'

    _sql_constraints = [
        ('hr_job_applicant_application_id_unique', 'unique(application_id)', 'Application ID must be unique.'),
    ]

    job_requisition_id = fields.Many2one('hr.job.requisition', string='Job', required=True, ondelete='cascade', index=True)
    application_id = fields.Char(string='Application ID', copy=False, index=True)
    full_name = fields.Char(string='Full Name', required=True)
    email = fields.Char(string='Email')
    phone_number = fields.Char(string='Phone Number')
    location = fields.Char(string='City or Country')
    linkedin_url = fields.Char(string='LinkedIn Profile URL')
    portfolio_url = fields.Char(string='Portfolio or GitHub URL')
    current_job_title = fields.Char(string='Current Job Title')
    years_experience = fields.Float(string='Years of Relevant Experience')
    education_level = fields.Char(string='Highest Education Level')
    english_level = fields.Char(string='English Level')
    other_languages = fields.Char(string='Other Languages')
    technical_skills = fields.Text(string='Technical Skills')
    other_tools = fields.Text(string='Other Tools or Platforms')
    years_automation_experience = fields.Float(string='Years of Experience with Automation / AI Agents', default=0.0)
    automation_workflow_description = fields.Text(string='Describe an automation or AI workflow you built')
    live_project_url = fields.Char(string='Link to a live automation or project')

    preferred_work_arrangement = fields.Char(string='Preferred Work Arrangement')
    earliest_start_date = fields.Date(string='Earliest Available Start Date')
    expected_salary = fields.Char(string='Expected Salary')

    cv_filename = fields.Char(string='CV File Name')
    cv_url = fields.Char(string='CV URL')
    motivation = fields.Text(string='Why Interested in This Role?')
    additional_info = fields.Text(string='Anything else you would like us to know')
    consent = fields.Text(string='Consent')

    form_mode = fields.Char(string='Form Mode')
    form_url = fields.Char(string='Form URL')
    received_at = fields.Datetime(string='Received At')
    submitted_at = fields.Datetime(string='Submitted At', default=fields.Datetime.now)
    status = fields.Selection([
        ('new', 'New'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ], string='Status', default='new', required=True)

    # AI Evaluation & Scoring
    score = fields.Integer(string='AI Score', default=0)
    score_summary = fields.Text(string='AI Score Summary')
    strengths = fields.Text(string='Strengths')
    gaps = fields.Text(string='Gaps')
    evidence = fields.Text(string='Requirement Evidence')
    scored_at = fields.Datetime(string='Scored At')

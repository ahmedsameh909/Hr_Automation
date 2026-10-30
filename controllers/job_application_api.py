import json
import hmac
import logging
from datetime import datetime, timezone
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

def _is_valid_api_key(provided_key):
    configured_key = request.env['ir.config_parameter'].sudo().get_param(
        'hr_automation.api_key'
    )
    return bool(
        configured_key
        and isinstance(provided_key, str)
        and hmac.compare_digest(provided_key, configured_key)
    )

def parse_list(val):
    if isinstance(val, list):
        return ", ".join(map(str, val))
    return str(val) if val else ""

def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def parse_date(val):
    if not val:
        return False
    try:
        if isinstance(val, str):
            return val.split('T')[0]
        return val
    except Exception:
        return False

def parse_datetime(val):
    if not val:
        return False
    try:
        if isinstance(val, str):
            dt_str = val.replace('Z', '+00:00')
            dt = datetime.fromisoformat(dt_str)
            return dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        return val
    except Exception:
        try:
            return str(val)[:19].replace('T', ' ')
        except Exception:
            return False

def format_list_bullets(val):
    if isinstance(val, list):
        return "\n".join(f"• {item}" for item in val)
    return str(val) if val else ""

def format_evidence(val):
    if isinstance(val, list):
        lines = []
        for item in val:
            if isinstance(item, dict):
                req = item.get('requirement', '')
                ev = item.get('candidateEvidence', '')
                match = str(item.get('match', '')).upper()
                lines.append(f"[{match}] {req}\n  Evidence: {ev}")
            else:
                lines.append(str(item))
        return "\n\n".join(lines)
    return str(val) if val else ""

class HrJobRequisitionAPI(http.Controller):

    @http.route('/api/job_requisition/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_job_requisition(self, **kwargs):
        try:
            # 1. Parsing payload safely
            req_data = request.dispatcher.jsonrequest if hasattr(request.dispatcher, 'jsonrequest') and isinstance(request.dispatcher.jsonrequest, (dict, list)) else {}
            
            if isinstance(req_data, list) and len(req_data) > 0:
                data = req_data[0]
            elif isinstance(req_data, dict) and 'params' in req_data:
                data = req_data.get('params', {})
            elif isinstance(req_data, dict):
                data = req_data
            else:
                data = kwargs or {}

            # 2. Auth Check
            auth_header = request.httprequest.headers.get('x-api-key') or request.httprequest.headers.get('Authorization')
            token_in_params = data.get('api_key')

            if auth_header and auth_header.startswith('Bearer '):
                auth_header = auth_header.split('Bearer ')[1].strip()

            provided_key = auth_header or token_in_params

            if not _is_valid_api_key(provided_key):
                return {
                    'status': 'unauthorized',
                    'message': 'Invalid or missing API Key.'
                }

            # 3. Mandatory Fields
            job_id = data.get('job_id') or data.get('jobId') or f"JOB-REQ-{request.env['hr.job.requisition'].sudo().search_count([]) + 1}"
            job_title = data.get('job_title') or data.get('Job Title')

            if not job_title:
                return {
                    'status': 'error',
                    'message': 'Missing required field: Job Title is mandatory.'
                }

            def parse_list(val):
                if isinstance(val, list):
                    return ", ".join(map(str, val))
                return str(val) if val else ""

            def safe_int(val, default=0):
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return default

            seniority_raw = str(data.get('seniority_level') or data.get('Seniority Level', 'junior')).lower()
            seniority = 'mid' if 'mid' in seniority_raw else ('senior' if 'senior' in seniority_raw else ('lead' if 'lead' in seniority_raw else 'junior'))

            emp_type_raw = str(data.get('employment_type') or data.get('Employment Type', 'full_time')).lower().replace('-', '_').replace(' ', '_')
            emp_type = emp_type_raw if emp_type_raw in ['full_time', 'part_time', 'contract', 'freelance'] else 'full_time'

            work_arr_raw = str(data.get('work_arrangement') or data.get('Work Arrangement', 'on_site')).lower().replace('-', '_').replace(' ', '_')
            work_arr = work_arr_raw if work_arr_raw in ['on_site', 'remote', 'hybrid'] else 'on_site'

            eng_level_raw = str(data.get('english_level') or data.get('Required English Level', 'intermediate')).lower()
            eng_level = eng_level_raw if eng_level_raw in ['beginner', 'intermediate', 'fluent', 'advanced', 'native'] else 'intermediate'

            budget_status_raw = str(
                data.get('budget_approval_status')
                or data.get('budgetApprovalStatus')
                or data.get('Budget Approval Status')
                or 'draft'
            ).lower().replace('-', '_').replace(' ', '_')
            budget_status = budget_status_raw if budget_status_raw in ['draft', 'pending', 'approved', 'rejected'] else 'draft'

            vals = {
                'job_id': str(job_id),
                'job_title': str(job_title),
                'application_url': data.get('application_url') or data.get('Job Application URL') or data.get('applicationUrl'),
                'job_description': data.get('job_description') or data.get('jobDescription') or data.get('Job Description') or data.get('Job description') or data.get('description'),
                'recruiter_email': data.get('recruiter_email') or data.get("Recruiter's Email"),
                'department_name': data.get('department_name') or data.get('Department or Team'),
                'alternative_job_title': data.get('alternative_job_title') or data.get('Alternative Job Title'),
                'seniority_level': seniority,
                'employment_type': emp_type,
                'number_of_openings': safe_int(data.get('number_of_openings') or data.get('Number of Openings'), 1),
                'reason_for_opening': data.get('reason_for_opening') or data.get('Reason for Opening'),
                'work_arrangement': work_arr,
                'country_name': data.get('country_name') or data.get('City or Country'),
                'city': data.get('city') or data.get('City or Country'),
                'expected_start_date': data.get('expected_start_date') or data.get('Expected Start Date') or None,
                'application_deadline': data.get('application_deadline') or data.get('Application Deadline') or None,
                'budget_approval_status': budget_status,
                'salary_range': data.get('salary_range') or data.get('Salary Range or Job Grade'),
                'approver_name': data.get('approver_name') or data.get('Approver Name or Email'),
                'min_years_experience': safe_int(data.get('min_years_experience') or data.get('Minimum Years of Relevant Experience'), 0),
                'max_years_experience': safe_int(data.get('max_years_experience') or data.get('Maximum Years of Relevant Experience'), 0),
                'additional_experience_req': data.get('additional_experience_req') or data.get('Additional Experience Requirements'),
                'required_education': data.get('required_education') or data.get('Required Education or Certifications'),
                'english_level': eng_level,
                'other_languages': data.get('other_languages') or data.get('Other Required Languages'),
                'required_tools': data.get('required_tools') or data.get('Required Tools or Systems'),
                'required_technical_skills': parse_list(data.get('Required Technical Skills')),
                'additional_technical_skills': data.get('Additional Technical Skills'),
                'must_have_skills': data.get('Which skills are must-have?'),
                'required_soft_skills': parse_list(data.get('Required Soft Skills')),
                'additional_soft_skills': data.get('Additional Soft Skills'),
                'most_important_soft_skills': data.get('Which soft skills are most important?'),
                'role_summary': data.get('role_summary') or data.get('Role Summary'),
                'key_responsibilities': data.get('key_responsibilities') or data.get('Key Responsibilities'),
                'additional_candidate_req': data.get('additional_candidate_req') or data.get('Additional Candidate Requirements'),
                'specific_instructions': data.get('specific_instructions') or data.get('Specific Instructions for the Job Description'),
                'advertisement_language': 'en',
                'publishing_channels': parse_list(data.get('Publishing Channels')),
                'additional_notes': data.get('additional_notes') or data.get('Additional Notes for the Recruitment Team'),
            }

            # Create Record
            requisition = request.env['hr.job.requisition'].sudo().create(vals)

            return {
                'status': 'success',
                'id': requisition.id,
                'job_id': requisition.job_id,
                'job_description': requisition.job_description,
                'message': 'Job Requisition created successfully!'
            }

        except Exception as e:
            _logger.error("Error creating Job Requisition: %s", str(e), exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/job_requisition/update', type='json', auth='public', methods=['POST'], csrf=False)
    def update_job_requisition_state(self, **kwargs):
        """Update job requisition details (budget approval status, job description, etc.)."""
        req_data = request.dispatcher.jsonrequest if hasattr(request.dispatcher, 'jsonrequest') else {}
        data = req_data.get('params', req_data) if isinstance(req_data, dict) else (kwargs or {})

        auth_header = request.httprequest.headers.get('x-api-key') or request.httprequest.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            auth_header = auth_header.removeprefix('Bearer ').strip()
        if not _is_valid_api_key(auth_header or data.get('api_key')):
            return {'status': 'unauthorized', 'message': 'Invalid or missing API Key.'}

        requisition_model = request.env['hr.job.requisition'].sudo()
        record_id = data.get('id') or data.get('requisition_id')
        if record_id:
            try:
                requisition = requisition_model.browse(int(record_id)).exists()
            except (TypeError, ValueError):
                requisition = requisition_model.browse()
        else:
            job_id = data.get('job_id') or data.get('jobId')
            requisition = requisition_model.search([('job_id', '=', job_id)], limit=1) if job_id else requisition_model.browse()

        if not requisition:
            return {'status': 'not_found', 'message': 'Job requisition was not found. Provide a valid id or job_id.'}

        update_vals = {}

        # Handle budget approval status if provided
        status_input = data.get('budget_approval_status') or data.get('budgetApprovalStatus') or data.get('status')
        if status_input:
            status = str(status_input).lower().replace('-', '_').replace(' ', '_')
            valid_statuses = {'draft', 'pending', 'approved', 'rejected'}
            if status not in valid_statuses:
                return {
                    'status': 'error',
                    'message': 'budget_approval_status must be one of: draft, pending, approved, rejected.',
                }
            update_vals['budget_approval_status'] = status

        # Handle job description if provided
        job_description = (
            data.get('job_description')
            or data.get('jobDescription')
            or data.get('Job Description')
            or data.get('Job description')
            or data.get('description')
        )
        if job_description is not None:
            update_vals['job_description'] = job_description

        # Handle application URL if provided
        app_url = data.get('application_url') or data.get('applicationUrl') or data.get('Job Application URL')
        if app_url is not None:
            update_vals['application_url'] = app_url

        if not update_vals:
            return {
                'status': 'error',
                'message': 'No valid fields provided to update (e.g. job_description or budget_approval_status).'
            }

        requisition.write(update_vals)
        return {
            'status': 'success',
            'id': requisition.id,
            'job_id': requisition.job_id,
            'budget_approval_status': requisition.budget_approval_status,
            'job_description': requisition.job_description,
            'message': 'Job requisition updated successfully.',
        }

    @http.route('/api/job_applicant/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_job_applicant(self, **kwargs):
        """Create an applicant linked to an approved job requisition (supports raw JSON, arrays, and JSON-RPC)."""
        try:
            req_data = {}
            raw_body = request.httprequest.get_data()
            if raw_body:
                try:
                    req_data = json.loads(raw_body.decode('utf-8'))
                except Exception:
                    req_data = {}

            if isinstance(req_data, list) and len(req_data) > 0:
                data = req_data[0]
            elif isinstance(req_data, dict) and 'params' in req_data:
                params = req_data.get('params')
                if isinstance(params, list) and len(params) > 0:
                    data = params[0]
                elif isinstance(params, dict):
                    data = params
                else:
                    data = req_data
            elif isinstance(req_data, dict):
                data = req_data
            else:
                data = kwargs or {}

            auth_header = request.httprequest.headers.get('x-api-key') or request.httprequest.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                auth_header = auth_header.removeprefix('Bearer ').strip()

            api_key = auth_header or data.get('api_key') or request.params.get('api_key') or kwargs.get('api_key')
            if not _is_valid_api_key(api_key):
                return request.make_json_response({
                    'status': 'unauthorized',
                    'message': 'Invalid or missing API Key.'
                }, status=401)

            job_id = data.get('job_id') or data.get('jobId')
            job = request.env['hr.job.requisition'].sudo().search([('job_id', '=', job_id)], limit=1)
            if not job:
                return request.make_json_response({
                    'status': 'not_found',
                    'message': f"No job was found for jobId: {job_id}"
                }, status=404)
            if job.budget_approval_status != 'approved':
                return request.make_json_response({
                    'status': 'not_available',
                    'message': 'Applications are accepted only for approved jobs.'
                }, status=400)

            full_name = data.get('full_name') or data.get('fullName') or data.get('Full Name')
            if not full_name:
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Missing required field: Full Name.'
                }, status=400)

            cv_data = data.get('Upload your CV') or {}
            raw_status = str(data.get('status') or 'new').lower().replace('-', '_').replace(' ', '_')
            status = raw_status if raw_status in {'new', 'under_review', 'shortlisted', 'rejected', 'hired'} else 'new'

            vals = {
                'job_requisition_id': job.id,
                'application_id': data.get('application_id') or data.get('applicationId') or False,
                'full_name': full_name,
                'email': data.get('email') or data.get('Email'),
                'phone_number': data.get('phone_number') or data.get('phoneNumber') or data.get('Phone Number'),
                'location': data.get('location') or data.get('City or Country'),
                'linkedin_url': data.get('linkedin_url') or data.get('LinkedIn Profile URL'),
                'portfolio_url': data.get('portfolio_url') or data.get('Portfolio or GitHub URL'),
                'current_job_title': data.get('current_job_title') or data.get('Current Job Title'),
                'years_experience': safe_float(data.get('years_experience') or data.get('Years of Relevant Experience')),
                'education_level': data.get('education_level') or data.get('Highest Education Level'),
                'english_level': data.get('english_level') or data.get('English Level'),
                'other_languages': data.get('other_languages') or data.get('Other Languages'),
                'preferred_work_arrangement': data.get('preferred_work_arrangement') or data.get('Preferred Work Arrangement'),
                'earliest_start_date': parse_date(data.get('earliest_start_date') or data.get('Earliest Available Start Date')),
                'expected_salary': data.get('expected_salary') or data.get('Expected Salary'),
                'technical_skills': parse_list(data.get('technical_skills') or data.get('Technical Skills')),
                'other_tools': data.get('other_tools') or data.get('Other Tools or Platforms'),
                'years_automation_experience': safe_float(data.get('years_automation_experience') or data.get('Years of Experience with Automation or AI Agents')),
                'automation_workflow_description': data.get('automation_workflow_description') or data.get('Describe an automation or AI workflow you built'),
                'live_project_url': data.get('live_project_url') or data.get('Link to a live automation or project'),
                'cv_filename': cv_data.get('filename') if isinstance(cv_data, dict) else (data.get('cvFileName') or data.get('cv_filename')),
                'cv_url': data.get('Cv_Url') or data.get('cv_url') or data.get('cvUrl'),
                'motivation': data.get('motivation') or data.get('Why are you interested in this role?'),
                'additional_info': data.get('additional_info') or data.get('Anything else you would like us to know'),
                'consent': parse_list(data.get('consent') or data.get('Consent')),
                'form_mode': data.get('form_mode') or data.get('formMode'),
                'form_url': data.get('form_url') or data.get('formUrl'),
                'submitted_at': parse_datetime(data.get('submitted_at') or data.get('submittedAt')),
                'received_at': parse_datetime(data.get('received_at') or data.get('receivedAt')),
                'status': status,
                # AI Scoring
                'score': safe_int(data.get('score')),
                'score_summary': data.get('scoreSummary') or data.get('score_summary'),
                'strengths': format_list_bullets(data.get('strengths')),
                'gaps': format_list_bullets(data.get('gaps')),
                'evidence': format_evidence(data.get('evidence')),
                'scored_at': parse_datetime(data.get('scoredAt') or data.get('scored_at')),
            }

            applicant = request.env['hr.job.applicant'].sudo().create(vals)

            return request.make_json_response({
                'status': 'success',
                'id': applicant.id,
                'application_id': applicant.application_id,
                'job_id': job.job_id,
                'full_name': applicant.full_name,
                'score': applicant.score,
                'status': applicant.status,
                'message': 'Applicant created successfully.',
            }, status=200)

        except Exception as error:
            _logger.exception('Error creating applicant')
            return request.make_json_response({'status': 'error', 'message': str(error)}, status=500)

    @http.route('/api/job_applicant/update', type='http', auth='public', methods=['POST'], csrf=False)
    def update_job_applicant(self, **kwargs):
        """Update an applicant's status, details, or AI scoring (supports raw JSON, arrays, and JSON-RPC)."""
        try:
            req_data = {}
            raw_body = request.httprequest.get_data()
            if raw_body:
                try:
                    req_data = json.loads(raw_body.decode('utf-8'))
                except Exception:
                    req_data = {}

            if isinstance(req_data, list) and len(req_data) > 0:
                data = req_data[0]
            elif isinstance(req_data, dict) and 'params' in req_data:
                params = req_data.get('params')
                if isinstance(params, list) and len(params) > 0:
                    data = params[0]
                elif isinstance(params, dict):
                    data = params
                else:
                    data = req_data
            elif isinstance(req_data, dict):
                data = req_data
            else:
                data = kwargs or {}

            auth_header = request.httprequest.headers.get('x-api-key') or request.httprequest.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                auth_header = auth_header.removeprefix('Bearer ').strip()

            api_key = auth_header or data.get('api_key') or request.params.get('api_key') or kwargs.get('api_key')
            if not _is_valid_api_key(api_key):
                return request.make_json_response({
                    'status': 'unauthorized',
                    'message': 'Invalid or missing API Key.'
                }, status=401)

            applicant_model = request.env['hr.job.applicant'].sudo()
            record_id = data.get('id') or data.get('applicant_id')
            app_id = data.get('application_id') or data.get('applicationId')
            job_id = data.get('job_id') or data.get('jobId')

            applicant = False
            if record_id:
                try:
                    applicant = applicant_model.browse(int(record_id)).exists()
                except (TypeError, ValueError):
                    applicant = False

            if not applicant and app_id:
                domain = [('application_id', '=', app_id)]
                if job_id:
                    domain.append(('job_requisition_id.job_id', '=', job_id))
                applicant = applicant_model.search(domain, limit=1)
                if not applicant:
                    applicant = applicant_model.search([('application_id', '=', app_id)], limit=1)

            if not applicant and job_id:
                applicant = applicant_model.search([('job_requisition_id.job_id', '=', job_id)], limit=1)

            if not applicant:
                return request.make_json_response({
                    'status': 'not_found',
                    'message': f"Applicant was not found for application_id: '{app_id}' or job_id: '{job_id}'."
                }, status=404)

            update_vals = {}
            status_in = data.get('status')
            if status_in:
                raw_status = str(status_in).lower().replace('-', '_').replace(' ', '_')
                valid_statuses = {'new', 'under_review', 'shortlisted', 'rejected', 'hired'}
                if raw_status in valid_statuses:
                    update_vals['status'] = raw_status

            # AI Scoring updates
            if 'score' in data and data['score'] is not None:
                update_vals['score'] = safe_int(data['score'])

            if 'scoreSummary' in data or 'score_summary' in data:
                update_vals['score_summary'] = data.get('scoreSummary') or data.get('score_summary')

            if 'strengths' in data and data['strengths'] is not None:
                update_vals['strengths'] = format_list_bullets(data['strengths'])

            if 'gaps' in data and data['gaps'] is not None:
                update_vals['gaps'] = format_list_bullets(data['gaps'])

            if 'evidence' in data and data['evidence'] is not None:
                update_vals['evidence'] = format_evidence(data['evidence'])

            if 'scoredAt' in data or 'scored_at' in data:
                update_vals['scored_at'] = parse_datetime(data.get('scoredAt') or data.get('scored_at'))

            field_mappings = [
                ('full_name', ['full_name', 'fullName', 'Full Name']),
                ('email', ['email', 'Email']),
                ('phone_number', ['phone_number', 'phoneNumber', 'Phone Number']),
                ('location', ['location', 'City or Country']),
                ('linkedin_url', ['linkedin_url', 'LinkedIn Profile URL']),
                ('portfolio_url', ['portfolio_url', 'Portfolio or GitHub URL']),
                ('current_job_title', ['current_job_title', 'Current Job Title']),
                ('education_level', ['education_level', 'Highest Education Level']),
                ('english_level', ['english_level', 'English Level']),
                ('other_languages', ['other_languages', 'Other Languages']),
                ('preferred_work_arrangement', ['preferred_work_arrangement', 'Preferred Work Arrangement']),
                ('expected_salary', ['expected_salary', 'Expected Salary']),
                ('other_tools', ['other_tools', 'Other Tools or Platforms']),
                ('automation_workflow_description', ['automation_workflow_description', 'Describe an automation or AI workflow you built']),
                ('live_project_url', ['live_project_url', 'Link to a live automation or project']),
                ('cv_url', ['cv_url', 'Cv_Url', 'cvUrl']),
                ('motivation', ['motivation', 'Why are you interested in this role?']),
                ('additional_info', ['additional_info', 'Anything else you would like us to know']),
            ]

            for model_field, keys in field_mappings:
                for k in keys:
                    if k in data and data[k] is not None:
                        update_vals[model_field] = data[k]
                        break

            if 'years_experience' in data or 'Years of Relevant Experience' in data:
                update_vals['years_experience'] = safe_float(data.get('years_experience') or data.get('Years of Relevant Experience'))

            if 'years_automation_experience' in data or 'Years of Experience with Automation or AI Agents' in data:
                update_vals['years_automation_experience'] = safe_float(data.get('years_automation_experience') or data.get('Years of Experience with Automation or AI Agents'))

            if 'technical_skills' in data or 'Technical Skills' in data:
                update_vals['technical_skills'] = parse_list(data.get('technical_skills') or data.get('Technical Skills'))

            if not update_vals:
                return request.make_json_response({
                    'status': 'error',
                    'message': 'No valid fields provided to update.'
                }, status=400)

            applicant.write(update_vals)
            return request.make_json_response({
                'status': 'success',
                'id': applicant.id,
                'application_id': applicant.application_id,
                'job_id': applicant.job_requisition_id.job_id,
                'status': applicant.status,
                'score': applicant.score,
                'message': 'Applicant updated successfully.',
            }, status=200)

        except Exception as error:
            _logger.exception('Error updating applicant')
            return request.make_json_response({'status': 'error', 'message': str(error)}, status=500)

    @http.route([
        '/api/job_requisition/description',
        '/api/job_requisition/<string:job_id>/description',
        '/api/job_requisition/get',
        '/api/job_requisition/get_description'
    ], type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def get_job_description(self, job_id=None, **kwargs):
        """Endpoint to retrieve job description and details (supports GET/POST and query/json params)."""
        try:
            # 1. Parse body if JSON was sent
            body_data = {}
            try:
                raw_body = request.httprequest.get_data()
                if raw_body:
                    parsed = json.loads(raw_body.decode('utf-8'))
                    if isinstance(parsed, dict):
                        body_data = parsed.get('params', parsed) if isinstance(parsed.get('params'), dict) else parsed
            except Exception:
                pass

            # 2. Auth check
            auth_header = request.httprequest.headers.get('x-api-key') or request.httprequest.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                auth_header = auth_header.removeprefix('Bearer ').strip()

            api_key = (
                auth_header
                or request.params.get('api_key')
                or body_data.get('api_key')
                or kwargs.get('api_key')
            )
            if not _is_valid_api_key(api_key):
                return request.make_json_response({
                    'status': 'unauthorized',
                    'message': 'Invalid or missing API Key. Please provide api_key in body or params or x-api-key in headers.'
                }, status=401)

            # 3. Locate requisition
            record_id = (
                request.params.get('id')
                or body_data.get('id')
                or body_data.get('requisition_id')
                or kwargs.get('id')
            )
            target_job_id = (
                job_id
                or request.params.get('job_id')
                or body_data.get('job_id')
                or body_data.get('jobId')
                or kwargs.get('job_id')
            )

            requisition_model = request.env['hr.job.requisition'].sudo()
            if record_id:
                try:
                    requisition = requisition_model.browse(int(record_id)).exists()
                except (TypeError, ValueError):
                    requisition = requisition_model.browse()
            elif target_job_id:
                requisition = requisition_model.search([('job_id', '=', str(target_job_id))], limit=1)
            else:
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Missing parameter: Please provide job_id or id.'
                }, status=400)

            if not requisition:
                return request.make_json_response({
                    'status': 'not_found',
                    'message': f"Job requisition '{target_job_id or record_id}' was not found."
                }, status=404)

            return request.make_json_response({
                'status': 'success',
                'id': requisition.id,
                'job_id': requisition.job_id,
                'job_title': requisition.job_title,
                'budget_approval_status': requisition.budget_approval_status,
                'job_description': requisition.job_description or '',
                'application_url': requisition.application_url or ''
            }, status=200)

        except Exception as e:
            _logger.error("Error retrieving Job Description: %s", str(e), exc_info=True)
            return request.make_json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)

    @http.route([
        '/api/job_requisition/<string:job_id>/applicants',
        '/api/job_applicant/list',
        '/api/job_applicants'
    ], type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def get_job_applicants(self, job_id=None, **kwargs):
        """Retrieve all applicants for a specific job requisition."""
        try:
            body_data = {}
            raw_body = request.httprequest.get_data()
            if raw_body:
                try:
                    parsed = json.loads(raw_body.decode('utf-8'))
                    if isinstance(parsed, dict):
                        body_data = parsed.get('params', parsed) if isinstance(parsed.get('params'), dict) else parsed
                except Exception:
                    pass

            auth_header = request.httprequest.headers.get('x-api-key') or request.httprequest.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                auth_header = auth_header.removeprefix('Bearer ').strip()

            api_key = (
                auth_header
                or request.params.get('api_key')
                or body_data.get('api_key')
                or kwargs.get('api_key')
            )
            if not _is_valid_api_key(api_key):
                return request.make_json_response({
                    'status': 'unauthorized',
                    'message': 'Invalid or missing API Key.'
                }, status=401)

            target_job_id = (
                job_id
                or request.params.get('job_id')
                or request.params.get('jobId')
                or body_data.get('job_id')
                or body_data.get('jobId')
                or kwargs.get('job_id')
            )
            record_id = (
                request.params.get('id')
                or body_data.get('id')
                or kwargs.get('id')
            )

            job_model = request.env['hr.job.requisition'].sudo()
            job = False
            if record_id:
                try:
                    job = job_model.browse(int(record_id)).exists()
                except (TypeError, ValueError):
                    job = False
            elif target_job_id:
                job = job_model.search([('job_id', '=', str(target_job_id))], limit=1)
            else:
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Missing parameter: Please provide job_id (or jobId).'
                }, status=400)

            if not job:
                return request.make_json_response({
                    'status': 'not_found',
                    'message': f"Job requisition '{target_job_id or record_id}' was not found."
                }, status=404)

            # Optional status filter
            filter_status = request.params.get('status') or body_data.get('status') or kwargs.get('status')
            applicant_domain = [('job_requisition_id', '=', job.id)]
            if filter_status:
                applicant_domain.append(('status', '=', str(filter_status).lower().replace('-', '_').replace(' ', '_')))

            applicants = request.env['hr.job.applicant'].sudo().search(
                applicant_domain,
                order='score desc, submitted_at desc, id desc'
            )

            applicant_list = []
            for app in applicants:
                applicant_list.append({
                    'id': app.id,
                    'application_id': app.application_id,
                    'full_name': app.full_name,
                    'email': app.email,
                    'phone_number': app.phone_number,
                    'location': app.location,
                    'linkedin_url': app.linkedin_url,
                    'portfolio_url': app.portfolio_url,
                    'current_job_title': app.current_job_title,
                    'years_experience': app.years_experience,
                    'years_automation_experience': app.years_automation_experience,
                    'education_level': app.education_level,
                    'english_level': app.english_level,
                    'other_languages': app.other_languages,
                    'preferred_work_arrangement': app.preferred_work_arrangement,
                    'earliest_start_date': app.earliest_start_date.isoformat() if app.earliest_start_date else None,
                    'expected_salary': app.expected_salary,
                    'technical_skills': app.technical_skills,
                    'other_tools': app.other_tools,
                    'automation_workflow_description': app.automation_workflow_description,
                    'live_project_url': app.live_project_url,
                    'cv_filename': app.cv_filename,
                    'cv_url': app.cv_url,
                    'motivation': app.motivation,
                    'additional_info': app.additional_info,
                    'consent': app.consent,
                    'form_mode': app.form_mode,
                    'form_url': app.form_url,
                    'status': app.status,
                    'score': app.score,
                    'score_summary': app.score_summary,
                    'strengths': app.strengths,
                    'gaps': app.gaps,
                    'evidence': app.evidence,
                    'submitted_at': app.submitted_at.isoformat() if app.submitted_at else None,
                    'received_at': app.received_at.isoformat() if app.received_at else None,
                    'scored_at': app.scored_at.isoformat() if app.scored_at else None,
                })

            return request.make_json_response({
                'status': 'success',
                'job_id': job.job_id,
                'job_title': job.job_title,
                'budget_approval_status': job.budget_approval_status,
                'total_applicants': len(applicant_list),
                'applicants': applicant_list
            }, status=200)

        except Exception as e:
            _logger.error("Error retrieving applicants: %s", str(e), exc_info=True)
            return request.make_json_response({'status': 'error', 'message': str(e)}, status=500)

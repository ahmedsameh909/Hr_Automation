# Odoo 18 HR Automation Module (`hr_automation`)

`hr_automation` is a custom Odoo 18 addon designed to streamline recruitment workflows by seamlessly connecting external form submissions and AI-driven automation pipelines (such as n8n, Make, or custom webhooks) directly to Odoo.

## 🚀 Key Features

- **Job Requisitions Management (`hr.job.requisition`)**: Dynamic tracking of hiring requests, budget approvals, required skill sets, and publishing configurations.
- **Applicant Intake Pipeline (`hr.job.applicant`)**: Automated capturing and mapping of candidate profiles, CV filenames, experience metrics, and portfolio links directly to job requisitions.
- **JSON-RPC / REST API Integration**: Secure controllers receiving payloads from external webhooks via custom API key authentication (`x-api-key`).
- **Flexible Payload Normalization**: Built-in parsers handling raw arrays, lists, multi-format JSON, and multi-database contexts.

## 🧰 Tech Stack & Environment

- **Platform**: Odoo 18 Enterprise / Community
- **Architecture**: Docker Compose (`odoo18_web`, `odoo18_db`)
- **Integration Layer**: n8n, Postman, ngrok reverse tunneling
- **Language**: Python 3.12, PostgreSQL

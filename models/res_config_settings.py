from odoo import fields, models


class HrAutomationConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_automation_api_key = fields.Char(
        string='API Key',
        config_parameter='hr_automation.api_key',
        groups='base.group_system',
    )

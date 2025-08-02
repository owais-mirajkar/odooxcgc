from odoo import models, fields

# Role progression mapping
ROLE_PROGRESSION = {
    'user': 'support_agent',
    'support_agent': 'admin',
    'admin': 'admin'  # No further upgrades
}

class ResUser(models.Model):
    _inherit = 'res.users'

    category_ids = fields.Many2many('quickdesk.category', string='Categories')
    role = fields.Selection([
        ('user', 'User'),
        ('support_agent', 'Support Agent'),
        ('admin', 'Admin')
    ], default='user')
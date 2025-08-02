from odoo import models, fields

class ResUser(models.Model):
    _inherit = 'res.users'

    category_ids = fields.Many2many('quickdesk.category', string='Categories')
    role = fields.Selection([
        ('user', 'User'),
        ('support_agent', 'Support Agent'),
        ('admin', 'Admin')
    ], default='user')
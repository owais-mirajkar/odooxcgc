from odoo import models, fields

class Category(models.Model):
    _name = 'quickdesk.category'
    _description = 'Ticket Category'
    
    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    team_id = fields.Many2one('quickdesk.team', string='Support Team')
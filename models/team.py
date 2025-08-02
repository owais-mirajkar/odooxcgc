from odoo import models, fields

class Team(models.Model):
    _name = 'quickdesk.team'
    _description = 'Support Team'
    
    name = fields.Char(required=True)
    member_ids = fields.Many2many('res.users', string='Team Members')
    category_ids = fields.One2many('quickdesk.category', 'team_id', string='Categories')
    color = fields.Integer(string='Color Index')
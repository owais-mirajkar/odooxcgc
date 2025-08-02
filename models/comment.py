from odoo import models, fields

class Comment(models.Model):
    _name = 'quickdesk.comment'
    _description = 'Ticket Comment'
    _order = 'create_date desc'
    
    ticket_id = fields.Many2one('quickdesk.ticket', string='Ticket', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Author', default=lambda self: self.env.user)
    content = fields.Html(string='Content', required=True)
    is_internal = fields.Boolean(string='Internal Note')
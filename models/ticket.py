from odoo import models, fields, api

class Ticket(models.Model):
    _name = 'quickdesk.ticket'
    _description = 'Support Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Subject', required=True)
    description = fields.Html(string='Description')
    number = fields.Char(string='Ticket Number', readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('quickdesk.ticket'))
    category_id = fields.Many2one('quickdesk.category', string='Category')
    team_id = fields.Many2one('quickdesk.team', string='Support Team')
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Customer')
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Critical')], string='Priority')
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')], string='Status', default='new', tracking=True)
    upvotes = fields.Integer(string='Upvotes', default=0)
    downvotes = fields.Integer(string='Downvotes', default=0)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'quickdesk.ticket')], string='Attachments')
    color = fields.Integer(string='Color Index')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    def action_upvote(self):
        self.upvotes += 1
        
    def action_downvote(self):
        self.downvotes += 1
        
    def action_assign_to_me(self):
        self.assigned_to = self.env.user
        
    def action_set_in_progress(self):
        self.state = 'in_progress'
        
    def action_set_resolved(self):
        self.state = 'resolved'
        
    def action_set_closed(self):
        self.state = 'closed'
        
    def action_reopen(self):
        self.state = 'new'
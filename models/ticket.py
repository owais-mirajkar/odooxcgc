from odoo import models, fields, api

class Ticket(models.Model):
    _name = 'quickdesk.ticket'
    _description = 'Support Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Subject', required=True)
    description = fields.Html(string='Description')
    number = fields.Char(string='Ticket Number', readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('quickdesk.ticket'))
    category_ids = fields.Many2many('quickdesk.category', string='Categories')
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
    comment_ids = fields.One2many('quickdesk.comment', 'ticket_id', string='Comments')
    
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
    
    @api.model
    def create(self, vals):
        ticket = super(Ticket, self).create(vals)
        ticket._assign_first_team_member()
        return ticket

    def write(self, vals):
        res = super(Ticket, self).write(vals)
        if 'category_ids' in vals:
            for ticket in self:
                ticket._assign_first_team_member()
        return res

    def _assign_first_team_member(self):
        """Assign the first available team member from the category's team."""
        if self.category_ids:
            first_category = self.category_ids[0]
            team = first_category.team_id
            if team and team.member_ids:
                self.assigned_to = team.member_ids[0]

    
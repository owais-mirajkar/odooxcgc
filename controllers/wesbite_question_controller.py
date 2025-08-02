from odoo import http
from odoo.http import request

class WebsiteTicketController(http.Controller):

    @http.route(['/ask'], type='http', auth='user', website=True)
    def ask_ticket(self, **kw):
        categories = request.env['quickdesk.category'].sudo().search([])
        return request.render('quickdesk.ask_ticket_template', {
            'categories': categories,
        })

    @http.route(['/submit/ticket'], type='http', auth='user', website=True, csrf=True)
    def submit_ticket(self, **post):
        category_ids = request.httprequest.form.getlist('category_ids')
        ticket_vals = {
            'number': request.env['ir.sequence'].sudo().next_by_code('quickdesk.ticket'),
            'name': post.get('question'),
            'description': post.get('description'),
            'category_ids': [(6, 0, list(map(int, category_ids)))],
            'partner_id': request.env.user.partner_id.id,
            'user_id': request.env.user.id,
        }
        request.env['quickdesk.ticket'].sudo().create(ticket_vals)
        return request.redirect('/my')


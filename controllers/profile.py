from odoo import http
from odoo.addons.portal.controllers import portal
from odoo.http import request, route

class QuickDeskProfile(http.Controller):

    def _prepare_portal_layout_values(self):
        user = request.env.user
        category = request.env['quickdesk.category'].search([])
        role = user.role
        language = user.lang
        return {
            'user_name': user.name,
            'categories': category,
            'role_option': role,
            'language_option': language,
            'page_name': 'home',
        }
        
    @http.route('/my/profile', auth='user', website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        return request.render("quickdesk.custom_profile_template", values)

    @http.route('/my/upgrade_role', type='http', auth="user", website=True)
    def request_role_upgrade(self, requested_role, **post):
        user = request.env.user
        
        if requested_role not in ['support_agent', 'admin']:
            return request.redirect('/my?error=Invalid+role+request')
        
        if user.role_upgrade_request == 'pending':
            return request.redirect('/my?error=You+already+have+a+pending+request')
        
        user.write({
            'role_upgrade_request': 'pending',
            'requested_role': requested_role
        })
        
        self._send_approval_request(user, requested_role)
        
        return request.redirect('/my?success=Upgrade+request+submitted')

    def _send_approval_request(self, user, requested_role):
        template = request.env.ref('quickdesk.email_template_role_approval_request')
        manager_group = request.env.ref('base.group_erp_manager')
        managers = request.env['res.users'].search([('groups_id', 'in', manager_group.ids)])
        
        for manager in managers:
            template.with_context({
                'requesting_user': user,
                'requested_role': requested_role,
                'approval_url': f"{request.httprequest.host_url}my/approve_role_upgrade/{user.id}"
            }).send_mail(manager.id, force_send=True)
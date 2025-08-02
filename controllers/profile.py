from odoo import http
from odoo.addons.portal.controllers import portal
from odoo.http import request, route

class QuickDeskProfile(http.Controller):

    def _prepare_portal_layout_values(self):
        user = request.env.user
        category = request.env['quickdesk.category'].search([])
        return {
            'user_name': user.name,
            'categories': category,
            'page_name': 'home',
        }
        
    @http.route('/my/profile', auth='user', website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        return request.render("quickdesk.custom_profile_template", values)

    @route('/my/upgrade_role', type='json', auth="user")
    def upgrade_role(self, **post):
        user = request.env.user
        current_role = user.role
        role_level = user.role_level or 1
        
        # Define your role upgrade path
        role_mapping = {
            1: "Basic User",
            2: "Advanced User",
            3: "Premium User", 
            4: "Admin"
        }
        
        if role_level < len(role_mapping):
            user.write({
                'role_level': role_level + 1,
                'role': role_mapping.get(role_level + 1)
            })
            return {
                'success': True,
                'new_role': user.role,
                'message': 'Role upgraded successfully!'
            }
        else:
            return {
                'success': False,
                'message': 'You already have the highest role!'
            }
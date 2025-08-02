# -*- coding: utf-8 -*-
# from odoo import http


# class QuickDesk(http.Controller):
#     @http.route('/quick_desk/quick_desk', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/quick_desk/quick_desk/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('quick_desk.listing', {
#             'root': '/quick_desk/quick_desk',
#             'objects': http.request.env['quick_desk.quick_desk'].search([]),
#         })

#     @http.route('/quick_desk/quick_desk/objects/<model("quick_desk.quick_desk"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('quick_desk.object', {
#             'object': obj
#         })


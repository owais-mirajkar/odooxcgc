# -*- coding: utf-8 -*-
from odoo.addons.portal.controllers import portal
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import pager as portal_pager
from operator import itemgetter
from odoo.http import request
from odoo.tools.translate import _
from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.osv.expression import AND, OR
from odoo.exceptions import AccessError, MissingError
import json
from collections import defaultdict


class QuickDesk(portal.CustomerPortal):
    def _ticket_get_page_view_values(self, ticket, access_token, **kwargs):
        values = {
            'page_name': 'ticket',
            'ticket': ticket,
            'ticket_link_section': [],
            'ticket_closed': ticket.state in ('resolved', 'closed'),
            'preview_object': ticket,
        }
        return self._get_page_view_values(ticket, access_token, values, 'my_tickets_history', False, **kwargs)
    
    def _ticket_get_searchbar_inputs(self):
        return {
            'name': {'input': 'name', 'label': _('Search in Subject')},
            'number': {'input': 'number', 'label': _('Search in Ticket Number')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

    def _ticket_get_searchbar_groupby(self):
        return {
            'none': {'label': _('None')},
            'category_id': {'label': _('Category')},
            'assigned_to': {'label': _('Assigned to')},
            'state': {'label': _('Status')},
            'priority': {'label': _('Priority')},
        }
    
    def _ticket_get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('name', 'all'):
            search_domain.append([('name', 'ilike', search)])
        if search_in in ('number', 'all'):
            search_domain.append([('number', 'ilike', search)])
        return OR(search_domain) if search_domain else []

    def _prepare_my_quick_tickets_values(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, groupby='none', search_in='all'):
        values = self._prepare_portal_layout_values()
        
        # Base domain to show only current user's tickets
        domain = [('user_id', '=', request.env.user.id)]

        searchbar_sortings = {
            'create_date desc': {'label': _('Newest')},
            'name': {'label': _('Subject')},
            'state': {'label': _('Status')},
            'priority': {'label': _('Priority')},
            'assigned_to': {'label': _('Assigned to')},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'assigned': {'label': _('Assigned'), 'domain': [('assigned_to', '!=', False)]},
            'unassigned': {'label': _('Unassigned'), 'domain': [('assigned_to', '=', False)]},
            'open': {'label': _('Open'), 'domain': [('state', 'in', ['new', 'in_progress'])]},
            'closed': {'label': _('Closed'), 'domain': [('state', 'in', ['resolved', 'closed'])]},
        }
        
        searchbar_inputs = self._ticket_get_searchbar_inputs()
        searchbar_groupby = self._ticket_get_searchbar_groupby()

        # default sort by value
        if not sortby:
            sortby = 'create_date desc'

        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if date_begin and date_end:
            domain = AND([domain, [('create_date', '>', date_begin), ('create_date', '<=', date_end)]])

        # search
        if search and search_in:
            search_domain = self._ticket_get_search_domain(search_in, search)
            if search_domain:
                domain = AND([domain, search_domain])

        # Use the correct model name - should match your model definition
        ticket_model = 'quickdesk.ticket'
        
        # pager
        tickets_count = request.env[ticket_model].search_count(domain)
        pager = portal_pager(
            url="/my/quickdesk/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby, 'filterby': filterby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        order = f'{groupby}, {sortby}' if groupby != 'none' else sortby
        tickets = request.env[ticket_model].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        if not tickets:
            grouped_tickets = []
        elif groupby != 'none':
            grouped_tickets = [request.env[ticket_model].concat(*g) for k, g in groupbyelem(tickets, itemgetter(groupby))]
        else:
            grouped_tickets = [tickets]

        values.update({
            'date': date_begin,
            'grouped_tickets': grouped_tickets,
            'page_name': 'ticket',
            'default_url': '/my/quickdesk/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
            'filterby': filterby,
        })
        return values
    
    @route(['/my', '/my/home', '/my/quickdesk/tickets', '/my/quickdesk/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def home(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, groupby='none', search_in='name', **kw):
        values = self._prepare_my_quick_tickets_values(page, date_begin, date_end, sortby, filterby, search, groupby, search_in)
        return request.render("quickdesk.quick_portal_helpdesk_ticket", values)

    # Add individual ticket view
    @route(['/my/quickdesk/tickets/<int:ticket_id>'], type='http', auth="user", website=True)
    def portal_ticket_detail(self, ticket_id, access_token=None, **kw):
        try:
            # Check if user can access this specific ticket
            ticket = request.env['quickdesk.ticket'].browse(ticket_id)
            ticket.check_access_rights('read')
            ticket.check_access_rule('read')
            
            # Double check that this ticket belongs to the current user (for portal users)
            if request.env.user.has_group('base.group_portal'):
                if ticket.user_id.id != request.env.user.id:
                    return request.redirect('/my')
            
            values = self._ticket_get_page_view_values(ticket, access_token, **kw)
            values['ticket_closed'] = kw.get('ticket_closed', False)
            return request.render("quickdesk.portal_ticket_detail", values)
        except (AccessError, MissingError):
            return request.redirect('/my')
    
    # Add route for closing tickets
    @route(['/my/quickdesk/tickets/<int:ticket_id>/close'], type='http', auth="user", website=True)
    def portal_ticket_close(self, ticket_id, **kw):
        try:
            ticket = request.env['quickdesk.ticket'].browse(ticket_id)
            ticket.check_access_rights('write')
            ticket.check_access_rule('write')
            
            # Check if user owns this ticket (for portal users)
            if request.env.user.has_group('base.group_portal'):
                if ticket.user_id.id != request.env.user.id:
                    return request.redirect('/my')
            
            # Close the ticket
            ticket.write({'state': 'closed'})
            
            # Redirect back to ticket detail with success message
            return request.redirect(f'/my/quickdesk/tickets/{ticket_id}?ticket_closed=1')
        except (AccessError, MissingError):
            return request.redirect('/my')

    @route('/my/quickdesk/dashboard/<int:user_id>', type='http', auth='user', website=True)
    def render_graph_template(self, user_id, **kwargs):
        env = request.env

        # 1. Tickets by User
        user_ticket_data = env['quickdesk.ticket'].sudo().read_group(
            [('user_id', '!=', False),  ('user_id', '=', user_id)],
            ['user_id'],
            ['user_id']
        )
        user_data = [(rec['user_id'][1], rec['user_id_count']) for rec in user_ticket_data]

        # 2. Comments Count per Ticket
        comment_data = env['quickdesk.ticket'].sudo().search_read(
            [('user_id', '=', user_id)], ['number', 'comments_count']
        )

        # 3. Tickets by Category
        tickets = env['quickdesk.ticket'].sudo().search([('user_id', '=', user_id)])

        category_counter = defaultdict(int)
        for ticket in tickets:
            for category in ticket.category_ids:
                category_counter[category.name] += 1

        category_data = list(category_counter.items())

        return request.render('quickdesk.quickdesk_graph_template', {
            'user_labels': json.dumps([rec[0] for rec in user_data]),
            'user_counts': json.dumps([rec[1] for rec in user_data]),
            'ticket_labels': json.dumps([rec['number'] for rec in comment_data]),
            'comment_counts': json.dumps([rec['comments_count'] for rec in comment_data]),
            'category_labels': json.dumps([name for name, count in category_data]),
            'category_counts': json.dumps([count for name, count in category_data]),
        })

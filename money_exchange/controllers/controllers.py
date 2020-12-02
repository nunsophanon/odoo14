# -*- coding: utf-8 -*-
# from odoo import http


# class MoneyExchange(http.Controller):
#     @http.route('/money_exchange/money_exchange/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/money_exchange/money_exchange/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('money_exchange.listing', {
#             'root': '/money_exchange/money_exchange',
#             'objects': http.request.env['money_exchange.money_exchange'].search([]),
#         })

#     @http.route('/money_exchange/money_exchange/objects/<model("money_exchange.money_exchange"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('money_exchange.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class money_exchange(models.Model):
    _name = 'money_exchange.money_exchange'
    _description = 'money_exchange.money_exchange'

    name = fields.Char()
    date_change = fields.Datetime()
    output_amount = fields.Float(compute="_compute_output_amount", store=True)
    note = fields.Char()


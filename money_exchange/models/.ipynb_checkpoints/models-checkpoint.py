# -*- coding: utf-8 -*-

from odoo import models, fields, api


class money_exchange(models.Model):
    _name = 'money_exchange.money_exchange'
    _description = 'money_exchange.money_exchange'
    
    @api.depends('input_currency_id', 'date_change')
    def _compute_input_currency_rate(self):
        if self.input_currency_id:
            self.input_currency_rate = self.input_currency_id.with_context(date=self.date_change).rate or 1.0
        else:
            self.input_currency_rate = 1.0
            
    @api.depends('output_currency_id', 'date_change')
    def _compute_output_currency_rate(self):
        if self.output_currency_id:
            self.output_currency_rate = self.output_currency_id.with_context(date=self.date_change).rate or 1.0
        else:
            self.output_currency_rate = 1.0
            
            
    
    @api.depends('input_amount', 'input_currency_rate', 'output_currency_rate')
    def _amount_all(self):
        """
        Compute the output amounts of the SO.
        """
        self.output_amount = (self.input_amount*self.output_currency_rate)/self.input_currency_rate

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    date_change = fields.Datetime(string='Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, tracking=2, default=lambda self: self.env.user)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    input_currency_id = fields.Many2one('res.currency', store=True, string='Input Currency')
    output_currency_id = fields.Many2one('res.currency', store=True, string='Output Currency')
    input_currency_rate = fields.Float("Input Currency Rate", compute='_compute_input_currency_rate', compute_sudo=True, store=True, digits=(12, 6), readonly=True, help='Input Rate')
    output_currency_rate = fields.Float("Output Currency Rate", compute='_compute_output_currency_rate', compute_sudo=True, store=True, digits=(12, 6), readonly=True, help='Output Rate')
    input_amount = fields.Float(string='Input Amount',store=True)
    output_amount = fields.Float(string='Output Amount', store=True, readonly=True, compute='_compute_output_amount', tracking=4)
    
    note = fields.Char()
    
    
    def _action_compute(self):
        self.write({'state': 'computed'})
        
    def _action_cancel(self):
        self.write({'state': 'cencelled'})
        
    def _action_draft(self):
        self.write({'state': 'draft'})


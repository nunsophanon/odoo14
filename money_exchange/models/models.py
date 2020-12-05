# -*- coding: utf-8 -*-

from odoo import models, fields, api


class money_exchange(models.Model):
    _name = 'money.exchange'
    _description = 'money.exchange'
    
    @api.depends('input_currency_id', 'date_change')
    def _compute_input_currency_rate(self):
        if self.input_currency_id:
            self.input_currency_rate = self.input_currency_id.rate or 1.0
            # self.input_currency_rate = self.input_currency_id.with_context(date=self.date_change).rate or 1.0
        else:
            self.input_currency_rate = 1.0
            
    @api.depends('output_currency_id', 'date_change')
    def _compute_output_currency_rate(self):
        if self.output_currency_id:
            self.output_currency_rate = self.output_currency_id.rate or 1.0
            # self.output_currency_rate = self.output_currency_id.with_context(date=self.date_change).rate or 1.0
        else:
            self.output_currency_rate = 1.0
            
            
    
    @api.depends('input_amount', 'input_currency_rate', 'output_currency_rate')
    def _compute_output_amount(self):
        """
        Compute the output amounts of the SO.
        """
        self.output_amount = (self.input_amount*self.output_currency_rate)/self.input_currency_rate
        
        
    @api.depends('output_amount', 'service')
    def _compute_tax_change(self):
        '''
        When you change out_amount or tax
        it will update the total of the currency exchange
        -------------------------------------------------
        @param self: object pointer
        '''
        
        self.total = self.output_amount + self.service
        

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: ('New'))

    date_change = fields.Datetime(string='Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, tracking=2, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.company)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    input_currency_id = fields.Many2one('res.currency', store=True, string='Input Currency', readonly=True, states={'draft': [('readonly', False)]})
    output_currency_id = fields.Many2one('res.currency', store=True, string='Output Currency', readonly=True, states={'draft': [('readonly', False)]})
    input_currency_rate = fields.Float("Input Currency Rate", compute='_compute_input_currency_rate', compute_sudo=True, store=True, digits=(12, 6), readonly=True, help='Input Rate')
    output_currency_rate = fields.Float("Output Currency Rate", compute='_compute_output_currency_rate', compute_sudo=True, store=True, digits=(12, 6), readonly=True, help='Output Rate')
    input_amount = fields.Float(string='Input Amount',store=True, readonly=True, states={'draft': [('readonly', False)]})
#     commission = fields.Float(string='Commission',store=True)
    output_amount = fields.Float(string='Output Amount', store=True, readonly=True, compute='_compute_output_amount', tracking=4)
    service = fields.Float('Service (%)', size=64, default=0.0, index=True)
    total = fields.Float(compute="_compute_tax_change", string='Total Amount')
    note = fields.Text('Note')


    def action_done(self):
        seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(self.date_change))
        name = self.env['ir.sequence'].next_by_code('money.exchange', sequence_date=seq_date) or ('New')
        self.write({'state': 'done','name':name})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})


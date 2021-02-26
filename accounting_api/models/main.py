from odoo import api, fields, models, tools, SUPERUSER_ID, _


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def sale_get_payment_term(self, partner):
        # if partner.property_payment_term_id:
        #     return partner.property_payment_term_id.id
        return (
                self.env.ref('account.account_payment_term_immediate', False) or
                self.env['account.payment.term'].sudo().search([('company_id', '=', self.company_id.id)], limit=1)
        ).id
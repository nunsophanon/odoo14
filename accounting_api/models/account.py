from odoo import api, fields, models, tools, SUPERUSER_ID, _
import pytz


class SchoolInvoice(models.Model):
    _name = "school.invoice"
    _description = "Function School Invoice"
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    def create_invoice(self, move_vals):
        # self.ensure_one()
        move_id = self.env['account.move'].sudo().with_company(self.company_id).with_context(
            default_move_type=move_vals['move_type']).create(move_vals)
        message = _("This Invoice is created from CUS") % (
                  self.id, self.name)
        move_id.message_post(body=message)

        return move_id
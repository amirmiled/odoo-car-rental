from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    driving_license = fields.Char(string='Driving License')
    rental_ids = fields.One2many('rental.rental', 'partner_id', string='Rentals')
    rental_count = fields.Integer(string='Rental Count', compute='_compute_rental_count')
    
    @api.depends('rental_ids')
    def _compute_rental_count(self):
        for partner in self:
            partner.rental_count = len(partner.rental_ids)

    def action_view_rentals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rentals',
            'res_model': 'rental.rental',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],            
            'context': {'default_partner_id': self.id},
        }
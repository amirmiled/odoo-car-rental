from odoo import fields, models


class RentalReturnWizard(models.TransientModel):
    _name = 'rental.return.wizard'
    _description = 'Rental Return Wizard'

    rental_id = fields.Many2one('rental.rental', string='Rental', required=True, readonly=True)
    mileage = fields.Integer(string='Mileage', required=True)
    has_damage = fields.Boolean(string='Damaged')
    damage_note = fields.Text(string='Damage Note')


    def action_confirm_return(self):
        self.ensure_one()
        self.rental_id.write({
            'return_mileage': self.mileage,   
            'has_damage': self.has_damage,
            'damage_note': self.damage_note,
        })
        self.rental_id.action_return()
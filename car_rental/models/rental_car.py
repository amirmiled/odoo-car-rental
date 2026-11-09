from odoo import models, fields

class RentalCar(models.Model):
    _name = 'rental.car'
    _description = 'Rental Car'

    name = fields.Char(string='Name', required=True)
    license_plate = fields.Char(string='License Plate', required=True)

    brand = fields.Char(string='Brand')
    model_name = fields.Char(string='Model Name')
    year = fields.Integer(string='Year')
    currency_id = fields.Many2one('res.currency',
                                  string='Currency',
                                  default=lambda self: self.env.company.currency_id,
                                  required=True)
    daily_price = fields.Monetary(string='Daily Price')
    image = fields.Image(string='Image')
    state = fields.Selection([('available','Available'),('rented','Rented'),('maintenance','Maintenance')],
                             string='Status',
                             default='available',
                             required=True  
                             )
    active = fields.Boolean(string='Active',
                            default=True)

    _sql_constraints = [
    ('license_plate_unique', 'UNIQUE(license_plate)', 'This license plate already exists!'),
    ]
from odoo import api, fields, models, Command
from odoo.exceptions import UserError, ValidationError


class RentalRental(models.Model):
    _name = 'rental.rental'
    _description = 'Car Rental'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', default='New', readonly=True, copy=False)
    partner_id = fields.Many2one('res.partner' , string='Customer', required=True, tracking=True)
    car_id = fields.Many2one('rental.car',string='Car',required=True, tracking=True)
    date_start = fields.Date(string='Start Date', required=True, tracking=True)
    date_end = fields.Date(string='End Date', required=True, tracking=True)
    currency_id = fields.Many2one(related='car_id.currency_id')
    daily_price = fields.Monetary(string='Daily Price', store=True, readonly=False, compute='_compute_daily_price')
    duration_days = fields.Integer(string='Days', store=True, compute='_compute_duration_days')
    total_price = fields.Monetary(string='Total Price', store=True, compute='_compute_total_price', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('returned', 'Returned'),
        ('invoiced', 'Invoiced'),
        ('cancelled','Cancelled'),
        ],string='Status', required=True, default='draft', copy=False, tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    user_id = fields.Many2one('res.users', string='Agent', default=lambda self: self.env.user, tracking=True)
    return_mileage = fields.Integer(string='Return Mileage', readonly=True)
    has_damage = fields.Boolean(string='Damage', readonly=True)
    damage_note = fields.Text(string='Damage Description', readonly=True)
    is_late = fields.Boolean(string='Late', readonly=True, copy=False)


    @api.depends('date_start','date_end')
    def _compute_duration_days(self):
        for rental in self:
            if rental.date_start and rental.date_end:
                rental.duration_days = max((rental.date_end - rental.date_start).days, 1)
            else:
                rental.duration_days = 0

    @api.depends('duration_days','daily_price')
    def _compute_total_price(self):
        for rental in self:
            rental.total_price = rental.duration_days * rental.daily_price

    @api.depends('car_id')
    def _compute_daily_price(self):
        for rental in self:
            rental.daily_price = rental.car_id.daily_price   


    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rental in self:
            if rental.date_end < rental.date_start:  
                raise ValidationError("The end date cannot be before the start date.")

    @api.constrains('car_id', 'date_start', 'date_end', 'state')
    def _check_car_availability(self):
        for rental in self:
            overlapping = self.sudo().search([
                ('id', '!=', rental.id),
                ('car_id', '=', rental.car_id.id),
                ('date_start', '<=', rental.date_end),
                ('date_end', '>=', rental.date_start),
                ('state', '!=', 'cancelled'),
            ])
            if overlapping:
                raise ValidationError("This car is already rented during these dates.")


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.rental')
        return super().create(vals_list)




    def action_confirm(self):
        for rental in self:
            rental.state = 'confirmed'

    def action_start(self):
        for rental in self:
            rental.state = 'ongoing'        
            rental.car_id.sudo().state = 'rented'     

    def action_return(self):
        for rental in self:
            rental.state = 'returned'
            rental.car_id.sudo().state = 'available'
            rental.message_post(body=f"Car {rental.car_id.name} returned.")
            rental.is_late = False

    def action_cancel(self):
        if not self.env.user.has_group('car_rental.group_rental_manager'):
            raise UserError("Only a manager can cancel a rental.")
        for rental in self:
            if rental.state == 'ongoing':
                rental.car_id.sudo().state = 'available'
            rental.state = 'cancelled'

    def action_draft(self):
        if not self.env.user.has_group('car_rental.group_rental_manager'):
            raise UserError("Only a manager can reset a rental to draft.")
        for rental in self:
            rental.state = 'draft'

    def action_create_invoice(self):
        self.ensure_one()
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,             
            'currency_id': self.currency_id.id,
            'invoice_line_ids': [Command.create({
                'name': f"{self.name} - {self.car_id.name}",
                'quantity': self.duration_days,
                'price_unit': self.daily_price,                  
            })],
        })
        self.invoice_id = invoice
        self.state = 'invoiced'                            
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
        }

    def action_open_return_wizard(self):
        self.ensure_one()
        return {
        'type': 'ir.actions.act_window',
        'name': 'Return Car',
        'res_model': 'rental.return.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {'default_rental_id': self.id},
        }



    def _cron_check_late_rentals(self):
        today = fields.Date.context_today(self)
        late_rentals = self.search([
            ('state', '=', 'ongoing'),            
            ('date_end', '<', today),        
            ('is_late', '=', False),       
        ])
        for rental in late_rentals:
            rental.is_late = True
            rental.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=rental.user_id.id,
                note=f"Rental {rental.name} is late. Please contact the customer.",
            )
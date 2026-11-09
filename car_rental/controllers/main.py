from odoo import http
from odoo.http import request


class RentalApi(http.Controller):

    @http.route('/api/cars/available', type='http', auth='public',
                methods=['GET'], csrf=False, cors='*')
    def available_cars(self, **kwargs):
        cars = request.env['rental.car'].sudo().search([
            ('state', '=', 'available'),
        ])
        data = []
        for car in cars:
            data.append({
                'id': car.id,
                'name': car.name,
                'brand': car.brand,
                'model_name': car.model_name,
                'year': car.year,
                'daily_price': car.daily_price,
                'currency': car.currency_id.name,
            })
        return request.make_json_response(data)
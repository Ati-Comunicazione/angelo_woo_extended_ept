# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class WooInstanceEpt(models.Model):
    _inherit = "woo.instance.ept"

    woo_update_products_price_last_date = fields.Datetime(help="This date is when the update products price at last.")

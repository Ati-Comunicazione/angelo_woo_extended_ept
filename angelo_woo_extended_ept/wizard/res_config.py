# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _, SUPERUSER_ID


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    woo_update_products_price_last_date = fields.Datetime(string="Last Update Product Price Date",
                                                          help="Connector only update those products price which have created "
                                                               "after a given date.")

    @api.onchange('woo_instance_id')
    def onchange_woo_instance_id(self):
        super(ResConfigSettings, self).onchange_woo_instance_id()
        instance = self.woo_instance_id or False
        if instance:
            self.woo_update_products_price_last_date = instance.woo_update_products_price_last_date

    def execute(self):
        instance = self.woo_instance_id
        values = {}
        res = super(ResConfigSettings, self).execute()
        if instance:
            values["woo_update_products_price_last_date"] = self.woo_update_products_price_last_date
            instance.write(values)
        return res
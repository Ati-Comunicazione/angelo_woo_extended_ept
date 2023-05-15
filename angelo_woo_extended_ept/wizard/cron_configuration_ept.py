# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7 * interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}


class WooCronConfigurationEpt(models.TransientModel):
    _inherit = "woo.cron.configuration.ept"

    # Auto cron for Update product Price
    woo_auto_update_product_price = fields.Boolean('Woo Product Price Auto Update.', default=False,
                                                   help="Check if you want to automatically update product price from Odoo to WooCommerce.")
    woo_update_product_price_interval_number = fields.Integer(help="Repeat every x.", default=10)
    woo_update_product_price_interval_type = fields.Selection([('minutes', 'Minutes'),
                                                               ('hours', 'Hours'), ('days', 'Days'),
                                                               ('weeks', 'Weeks'), ('months', 'Months')],
                                                              'Woo Update Product Price Unit')
    woo_update_product_price_next_execution = fields.Datetime(help='Next execution time')
    woo_update_product_price_user_id = fields.Many2one('res.users', string="Woo User",
                                                       help='Woo Product Price Update User',
                                                       default=lambda self: self.env.user)

    @api.constrains("woo_update_product_price_interval_number")
    def check_update_product_price_cron_interval_time(self):
        """
        It does not let set the cron execution time to Zero.
        @author: Yagnik Joshi @Emipro Technologies Pvt. Ltd on date 30/03/2023.
        Task Id : 222686
        """
        for record in self:
            is_zero = False
            if record.woo_auto_update_product_price and record.woo_update_product_price_interval_number <= 0:
                is_zero = True
            if is_zero:
                raise ValidationError(_("Cron Execution Time can't be set to 0(Zero). "))

    def update_product_price_cron_field(self, instance):
        """
        Set Update Product Price cron fields value while open the wizard for cron configuration from the instance form view.
        @author: Yagnik Joshi @Emipro Technologies Pvt. Ltd on date 03/04/2023.
        Task Id : 222686
        """
        try:
            update_product_price_cron_exist = instance and self.env.ref(
                'angelo_woo_extended_ept.ir_cron_woo_update_product_price_instance_%d' % instance.id)
        except:
            update_product_price_cron_exist = False
        if update_product_price_cron_exist:
            self.woo_auto_update_product_price = update_product_price_cron_exist.active or False
            self.woo_update_product_price_interval_number = update_product_price_cron_exist.interval_number or False
            self.woo_update_product_price_interval_type = update_product_price_cron_exist.interval_type or False
            self.woo_update_product_price_next_execution = update_product_price_cron_exist.nextcall or False
            self.woo_update_product_price_user_id = update_product_price_cron_exist.user_id.id or False

    @api.onchange("woo_instance_id")
    def onchange_woo_instance_id(self):
        """
        Set cron field value while open the wizard for cron configuration from the instance form view.
        @author: Yagnik Joshi @Emipro Technologies Pvt. Ltd on date 03/04/2023.
        Task Id : 222686
        """
        res = super(WooCronConfigurationEpt, self).onchange_woo_instance_id()
        instance = self.woo_instance_id
        self.update_product_price_cron_field(instance)
        return res

    def setup_woo_update_product_price_cron(self, instance):
        """
            Setup Cron for Export Coupon
            :param instance:
            :return:
            @author: Yagnik Joshi @Emipro Technologies Pvt. Ltd on date 03/04/2023.
            Task Id : 222686
        """
        try:
            cron_exist = self.env.ref(
                'angelo_woo_extended_ept.ir_cron_woo_update_product_price_instance_%d' % instance.id)
        except:
            cron_exist = False
        if self.woo_auto_update_product_price:
            nextcall = datetime.now() + _intervalTypes[self.woo_update_product_price_interval_type](
                self.woo_update_product_price_interval_number)
            vals = self.prepare_vals_for_cron(self.woo_update_product_price_interval_number,
                                              self.woo_update_product_price_interval_type,
                                              self.woo_update_product_price_user_id)
            vals.update({
                'nextcall': self.woo_update_product_price_next_execution or nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                'code': "model.auto_update_product_price(%d)" % (instance.id),
            })
            if cron_exist:
                vals.update({'name': cron_exist.name})
                cron_exist.write(vals)
            else:
                core_cron = self.search_cron_with_xml_id("angelo_woo_extended_ept.ir_cron_update_woo_product_price")

                name = instance.name + ' : ' + core_cron.name
                vals.update({'name': name})
                new_cron = core_cron.copy(default=vals)
                name = 'ir_cron_woo_update_product_price_instance_%d' % (instance.id)
                self.env['ir.model.data'].create({'module': 'angelo_woo_extended_ept',
                                                  'name': name,
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True})
        else:
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def save(self):
        """
        This method is used to update Coupon related cron job fields value.
        @author: Yagnik Joshi @Emipro Technologies Pvt. Ltd on date 03/04/2023.
        Task Id : 222686
        """
        res = super(WooCronConfigurationEpt, self).save()
        instance = self.woo_instance_id
        if instance:
            self.setup_woo_update_product_price_cron(instance)
        return res
# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import time
import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger("WooCommerce")


class WooProductTemplateEpt(models.Model):
    _inherit = "woo.product.template.ept"

    def auto_update_product_price(self, woo_instance):
        """
        This method is call when auto update product price cron in enable
        This method is call update_stock() method which is responsible to update stock in WooCommerce.
        :return: Boolean
        @author: Yagnik Joshi @Emipro Technologies Pvt. Ltd on date 03/04/2023.
        Task Id : 222686
        """
        start = time.time()
        woo_instance_obj = self.env['woo.instance.ept']
        common_log_book_obj = self.env['common.log.book.ept']
        woo_product_tmpl_obj = self.env['woo.product.template.ept']
        woo_product_product_obj = self.env['woo.product.product.ept']

        woo_is_set_price = True
        woo_publish = True
        woo_is_set_image = False
        woo_basic_detail = False

        woo_instance = woo_instance_obj.browse(woo_instance)
        woo_instance.woo_update_products_price_last_date = datetime.now() - timedelta(hours=3)
        product_ids, applied = self.get_products_based_on_price_list_movement_date_ept(
            woo_instance.woo_update_products_price_last_date, woo_instance.company_id)
        for instance in woo_instance:
            woo_product_ids = woo_product_product_obj.search([('product_id', 'in', product_ids)])
            woo_product_tmpl_ids = woo_product_tmpl_obj.search([('product_tmpl_id', 'in', product_ids)])
            woo_templates = woo_product_ids.mapped('woo_template_id')
            woo_templates += woo_product_tmpl_ids
            if applied == True:
                woo_templates += woo_product_tmpl_obj.search([])
            if not woo_templates:
                continue
            common_log_id = common_log_book_obj.woo_create_log_book('export', instance)
            woo_product_tmpl_obj.update_products_in_woo(instance, woo_templates, woo_is_set_price, woo_publish,
                                                        woo_is_set_image, woo_basic_detail, common_log_id)
            if not common_log_id.log_lines:
                common_log_id.unlink()
        end = time.time()
        woo_instance.woo_update_products_price_last_date = datetime.now()
        _logger.info("Update products in Woocommerce Store in %s seconds.", str(end - start))
        return True

    def get_products_based_on_price_list_movement_date_ept(self, from_datetime, company):
        """ This method is used to get product records which price updates after from date.
            @param from_datetime: Date
            @param company: Company
            @return company: It will return list of product records
            @author: Yagnik Joshi @Emipro Technologies Pvt. Ltd on date 03/04/2023 .
            Task_id: 222686
        """
        if not from_datetime or not company:
            raise UserError(_('You must provide the From Date and Company'))
        result = []
        date = str(datetime.strftime(from_datetime, '%Y-%m-%d %H:%M:%S'))
        query = (
                    """select distinct product_id, product_tmpl_id from product_pricelist_item where write_date >= '%s' and company_id = %d """ % (
                date, company.id))
        self._cr.execute(query)
        result += self._cr.dictfetchall()
        product_ids = [product_id.get('product_id') for product_id in result]
        product_ids += [product_id.get('product_tmpl_id') for product_id in result]

        sub_qry = (
                """select distinct applied_on from product_pricelist_item where write_date >= '%s' and company_id = %d """ % (
            date, company.id))
        self._cr.execute(sub_qry)
        result_applied_on = self._cr.dictfetchall()
        applied_on = [applied_on.get('applied_on') for applied_on in result_applied_on]
        search_string = [string[2:] for string in applied_on]
        compare = [i for i in search_string if 'global' in search_string]
        if len(compare) > 0:
            applied = True
        else:
            applied = False

        return list(set(product_ids)), applied

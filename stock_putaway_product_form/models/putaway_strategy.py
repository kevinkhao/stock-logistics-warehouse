# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FixedPutAwayStrategy(models.Model):
    _inherit = "stock.fixed.putaway.strat"

    product_tmpl_id = fields.Many2one(
        "product.template",
        compute="_compute_product_tmpl_id",
        string="Product template",
        store=True,
    )

    @api.depends("product_id")
    def _compute_product_tmpl_id(self):
        for rec in self:
            rec.product_tmpl_id = rec.product_id.product_tmpl_id

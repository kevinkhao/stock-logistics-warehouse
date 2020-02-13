# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_tmpl_putaway_ids = fields.One2many(
        comodel_name="stock.fixed.putaway.strat",
        inverse_name="product_tmpl_id",
        string="Product putaway strategies by product",
    )

    product_putaway_categ_ids = fields.Many2many(
        comodel_name="stock.fixed.putaway.strat",
        string="Product putaway strategies by category",
        compute="_compute_putaway_categ_ids",
    )

    def _find_closest_categ_match(self, categ, putaway_lines):
        """Returns the putaway line with the nearest product category"""
        filtered_lines = putaway_lines.filtered(
            lambda r: r.category_id == categ
        )
        if filtered_lines:
            return filtered_lines[0]
        elif categ.parent_id:
            return self._find_closest_categ_match(
                categ.parent_id, putaway_lines
            )
        else:
            return self.env["stock.fixed.putaway.strat"]

    @api.depends("categ_id")
    def _compute_putaway_categ_ids(self):
        for rec in self:
            """Pay attention to keep only 1 (most specific,
            i.e closest to our product category's parents)
            putaway.strat per product.putaway"""
            res = self.env["stock.fixed.putaway.strat"]
            categ = rec.categ_id
            categs = categ
            parent_categ_iterator = rec.categ_id.parent_id
            # get all our category's parents
            while parent_categ_iterator:
                categs += parent_categ_iterator
                parent_categ_iterator = parent_categ_iterator.parent_id
            # get matching lines from our category or its parents
            product_putaway_categ_lines = self.env[
                "stock.fixed.putaway.strat"
            ].search([("category_id", "in", categs.ids)])
            # from these, get the matching putaway.strats and find
            # the lowest-level category match
            product_putaways = product_putaway_categ_lines.mapped("putaway_id")
            for el in product_putaways:
                lines = el.fixed_location_ids
                res += self._find_closest_categ_match(categ, lines)
            rec.product_putaway_categ_ids = res

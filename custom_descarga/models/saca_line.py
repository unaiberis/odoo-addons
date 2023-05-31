# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta


class SacaLine(models.Model):
    _inherit = "saca.line"

    def _get_default_weight_uom(self):
        return self.env[
            "product.template"]._get_weight_uom_name_from_ir_config_parameter()

    priority = fields.Selection([
        ("0", "Very Low"),
        ("1", "Low"),
        ("2", "Normal"),
        ("3", "High"),
        ("4", "Very High"),
        ("5", "Super High")],
        string="Valuation",
        default="0")
    forklift = fields.Boolean(string="Forklift", default=False)
    download_unit = fields.Integer(string="Download Unit")
    staff = fields.Integer(string="Staff")
    crew = fields.Integer(string="Crew")
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id.id)
    total_cost = fields.Float(string="Total Cost")
    kilo_discount = fields.Float(string="Kilo discount")
    guide_number = fields.Char(string="Guide Number")
    torista_id = fields.Many2one(
        string="Torista",
        comodel_name="res.partner",
        domain=lambda self: [
            ("category_id", "=", (
                self.env.ref("custom_descarga.torista_category").id))])
    slaughterer_ids = fields.Many2many(
        string="Slaughterer",
        comodel_name="res.partner",
        relation="rel_sacaline_slaughterer",
        column1="partner_id",
        column2="saca_line_id",
        domain=lambda self: [
            ("category_id", "=", (
                self.env.ref("custom_descarga.slaughterer_category").id))])
    hanger_ids = fields.Many2many(
        string="Hanger",
        comodel_name="res.partner",
        relation="rel_sacaline_hanger",
        column1="partner_id",
        column2="saca_line_id",
        domain=lambda self: [
            ("category_id", "=", (
                self.env.ref("custom_descarga.hanger_category").id))])
    forklift_operator_ids = fields.Many2many(
        string="Forklift Operator",
        comodel_name="res.partner",
        relation="rel_sacaline_forklift",
        column1="partner_id",
        column2="saca_line_id",
        domain=lambda self: [
            ("category_id", "=", (
                self.env.ref("custom_descarga.forklift_category").id))])
    craw = fields.Float(string="Craw")
    weight_uom_name = fields.Char(
        string='Weight UOM', default=_get_default_weight_uom)
    color_name = fields.Selection(
        string="Color",
        selection=[
            ("red", "Red"),
            ("blue", "Blue"),
            ("green", "Green"),
            ("yellow", "Yellow"),
            ("gray", "Gray"),
            ("purple", "Purple")],
        related="stage_id.color_name",
        store="True")
    is_canceled = fields.Boolean(string="Canceled", default=False)
    waiting_reason = fields.Selection(
        string="Waiting Reason", selection=[
            ("failure", "Failure"),
            ("lunch", "Lunch"),
            ("truck_delay", "Truck Delay")])
    origin_qty = fields.Float(
        string="Origin Qty",
        compute="_compute_origin_qty",
        store=True)
    dest_qty = fields.Float(
        string="Dest Qty",
        compute="_compute_dest_qty",
        store=True)
    purchase_price = fields.Float(
        string="Purchase Price",
        compute="_compute_puchase_price",
        store=True)
    purchase_unit_price = fields.Float(
        string="Purchase Unit Price",
        compute="_compute_puchase_unit_price",
        store=True)
    gross_origin = fields.Float(string="Gross Origin")
    tara_origin = fields.Float(string="Tara Oringin")
    net_origin = fields.Float(
        string="Net Origin", compute="_compute_net_origin", store=True)
    average_weight_origin = fields.Float(
        string="Average Weight Origin",
        compute="_compute_average_weight_origin",
        digits=dp.get_precision("Weight Decimal Precision"),
        store=True)
    gross_dest = fields.Float(string="Gross Dest.")
    tara_dest = fields.Float(string="Tara Dest.")
    net_dest = fields.Float(
        string="Net Dest", compute="_compute_net_dest", store=True)
    average_weight_dest = fields.Float(
        string="Average Weight Dest",
        digits=dp.get_precision("Weight Decimal Precision"),
        compute="_compute_average_weight_dest",
        store=True)
    dif_gross = fields.Float(
        string="Diff. Gross", compute="_compute_dif_gross", store=True)
    dif_tara = fields.Float(
        string="Diff. Tara", compute="_compute_dif_tara", store=True)
    dif_net = fields.Float(
        string="Diff. Net", compute="_compute_dif_net", store=True)
    dif_average_weight = fields.Float(
        string="Diff. Averge Weight",
        digits=dp.get_precision("Weight Decimal Precision"),
        compute="_compute_dif_average_weight", store=True)
    distance_done = fields.Float(
        string="Kilometers")
    is_presaca = fields.Boolean(
        string="Is Presaca",
        compute="_compute_stage",
        store=True)
    is_saca = fields.Boolean(
        string="Is Saca",
        compute="_compute_stage",
        store=True)
    is_descarga = fields.Boolean(
        string="Is Descarga",
        compute="_compute_stage",
        store=True)
    is_killing = fields.Boolean(
        string="Is Killing",
        compute="_compute_stage",
        store=True)
    is_classified = fields.Boolean(
        string="Is Classified",
        compute="_compute_stage",
        store=True)
    historic_line_ids = fields.One2many(
        string="Historic Lines",
        comodel_name="saca.line",
        inverse_name="historic_id")
    historic_id = fields.Many2one(
        string="Historic",
        comodel_name="saca.line")
    hard_chicken = fields.Integer(
        string="Hard Chicken %")
    yellowish_chicken = fields.Boolean(
         string="Yellowish Chicken",
         default=False)
    burned_leg = fields.Boolean(
        string="Burned Legs",
        default=False)
    dirt = fields.Boolean(
        string="Dirt",
        default=False)
    count_historic = fields.Integer(
        string="Count Historic",
        compute="_compute_count_historic")
    descarga_order = fields.Char(
        string="Deccarga Order",
        compute="_compute_descarga_order")
    img_origin = fields.Binary(
        string="Ticket Farm",
        attachment=True)
    img_dest = fields.Binary(
        string="Ticket Slaughterhouse")
    staff_crew = fields.Integer(
        string="Staff Crew")
    floor = fields.Selection(
        [('single', 'Single'), ('top', 'Top'), ('below', 'Below')])

    def _compute_descarga_order(self):
        for line in self:
            line.descarga_order = "0"
            saca_lines = line.saca_id.saca_line_ids.filtered(
                lambda c: c.unload_date)
            if saca_lines and line.unload_date:
                saca_lines = sorted(
                    saca_lines, key=lambda c: c.unload_date, reverse=False)
                position = saca_lines.index(line)
                line.descarga_order = u"{}".format(position + 1)

    def _compute_count_historic(self):
        for line in self:
            line.count_historic = len(line.historic_line_ids)

    @api.depends("stage_id")
    def _compute_stage(self):
        for line in self:
            presaca = self.env.ref("custom_saca_purchase.stage_presaca")
            saca = self.env.ref("custom_saca_purchase.stage_saca")
            descarga = self.env.ref("custom_descarga.stage_descarga")
            matanza = self.env.ref("custom_descarga.stage_matanza")
            clasificado = self.env.ref("custom_descarga.stage_clasificado")
            line.is_presaca = False
            line.is_saca = False
            line.is_descarga = False
            line.is_killing = False
            line.is_classified = False
            if line.stage_id == presaca:
                line.is_presaca = True
                line.is_saca = False
                line.is_descarga = False
                line.is_killing = False
                line.is_classified = False
            if line.stage_id == saca:
                line.is_presaca = False
                line.is_saca = True
                line.is_descarga = False
                line.is_killing = False
                line.is_classified = False
            if line.stage_id == descarga:
                line.is_presaca = False
                line.is_saca = False
                line.is_descarga = True
                line.is_killing = False
                line.is_classified = False
            if line.stage_id == matanza:
                line.is_presaca = False
                line.is_saca = False
                line.is_descarga = False
                line.is_killing = True
                line.is_classified = False
            if line.stage_id == clasificado:
                line.is_presaca = False
                line.is_saca = False
                line.is_descarga = False
                line.is_killing = False
                line.is_classified = True

    @api.depends("download_unit", "net_dest")
    def _compute_average_weight_dest(self):
        for line in self:
            line.average_weight_dest = 0
            if line.download_unit != 0:
                line.average_weight_dest = line.net_dest / line.download_unit

    @api.depends("download_unit", "net_origin")
    def _compute_average_weight_origin(self):
        for line in self:
            line.average_weight_origin = 0
            if line.download_unit != 0:
                line.average_weight_origin = (
                    line.net_origin / line.download_unit)

    @api.depends("average_weight_origin", "average_weight_dest")
    def _compute_dif_average_weight(self):
        for line in self:
            line.dif_average_weight = (
                line.average_weight_dest - line.average_weight_origin)

    @api.depends("net_origin", "net_dest")
    def _compute_dif_net(self):
        for line in self:
            line.dif_net = line.net_dest - line.net_origin

    @api.depends("tara_origin", "tara_dest")
    def _compute_dif_tara(self):
        for line in self:
            line.dif_tara = line.tara_dest - line.tara_origin

    @api.depends("gross_origin", "gross_dest")
    def _compute_dif_gross(self):
        for line in self:
            line.dif_gross = line.gross_dest - line.gross_origin

    @api.depends("gross_origin", "tara_origin")
    def _compute_net_origin(self):
        for line in self:
            line.net_origin = line.gross_origin - line.tara_origin
            line.onchange_origin()

    @api.depends("gross_dest", "tara_dest")
    def _compute_net_dest(self):
        for line in self:
            line.net_dest = line.gross_dest - line.tara_dest

    @api.depends("sale_order_id", "sale_order_id.picking_ids",
                 "sale_order_id.picking_ids.move_ids_without_package",
                 "sale_order_id.picking_ids.move_ids_without_package.quantity_done")
    def _compute_origin_qty(self):
        for line in self:
            if line.sale_order_id and (
                line.sale_order_id.picking_ids) and (
                    line.sale_order_id.picking_ids[0].
                    move_ids_without_package):
                line.origin_qty = (
                    line.sale_order_id.picking_ids[0].
                    move_ids_without_package[0].quantity_done)

    @api.depends("purchase_order_id", "purchase_order_id.picking_ids",
                 "purchase_order_id.picking_ids.move_ids_without_package",
                 "purchase_order_id.picking_ids.move_ids_without_package.quantity_done")
    def _compute_dest_qty(self):
        for line in self:
            if line.purchase_order_id and (
                line.purchase_order_id.picking_ids) and (
                    line.purchase_order_id.picking_ids.
                    move_ids_without_package):
                line.dest_qty = (
                    line.purchase_order_id.picking_ids[0].
                    move_ids_without_package[0].quantity_done)

    @api.depends("purchase_order_id",
                 "purchase_order_id.order_line",
                 "purchase_order_id.order_line.price_unit")
    def _compute_puchase_unit_price(self):
        for line in self:
            if line.purchase_order_id and line.purchase_order_id.order_line:
                line.purchase_unit_price = (
                    line.purchase_order_id.order_line[0].price_unit)

    @api.depends("purchase_order_id",
                 "purchase_order_id.amount_untaxed")
    def _compute_puchase_price(self):
        for line in self:
            if line.purchase_order_id:
                line.purchase_price = line.purchase_order_id.amount_untaxed

    def write(self, values):
        result = super(SacaLine, self).write(values)
        if "download_unit" in values:
            for record in self:
                for line in record.move_line_ids:
                    line.download_unit = record.download_unit
                    for move in record.stock_move_ids:
                        move.download_unit = record.download_unit
        if "gross_origin" in (
            values) or "tara_origin" in (
                values) and self.net_origin:
            for line in self.purchase_order_line_ids:
                line.product_qty = self.net_origin
            for line in self.stock_move_ids:
                line.product_uom_qty = self.net_origin
        if "unload_date" in values:
            for line in self:
                if line.download_unit and line.move_line_ids:
                    for ml in line.move_line_ids:
                        ml.download_unit = line.download_unit
                    for move in line.stock_move_ids:
                        move.download_unit = line.download_unit
        return result

    @api.onchange("download_unit")
    def onchange_download_unit(self):
        if self.download_unit:
            for line in self.move_line_ids:
                line.download_unit = self.download_unit
            for move in self.stock_move_ids:
                move.download_unit = self.download_unit

    @api.onchange("staff")
    def onchange_staff(self):
        if self.staff:
            for line in self.saca_id.saca_line_ids:
                if not line.staff:
                    line.staff = self.staff

    @api.onchange("crew")
    def onchange_crew(self):
        if self.crew:
            for line in self.saca_id.saca_line_ids:
                if not line.crew:
                    line.crew = self.crew

    @api.onchange("slaughterer_ids")
    def onchange_slaughterer_ids(self):
        if self.slaughterer_ids:
            for line in self.saca_id.saca_line_ids:
                if not line.slaughterer_ids:
                    line.slaughterer_ids = [(6, 0, self.slaughterer_ids.ids)]

    @api.onchange("hanger_ids")
    def onchange_hanger_ids(self):
        if self.hanger_ids:
            for line in self.saca_id.saca_line_ids:
                if not line.hanger_ids:
                    line.hanger_ids = [(6, 0, self.hanger_ids.ids)]

    @api.onchange("forklift_operator_ids")
    def onchange_forklift_operator_ids(self):
        if self.forklift_operator_ids:
            for line in self.saca_id.saca_line_ids:
                if not line.forklift_operator_ids:
                    line.forklift_operator_ids = [
                        (6, 0, self.forklift_operator_ids.ids)]

    @api.onchange("gross_origin", "tara_origin", "download_unit")
    def onchange_origin(self):
        if self.breeding_id and self.breeding_id.estimate_weight_ids:
            line = self.breeding_id.estimate_weight_ids.filtered(
                lambda c: c.date == self.date)
            if line:
                line.write({
                    "saca_casualties": self.download_unit,
                    "real_weight": self.average_weight_origin * 1000})

    def action_next_stage(self):
        self.ensure_one()
        stage_saca = self.env.ref("custom_saca_purchase.stage_saca")
        stage_descarga = self.env.ref("custom_descarga.stage_descarga")
        stage_matanza = self.env.ref("custom_descarga.stage_matanza")
        stage_clasificado = self.env.ref("custom_descarga.stage_clasificado")
        if self.stage_id == stage_matanza:
            pickings = (
                self.purchase_order_id.picking_ids + (
                    self.sale_order_id.picking_ids))
            for picking in pickings:
                for line in picking.move_line_ids_without_package:
                    if not line.qty_done:
                        line.qty_done = line.move_id.product_uom_qty
                    if not line.lot_id and (
                        picking.picking_type_code) == (
                            "incoming"):
                        name = u'{}{}'.format(
                            line.saca_line_id.lot, line.saca_line_id.seq)
                        lot = self.env["stock.production.lot"].search([
                            ("product_id", "=", line.product_id.id),
                            ("name", "=", name),
                            ("company_id", "=", picking.company_id.id)
                            ], limit=1)
                        if not lot:
                            lot = self.env[
                                "stock.production.lot"].action_create_lot(
                                line.product_id, name, picking.company_id)
                        line.lot_id = lot.id
                if picking.state != "done":
                    if not picking.custom_date_done:
                        picking.custom_date_done = fields.Datetime.now()
                    picking.sudo().button_validate()
            self.write({
                "stage_id": stage_clasificado.id})
        elif self.stage_id == stage_descarga:
            for picking in self.sale_order_id.picking_ids:
                for move in picking.move_ids_without_package:
                    one_day_chicken = self.breeding_id.move_line_ids.filtered(
                        "product_id.one_day_chicken")
                    # if not one_day_chicken:
                        # raise ValidationError(
                            # _("This breeding does not have day-old chicks."))
                    name = u"{}".format(self.breeding_id.name)
                    lot = self.env["stock.production.lot"].search([
                        ("product_id", "=", move.product_id.id),
                        ("name", "=", name),
                        ("company_id", "=", picking.company_id.id)], limit=1)
                    if not lot:
                        lot = self.env[
                            "stock.production.lot"].action_create_lot(
                                move.product_id, name,
                                picking.company_id)
                picking.custom_date_done = self.date
                picking.action_confirm()
                picking.action_assign()
                picking.button_force_done_detailed_operations()
                for line in picking.move_line_ids_without_package:
                    line.write({
                        "lot_id": lot.id,
                        "download_unit": self.download_unit})
                picking.sudo().button_validate()
            for picking in self.purchase_order_id.picking_ids:
                picking.custom_date_done = self.date
            self.write({
                "stage_id": stage_matanza.id})
        elif self.stage_id == stage_saca:
            if not self.purchase_order_line_ids:
                raise ValidationError(
                    _("There is no any purchase order line.")
                )
            # if self.breeding_id:
                # one_day_chicken = self.breeding_id.move_line_ids.filtered("product_id.one_day_chicken")
                # if not one_day_chicken:
                    # raise ValidationError(
                        # _("This breeding does not have day-old chicks."))
            price = self.purchase_order_line_ids[0].price_unit
            self.purchase_order_id.button_confirm()
            if price:
                self.purchase_order_line_ids.price_unit = price
            type_normal = self.env["sale.order.type"].search([
                ("name", "ilike", "Normal"),
                ("company_id", "=", self.sale_order_id.company_id.id)],
            limit=1)
            if type_normal:
                self.sale_order_id.type_id = type_normal.id
            for line in self.sale_order_id.picking_ids:
                line.batch_id = self.breeding_id.id
            date = self.date + timedelta(days=1)
            time = datetime.now().time()
            time = time.strftime("%H:%M:%S")
            fecha = '{} {}'.format(date, time)
            self.write({
                "stage_id": stage_descarga.id,
                "unload_date": fecha})

    def action_create_purchase(self):
        result = super(SacaLine, self).action_create_purchase()
        stage_saca = self.env.ref("custom_saca_purchase.stage_saca")
        if self.stage_id == stage_saca:
            self.action_create_historic()
        return result

    def action_create_historic(self):
        self.ensure_one()
        stage_historico = self.env.ref("custom_descarga.stage_historico")
        historic = self.copy()
        historic.sudo().write({
            "historic_id": self.id,
            "is_historic": True,
            "saca_id": False,
            "stage_id": stage_historico.id,
            "is_canceled": True})

    def action_cancel(self):
        self.ensure_one()
        stage_presaca = self.env.ref("custom_saca_purchase.stage_presaca")
        stage_saca = self.env.ref("custom_saca_purchase.stage_saca")
        stage_descarga = self.env.ref("custom_descarga.stage_descarga")
        stage_cancelado = self.env.ref("custom_descarga.stage_cancelado")
        if self.stage_id in (stage_presaca, stage_saca, stage_descarga):
            self.is_canceled = True
            for move in self.stock_move_ids:
                move.picking_id.action_cancel()
            if self.sale_order_id:
                self.sale_order_id.action_cancel()
            if self.purchase_order_id:
                self.purchase_order_id.button_cancel()
            self.write({
                "stage_id": stage_cancelado.id})
        else:
            raise ValidationError(
                _("You cannot cancel because some products have already " +
                  "been delivered."))

    def action_view_historic(self):
        context = self.env.context.copy()
        context.update({'default_historic_id': self.id})
        return {
            'name': _("Historics"),
            'view_mode': 'tree,form',
            'res_model': 'saca.line',
            'domain': [('id', 'in', self.historic_line_ids.ids),
                       ('is_historic', '=', True)],
            'type': 'ir.actions.act_window',
            'context': context
        }

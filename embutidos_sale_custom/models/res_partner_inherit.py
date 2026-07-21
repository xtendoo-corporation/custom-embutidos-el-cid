from odoo import api, models


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    @api.depends_context("company")
    @api.depends("commercial_partner_id")
    def _compute_partner_domains(self):
        """Override computed domains from the OCA module to allow selecting
        any child address regardless of its 'type'. We don't modify the
        original module; instead we inherit and replace the compute here.
        """
        for partner in self:
            # If company setting allows any partner, keep empty domains
            if getattr(self.env.company, "contact_address_default_allow_all_partners", False):
                partner.partner_delivery_domain = []
                partner.partner_invoice_domain = []
                partner.partner_contact_domain = []
                continue
            base_domain = [("id", "child_of", partner.commercial_partner_id.ids)]
            # Do not filter by 'type' so all child addresses are selectable
            partner.partner_delivery_domain = base_domain
            partner.partner_invoice_domain = base_domain
            partner.partner_contact_domain = base_domain



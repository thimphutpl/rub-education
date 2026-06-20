# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class GrantType(Document):

	def validate(self):
		self.validate_abbr()

	def validate_abbr(self):
		if not self.abbr:
			self.abbr = "".join(c[0] for c in self.grant_type.split()).upper()

		self.abbr = self.abbr.strip()

		if not self.abbr.strip():
			frappe.throw(_("Abbreviation is mandatory"))

		if frappe.db.sql("select abbr from `tabGrant Type` where name!=%s and abbr=%s", (self.name, self.abbr)):
			frappe.throw(_("Abbreviation already used for another grant type"))

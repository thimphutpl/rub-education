# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Module(Document):
	def validate(self):
		self.validate_assessment()

	@frappe.whitelist()
	def validate_assessment(self):
		total = 0
		for a in self.assessment_item:
			total += flt(a.weightage)
		if flt(total) != 100:
			# frappe.throw("Total Weightage must be 100%")
			pass

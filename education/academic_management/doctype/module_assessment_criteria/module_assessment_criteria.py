# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ModuleAssessmentCriteria(Document):
	def validate(self):
		self.validate_assessment()
		self.validate_duplicate()
	
	def validate_duplicate(self):
		if frappe.db.exists("Module Assessment Criteria", {
			"college": self.college,
			"academic_term": self.academic_term,
			"programme": self.programme,
			"module": self.module,
			"name": ["!=", self.name],
			"docstatus":1
		}):
			frappe.throw("Record already exists for the selected combination.")

	@frappe.whitelist()
	def validate_assessment(self):
		total = 0
		for a in self.assessment_item:
			total += flt(a.weightage)
		if flt(total) != 100:
			frappe.throw("Total Weightage must be 100%")

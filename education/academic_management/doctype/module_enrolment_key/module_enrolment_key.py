# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ModuleEnrolmentKey(Document):
	def validate(self):
		self.check_duplicate()
	
	def check_duplicate(self):
		if frappe.db.exists("Module Enrolment Key", {"college": self.college, "programme": self.programme, "academic_term": self.academic_term, "module": self.module, "docstatus": ["<", 2], "student_batch": self.student_batch, "student_section": self.student_section, "name": ["!=", self.name]}):
			frappe.throw("""Module Enrolment Key <b><a href="/app/module-enrolment-key/{0}">{0}</a></b> already exists for the selected details.""".format(frappe.db.get_value("Module Enrolment Key", {"college": self.college, "programme": self.programme, "academic_term": self.academic_term, "module": self.module, "docstatus": ["<", 2], "student_batch": self.student_batch, "student_section": self.student_section, "name": ["!=", self.name]})))


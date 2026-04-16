# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ResultEntry(Document):
	def validate(self):
		self.check_result_remarks()

	def check_result_remarks(self):

		if self.no_of_modules_failed >= 3:
			self.status = "Failed"
			self.status_remark = "Semester Repeat"
		else:
			self.status = "Passed"
		
		if self.status == "Passed" and self.no_of_modules_failed >0:
			self.status_remark = "Passed with module repeat"

		


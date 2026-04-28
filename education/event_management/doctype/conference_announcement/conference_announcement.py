# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ConferenceAnnouncement(Document):
	def validate(self):
		self.validate_from_to_dates()
	def validate_from_to_dates(self):
		if self.start_date > self.end_date:
			frappe.throw("From Date cannot be after To Date")

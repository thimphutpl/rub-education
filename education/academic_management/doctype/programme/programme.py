# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Programme(Document):
	def validate(self):
		if len(self.programme_record) == 0:
			self.update_programme_record()

	def update_programme_record(self):
		if not frappe.db.exists("Programme Record History", {"parent": self.name, "name": self.name}):
			self.append(
				"programme_record",
				{
					"programme_name": self.programme_name,
					"approval_date": self.programme_approval_date,
					"programme_leader": self.programme_leader,
					"apmr_date": self.programme_apmr_date,
					"ccr_date": self.programme_ccr_date,
				},
			)

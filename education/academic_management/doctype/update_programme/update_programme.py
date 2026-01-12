# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UpdateProgramme(Document):
	def validate(self):
		self.validate_fields()

	def validate_fields(self):
		pass

	def on_submit(self):
		self.update_programme_master()

	def on_cancel(self):
		self.update_programme_master(cancel=True)
	
	def update_programme_master(self, cancel=False):
		programme_master = frappe.get_doc("Programme Master", self.old_programme)
		programme_master.programme_name = self.new_programme_name if not cancel else self.old_programme_name
		programme_master.programme_abbreviation = self.new_programme_abbreviation if not cancel else self.old_programme_abbreviation
		programme_master.programme_description = self.new_programme_description if not cancel else self.old_programme_description
		programme_master.programme_approval_date = self.new_programme_approval_date if not cancel else self.old_programme_approval_date
		programme_master.programme_ccr_date = self.new_programme_ccr_date if not cancel else self.old_programme_ccr_date
		programme_master.programme_apmr_date = self.new_programme_apmr_date if not cancel else self.old_programme_apmr_date
		programme_master.upload_approved_dpd = self.upload_approved_dpd if not cancel else self.old_approved_dpd
		programme_master.set("colleges", [])
		if not cancel:
			for college in self.new_colleges:
				row = programme_master.append("colleges", {})
				row.company = college.company
				row.programme_leader = college.programme_leader
				row.programme_leader_name = college.programme_leader_name
				row.from_date = college.from_date
				row.to_date = college.to_date
		else:
			for college in self.colleges:
				row = programme_master.append("colleges", {})
				row.company = college.company
				row.programme_leader = college.programme_leader
				row.programme_leader_name = college.programme_leader_name
				row.from_date = college.from_date
				row.to_date = college.to_date
		programme_master.programme_description = self.new_programme_description
		programme_master.sync_programme_history(update = True)
		programme_master.save()

	@frappe.whitelist()
	def get_old_programme_details(self):
		doc = frappe.get_doc("Programme Master", self.old_programme)
		for item in doc.colleges:
			row = self.append("colleges", {})
			row.company = item.company
			row.programme_leader = item.programme_leader
			row.from_date = item.from_date
			row.to_date = item.to_date
			
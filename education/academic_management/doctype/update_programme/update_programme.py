# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re

class UpdateProgramme(Document):
	def validate(self):
		self.validate_fields()

	def validate_fields(self):
		if not bool(re.match("^[A-Za-z0-9]+$", self.new_programme_name)):
			frappe.throw("Special Characters not allowed in New Programme Name.")

	def on_submit(self):
		self.update_programme_master()
		self.new_programme = self.new_programme_name

	def on_cancel(self):
		self.update_programme_master(cancel=True)
		self.new_programme = None
	
	def update_programme_master(self, cancel=False):
		old_name = self.old_programme
		new_name = self.new_programme_name if not cancel else self.old_programme_name
		frappe.rename_doc("Programme Master", old_name, new_name)
		programme_master = frappe.get_doc("Programme Master", new_name)
		programme_master.abbreviation = self.new_programme_abbreviation if not cancel else self.old_programme_abbreviation
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
		programme_master.programme_name = self.new_programme_name if not cancel else self.old_programme_name
		programme_master.save()
		# programme_master.db_set("programme_name", self.new_programme_name if not cancel else self.old_programme_name)				
		# if cancel:
		# 	# frappe.db.sql("delete from `tabProgramme Record History` where programme_link = '{}'".format(self.new_programme_name+ " - " + str(self.new_programme_approval_date).split("-")[0]))
		# 	if frappe.db.exists("Programme", self.new_programme_name+ " - " + str(self.new_programme_approval_date).split("-")[0]):
		# 		programme = frappe.get_doc("Programme", self.new_programme_name+ " - " + str(self.new_programme_approval_date).split("-")[0])
		# 		if programme.docstatus == 1:
		# 			programme.cancel()
		# 		frappe.delete_doc("Programme", self.new_programme_name+ " - " + str(self.new_programme_approval_date).split("-")[0])
		if cancel:
			programme_name = (
				self.new_programme_name
				+ " - "
				+ str(self.new_programme_approval_date).split("-")[0]
			)

			if frappe.db.exists("Programme", programme_name):
				programme = frappe.get_doc("Programme", programme_name)

				# 🧹 STEP 1 — BREAK THE LINK (CRITICAL)
				programme.db_set("programme_master", None)

				# 🧹 STEP 2 — also clear child history link
				frappe.db.sql(
					"""
					update `tabProgramme Record History`
					set programme_link = NULL
					where programme_link = %s
					""",
					programme_name,
				)

				# 🧹 STEP 3 — cancel if submitted
				if programme.docstatus == 1:
					programme.cancel()

				# 🧹 STEP 4 — now safe to delete
				frappe.delete_doc("Programme", programme_name)
				prog_name = self.new_programme_name + " - " + str(self.new_programme_approval_date).split("-")[0]

				# remove child history rows
				programme_master = frappe.get_doc("Programme Master", self.old_programme_name)

				rows_to_remove = [
					d for d in programme_master.programme_record
					if d.programme_name == prog_name
				]

				for d in rows_to_remove:
					programme_master.remove(d)

				programme_master.save(ignore_permissions=True)
		if not cancel:
			programme_master.sync_programme_history(update = True)


	@frappe.whitelist()
	def get_old_programme_details(self):
		doc = frappe.get_doc("Programme Master", self.old_programme)
		for item in doc.colleges:
			row = self.append("colleges", {})
			row.company = item.company
			row.programme_leader = item.programme_leader
			row.from_date = item.from_date
			row.to_date = item.to_date
			
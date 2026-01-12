# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ProgrammeMaster(Document):
	def validate(self):
		if len(self.programme_record) == 0:
			self.update_programme_record()
		self.sync_programme_history()


	# @frappe.whitelist()
	# def validate_assessment(self):
	# 	total = 0
	# 	for a in self.assessment_item:
	# 		total += flt(a.weightage)
	# 	if flt(total) != 100:
	# 		frappe.throw("Total Weightage must be 100%")
			

	def update_programme_record(self):
		if not frappe.db.exists("Programme Record History", {"parent": self.name, "programme_name": self.programme_name}):
			self.append(
				"programme_record",
				{
					"programme_name": self.programme_name,
					"approval_date": self.programme_approval_date,
					"abbreviation": self.abbreviation,
					"apmr_date": self.programme_apmr_date,
					"ccr_date": self.programme_ccr_date,
					"programme_description": self.programme_description,
				},
			)

	@frappe.whitelist()
	def sync_programme_history(self, update = False):
		for prog in self.programme_record:
			if not prog.programme_link:
				if frappe.db.exists("Programme", {"name": prog.programme_name}):
					prog.programme_link = prog.programme_name
				else:
					programme = frappe.new_doc("Programme")
					programme.programme_name = prog.programme_name
					programme.abbreviation = prog.abbreviation
					programme.programme_approval_date = prog.approval_date
					programme.programme_apmr_date = prog.apmr_date
					programme.programme_ccr_date = prog.ccr_date
					programme.programme_description = prog.programme_description
					if self.name == programme.name:
						for c in self.colleges:
							if not frappe.db.exists("Colleges", {"parent": programme.name, "parenttype": "Programme"}):
								row = programme.append("colleges", {})
								row.programme_leader = c.programme_leader
								row.programme_leader_name = c.programme_leader_name
								row.company = c.company
								row.from_date = c.from_date
								row.to_date = c.to_date
							else:
								for row in  programme.colleges:
									if row.company == c.company:
										row.programme_leader = c.programme_leader
										row.programme_leader_name = c.programme_leader_name
										row.from_date = c.from_date
										row.to_date = c.to_date
					programme.insert()
					programme.submit()
					# for a in self.
					prog.programme_link = programme.name
			else:
				if self.name == prog.programme_link:
					old = self.get_doc_before_save()
					if old:
						if (old.abbreviation != self.abbreviation) or not prog.abbreviation:
							prog.abbreviation = self.abbreviation
						if (old.programme_approval_date != self.programme_approval_date) or not prog.approval_date:
							prog.approval_date = self.programme_approval_date
						# if (old.programme_leader != self.programme_leader) or not prog.programme_leader:
						# 	prog.programme_leader = self.programme_leader
						if (old.programme_apmr_date != self.programme_apmr_date) or not prog.apmr_date:
							prog.apmr_date = self.programme_apmr_date
						if (old.programme_ccr_date != self.programme_ccr_date) or not prog.ccr_date:
							prog.ccr_date = self.programme_ccr_date
						if (old.programme_description != self.programme_description) or not prog.programme_description:
							prog.programme_description = self.programme_description
						if (old.upload_approved_dpd != self.upload_approved_dpd) or not prog.attached_dpd:
							prog.attached_dpd = self.upload_approved_dpd
						
						if frappe.db.exists("Programme", {"name": prog.programme_link}):
							programme = frappe.get_doc("Programme", prog.programme_link)
							programme.abbreviation = prog.abbreviation
							programme.programme_approval_date = prog.approval_date
							# programme.programme_leader = prog.programme_leader
							programme.programme_apmr_date = prog.apmr_date
							programme.programme_ccr_date = prog.ccr_date
							programme.programme_description = prog.programme_description
							programme.upload_approved_dpd = prog.attached_dpd
							programme.programme_master = self.name
							for c in self.colleges:
								for row in  programme.colleges:
									if row.company == c.company:
										row.programme_leader = c.programme_leader
										row.programme_leader_name = c.programme_leader_name
										row.from_date = c.from_date
										row.to_date = c.to_date
								if not frappe.db.exists("Colleges", {"parent": programme.name, "parenttype": "Programme", "company": c.company}):
									row = programme.append("colleges", {})
									row.company = c.company
									row.programme_leader = c.programme_leader
									row.programme_leader_name = c.programme_leader_name
									row.from_date = c.from_date
									row.to_date = c.to_date
							programme.save()
			if update:
				prog.save()

					
# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FullPaper(Document):
	def after_insert(self):
		if not self.workflow_state or self.workflow_state == "Draft":
			self.db_set("workflow_state", "Waiting for Review")

	@frappe.whitelist()
	def has_given_mark(self):
		# privileged_roles = ["Administrator", "System Manager", "Super Admin"]
		# user_roles = frappe.get_roles(frappe.session.user)
		# if ("SSO" not in user_roles) and not any(role in privileged_roles for role in user_roles):
		# 	return {"can_give_marks": False}
		pm = frappe.qb.DocType("Full Paper Panel Mark")
		full_paper_panel_mark = (
			frappe.qb.from_(pm)
			.select(pm.name)
			.where(
				(pm.docstatus < 2) &
				(pm.source_doctype == self.doctype) &
			    (pm.source_name == self.name) &
				(pm.owner == frappe.session.user)
			)
		).run(as_dict=True)

		return {
			# "can_give_marks": not bool(full_paper_panel_mark),
			"has_given_mark": bool(full_paper_panel_mark),
			"full_paper_panel_mark_name": full_paper_panel_mark[0]["name"] if full_paper_panel_mark else None
		}


	@frappe.whitelist()
	def update_panel_summary(self):
		theme = self.theme
		if not theme:
			return {
				"total_panel_member": 0,
				"total_mark_submitted": 0,
				"waiting_for_review": 0
			}

		total_panel = frappe.db.count("Panel Member", {"parent": theme})
		submitted = frappe.db.count(
			"Full Paper Panel Mark",
			{
				"theme": theme,
				"docstatus": 1,
				"source_name": self.name
			}
		)
		pending = total_panel - submitted if total_panel > submitted else 0

		return {
			"total_panel_member": total_panel,
			"total_mark_submitted": submitted,
			"waiting_for_review": pending
		}
	@frappe.whitelist()
	def calculate_total_mark(self):
		total = 0.0
		for row in self.master_evaluation_criteria_full_paper:
			total += float(row.avg_weight or 0)

		# Optional: store it in a field on the parent
		# self.db_set("total_mark", total)
		return total	
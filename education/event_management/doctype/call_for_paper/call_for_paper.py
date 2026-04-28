# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class CallForPaper(Document):
	def after_insert(self):
		if not self.workflow_state or self.workflow_state == "Draft":
			self.db_set("workflow_state", "Waiting for Review")
	
	
	@frappe.whitelist()
	def has_given_mark(self):
		pm = frappe.qb.DocType("Call For Paper Panel Mark")
		call_for_paper_panel_mark = (
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
			# "can_give_marks": not bool(panel_mark),
			"has_given_mark": bool(call_for_paper_panel_mark),
			"call_for_paper_panel_mark_name": call_for_paper_panel_mark[0]["name"] if call_for_paper_panel_mark else None
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
			"Call For Paper Panel Mark",
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
		for row in self.master_evaluation_criteria_call_for_paper:
			total += float(row.avg_weight or 0)
		return total






@frappe.whitelist()
def get_permission_query_conditions(user):
    """Return permission conditions for Call For Paper"""
    if not user:
        user = frappe.session.user
    
    roles = frappe.get_roles(user)
    
    # Admin sees everything
    if "Administrator" in roles or "System Manager" in roles:
        return ""
    
    # Panel Member sees Call for Papers from their themes
    if "Panel Member" in roles:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        
        if employee:
            # Get themes where user is a panel member
            return """`tabCall For Paper`.`theme` IN (
                SELECT ct.`theme` 
                FROM `tabConference Theme` ct 
                JOIN `tabPanel Member` pm ON ct.`theme` = pm.`parent`
                WHERE pm.`employee` = '%s'
            )""" % employee
        return "1=0"
    
    return "1=0"
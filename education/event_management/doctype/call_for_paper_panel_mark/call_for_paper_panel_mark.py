# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CallForPaperPanelMark(Document):
	
	def on_submit(self):
		papers = frappe.get_all(
			"Call For Paper",
			filters={
				"conference": self.conference
			},
			limit=1,
			fields=["name"]
		)

		if not papers:
			frappe.throw(f"No Call For Paper found for Conference {self.conference} and participant {self.email}")

		parent = frappe.get_doc("Call For Paper", papers[0].name)
		call_for_paper_panel_marks = frappe.get_all(
			"Call For Paper Panel Mark",
			filters={"conference": self.conference, "docstatus": 1},
			fields=["name"]
		)
		criteria_dict = {}
		for pm in call_for_paper_panel_marks:
			doc = frappe.get_doc("Call For Paper Panel Mark", pm.name)
			for row in doc.panel_evaluation_criteria_call_for_paper:
				crit = row.criteria
				if crit not in criteria_dict:
					criteria_dict[crit] = {
						"score": float(row.score),
						"weight_marks": [],"remark": []
					}
				criteria_dict[crit]["weight_marks"].append(float(row.weight_marks or 0))
				criteria_dict[crit]["remark"].append(row.remark or "")
		

		parent.master_evaluation_criteria_call_for_paper = []
		for crit,scores in criteria_dict.items():
			parent.append("master_evaluation_criteria_call_for_paper", {
				"criteria": crit,
				"score": scores["score"],
				"avg_weight": sum(scores["weight_marks"]) / len(scores["weight_marks"]) if scores["weight_marks"] else 0,
				"remark": "\n".join(
			[r for r in scores["remark"] if r]   
		)
		
			})

		total_panel = frappe.db.count("Panel Member", {"parent": parent.theme})
		submitted = len(call_for_paper_panel_marks)
		pending = total_panel - submitted

		if submitted >= total_panel:
			parent.db_set("workflow_state", "Marks Submitted")	
 
		parent.save()
@frappe.whitelist()
def get_conference_info(source_doctype, source_name):

	existing = frappe.db.get_value(
		"Call for Paper Panel Mark",
		{
			"source_doctype": source_doctype,
			"source_name": source_name,
			"owner": frappe.session.user 
		},
		"name"
	)

	if existing:
		return {
			"doctype": "Call For Paper Panel Mark",
			"name": existing
		}

	call_for_paper_panel_mark = frappe.new_doc("Call For Paper Panel Mark")
	call_for_paper_panel_mark.source_doctype = source_doctype
	call_for_paper_panel_mark.source_name = source_name

	if source_doctype == "Call For Paper":
		conf = frappe.get_doc("Call For Paper", source_name)
		call_for_paper_panel_mark.conference = conf.conference
		call_for_paper_panel_mark.theme = conf.theme

	call_for_paper_panel_mark.insert(ignore_permissions=True)

	return {
		"doctype": "Call For Paper Panel Mark",
		"name": call_for_paper_panel_mark.name
	}

@frappe.whitelist()
def get_permission_query_conditions(user):
	user = user or frappe.session.user
	user_roles = frappe.get_roles(user)
	if any(role in ["Administrator", "System Manager", "Super Admin"] for role in user_roles):
		return None

	# Panel Members see only records for themes they belong to
	return f"`tabCall For Paper Panel Mark`.owner = '{user}'"

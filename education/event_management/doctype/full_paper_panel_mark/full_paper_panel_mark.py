# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FullPaperPanelMark(Document):
	def on_submit(self):
		# Find the Call For Paper for this conference and participant
		papers = frappe.get_all(
			"Full Paper",
			filters={
				"conference": self.conference
			},
			limit=1,
			fields=["name"]
		)

		if not papers:
			frappe.throw(f"No Full Paper found for Conference {self.conference} and participant {self.email}")

		parent = frappe.get_doc("Full Paper", papers[0].name)

		# Now you can continue processing marks
		full_paper_panel_marks = frappe.get_all(
			"Full Paper Panel Mark",
			filters={"conference": self.conference, "docstatus": 1},
			fields=["name"]
		)

		# Aggregate marks as you already have
		criteria_dict = {}
		for pm in full_paper_panel_marks:
			doc = frappe.get_doc("Full Paper Panel Mark", pm.name)
			for row in doc.evaluation_criteria_full_paper:
				crit = row.criteria
				if crit not in criteria_dict:
					criteria_dict[crit] = {
						"score": float(row.score),
						"weight_marks": [],  "remark": []
					}

				criteria_dict[crit]["weight_marks"].append(float(row.weight_marks or 0))
				criteria_dict[crit]["remark"].append(row.remark or "")

		parent.master_evaluation_criteria_full_paper = []

		for crit, scores in criteria_dict.items():
			parent.append("master_evaluation_criteria_full_paper", {
				"criteria": crit,
				"score": scores["score"],
				"avg_weight": sum(scores["weight_marks"]) / len(scores["weight_marks"]) if scores["weight_marks"] else 0,
				"remark": "\n".join(
			[r for r in scores["remark"] if r]   
		)
			   
			   
			})
		total_panel = frappe.db.count("Panel Member", {"parent": parent.theme})
		# Total marks submitted
		submitted = len(full_paper_panel_marks)
		pending = total_panel - submitted

		# parent.db_set("total_panel_member", total_panel)
		# parent.db_set("total_mark_submitted", submitted)
		# parent.db_set("waiting_for_review", pending)

		# --- Workflow update ---
		if submitted >= total_panel:
			# All panel members submitted → set workflow state
			parent.db_set("workflow_state", "Marks Submitted")	
 
		parent.save()




# @frappe.whitelist()
# def get_conference_info(source_doctype, source_name):

# 	existing = frappe.db.get_value(
# 		"Full Paper Panel Mark",
# 		{
# 			"source_doctype": source_doctype,
# 			"source_name": source_name,
			
# 		},
# 		"name"
# 	)

# 	if existing:
# 		return {
# 			"doctype": "Full Paper Panel Mark",
# 			"name": existing
# 		}

# 	full_paper_panel_mark = frappe.new_doc("Full Paper Panel Mark")
# 	full_paper_panel_mark.source_doctype = source_doctype
# 	full_paper_panel_mark.source_name = source_name


# 	if source_doctype == "Full Paper":
# 		paper = frappe.get_doc("Full Paper", source_name)
# 		full_paper_panel_mark.full_paper = paper.name
# 		# full_paper_panel_mark.conference = paper.conference
# 		full_paper_panel_mark.theme = paper.theme

# 	full_paper_panel_mark.insert(ignore_permissions=True)
# 	return {
# 		"doctype": "Full Paper Panel Mark",
# 		"name": full_paper_panel_mark.name
# 	}
@frappe.whitelist()
def get_conference_info(source_doctype, source_name):
    # Check if current user already has a mark for this paper
    existing = frappe.db.get_value(
        "Full Paper Panel Mark",
        {
            "source_doctype": source_doctype,
            "source_name": source_name,
            "owner": frappe.session.user  # <-- only fetch this user's mark
        },
        "name"
    )

    if existing:
        return {
            "doctype": "Full Paper Panel Mark",
            "name": existing
        }

    # If not exists, create a new document for the current user
    full_paper_panel_mark = frappe.new_doc("Full Paper Panel Mark")
    full_paper_panel_mark.source_doctype = source_doctype
    full_paper_panel_mark.source_name = source_name

    if source_doctype == "Full Paper":
        paper = frappe.get_doc("Full Paper", source_name)
        full_paper_panel_mark.full_paper = paper.name
        full_paper_panel_mark.theme = paper.theme

    full_paper_panel_mark.insert(ignore_permissions=True)
    return {
        "doctype": "Full Paper Panel Mark",
        "name": full_paper_panel_mark.name
    }

@frappe.whitelist()
def get_permission_query_conditions(user):
	user = user or frappe.session.user
	user_roles = frappe.get_roles(user)
	if any(role in ["Administrator", "System Manager", "Super Admin"] for role in user_roles):
		return None

	# Panel Members see only records for themes they belong to
	return f"`tabCall For Paper Panel Mark`.owner = '{user}'"

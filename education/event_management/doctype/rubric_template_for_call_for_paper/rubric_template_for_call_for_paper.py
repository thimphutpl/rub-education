# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe
class RubricTemplateForCallForPaper(Document):
	pass
@frappe.whitelist()
def get_abstract_rubric(theme_name):
    """
    Fetch active abstract rubric rows based on theme.
    """
    rubric_docs = frappe.get_list(
        "Rubric Template For Call For Paper",
        filters={"theme": theme_name, "docstatus": 1},
        fields=["name"]
    )


    if not rubric_docs:
        return []

    rubric_name = rubric_docs[0].name
    criteria_rows = frappe.get_all(
        "Evaluation Criteria Call For Paper",
        filters={"parent": rubric_name},
        fields=["criteria","score"],
        order_by="idx asc"
    )

    for row in criteria_rows:
        for key in ["criteria","score","weight_marks"]:
            if key not in row or not row[key]:
                row[key] = ""

    return criteria_rows

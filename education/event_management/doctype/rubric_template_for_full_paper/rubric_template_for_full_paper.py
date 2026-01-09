# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from frappe.model.document import Document
import frappe
class RubricTemplateForFullPaper(Document):
	pass
@frappe.whitelist()
def get_full_paper_rubric(theme_name):
    """
    Fetch active full paper rubric rows based on theme.
    """
    rubric_docs = frappe.get_list(
        "Rubric Template For Full Paper",
        filters={"theme": theme_name, "docstatus": 1},
        fields=["name"]
    )


    if not rubric_docs:
        return []

    rubric_name = rubric_docs[0].name
    criteria_rows = frappe.get_all(
        "Evaluation Criteria Full Paper",
        filters={"parent": rubric_name},
        fields=["criteria", "weight_marks", "remark"],
        order_by="idx asc"
    )

    for row in criteria_rows:
        for key in ["criteria", "weight_marks", "remark"]:
            if key not in row or not row[key]:
                row[key] = ""

    return criteria_rows

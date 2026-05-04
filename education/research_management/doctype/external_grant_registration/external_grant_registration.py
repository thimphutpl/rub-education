# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ExternalGrantRegistration(Document):
	pass

@frappe.whitelist()
def get_researcher_details(investigator_type, principal_investigator):
    """Get researcher details including name, email, and gender"""
    if not investigator_type or not principal_investigator:
        frappe.throw(_("Researcher Type and Researcher ID are required"))
    
    details = {
        "principal_investigator": principal_investigator,
        "pi_name": "",
    }
    
    if investigator_type == "Employee":
        employee = frappe.db.get_value(
            "Employee", 
            principal_investigator, 
            ["employee_name", "company_email", "personal_email", "gender", "cell_number", "company"], 
            as_dict=True
        )
        if employee:
            # Prefer company email, fallback to personal email
            email = employee.get("company_email") or employee.get("personal_email")
            details.update({
                "pi_name": employee.get("employee_name", ""),
            })
        else:
            frappe.throw(_("Employee {0} not found").format(principal_investigator))
    
    elif investigator_type == "Student":
        student = frappe.db.get_value(
            "Student", 
            principal_investigator, 
            ["student_name", "student_email_id", "gender", "student_mobile_number", "company"], 
            as_dict=True
        )
        if student:
            details.update({
                "pi_name": student.get("student_name", ""),
            })
        else:
            frappe.throw(_("Student {0} not found").format(principal_investigator))
    
    return details
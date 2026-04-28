import frappe

@frappe.whitelist()
def get_signed_in_user_college(user):
    user_roles = frappe.get_roles(user)
    college = None
    if "Student" in user_roles:
        college = frappe.db.get_value("Student", {"user": user}, "company")
    elif "Employee" in user_roles:
        college = frappe.db.get_value("Employee", {"user_id": user}, "company")
    if not college:
        college = ""
    return college
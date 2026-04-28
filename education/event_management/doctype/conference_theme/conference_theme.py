# Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
import frappe
from frappe.model.document import Document

class ConferenceTheme(Document):

	pass
	
@frappe.whitelist()
def panel_member_query(doctype, txt, searchfield, start, page_len, filters):
    """Get employees with Panel Member role"""
    company = filters.get("company")
    
    # Get users with Panel Member role
    users = frappe.get_all("Has Role", {"role": "Panel Member"}, pluck="parent")
    
    if not users:
        return []
    
    # Get employees
    return frappe.db.sql("""
        SELECT name, employee_name
        FROM `tabEmployee`
        WHERE company = %s
            AND status = 'Active'
            AND user_id IN %s
            AND (name LIKE %s OR employee_name LIKE %s)
        LIMIT %s OFFSET %s
    """, (company, tuple(users), f"%{txt}%", f"%{txt}%", page_len, start))
# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class FacultyAttendance(Document):
	pass

@frappe.whitelist()
def create_attendance(dt, dn):
    event = frappe.get_doc(dt, dn)
    if not event.get("faculty_register") or len(event.faculty_register) == 0:
        frappe.throw(_("Cannot create attendance - Faculty Register is empty. Please add students first."))    
    attendance = frappe.new_doc("Faculty Attendance")
    attendance.event = event.name
    attendance.college = event.college
    attendance.attendance_date = event.start_date.date() if event.start_date else frappe.utils.today()
    for row in event.faculty_register:
        if not row.faculty_email:
            continue 
        attendance.append("faculty_attendance_list", {
            "faculty": row.faculty,
            "faculty_name": row.faculty_name,
            
         
        })
    attendance.insert(ignore_permissions=True)
    return {
        "status": "success",
        "attendance_name": attendance.name
    }

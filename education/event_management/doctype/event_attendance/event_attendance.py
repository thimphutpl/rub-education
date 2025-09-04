# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class EventAttendance(Document):
	pass
@frappe.whitelist()
def create_attendance(dt, dn):
    event = frappe.get_doc(dt, dn)
    # if event.registration_type != "Class":
    #     frappe.throw(_("Attendance can only be created for class events."))

    if not event.get("student_register") or len(event.student_register) == 0:
        frappe.throw(_("Cannot create attendance - Student Register is empty. Please add students first."))    
    attendance = frappe.new_doc("Event Attendance")
    attendance.event = event.name
    attendance.attendance_date = event.start_date.date() if event.start_date else frappe.utils.today()
    for row in event.student_register:
        if not row.student_email:
            continue 
        attendance.append("attendance_list", {
            "student": row.student,
            "student_email": row.student_email,
            "student_name": row.student_name,
         
        })
    attendance.insert(ignore_permissions=True)
    return {
        "status": "success",
        "attendance_name": attendance.name
    }

# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EventAttendance(Document):
	pass

@frappe.whitelist()
def create_attendance(dt, dn):
    event = frappe.get_doc(dt, dn)

    if event.registration_type != "Faculty":
        frappe.throw(_("Attendance can only be created for Faculty events."))

    attendance = frappe.new_doc("Event Attendance")
    attendance.event = event.name
    attendance.attendance_date = event.start_date.date() if event.start_date else frappe.utils.today()

    for row in event.event_register:
        if not row.faculty_email:
            continue
        attendance.append("attendance_list", {
            "student_name": row.faculty_name
        })
    attendance.insert(ignore_permissions=True)

    return {
        "status": "success",
        "attendance_name": attendance.name
    }


# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class FacultyAttendance(Document):
	def on_submit(self):
		self.create_attendance_entries()
	def create_attendance_entries(self):
		created_count = 0
		skipped_count = 0

		for row in self.faculty_attendance_list:

			if not row.faculty:
				skipped_count += 1
				continue

			existing_entry = frappe.db.exists("Attendance Entry", {
				"student_code": row.faculty,
				"posting_date": self.posting_date,
				"transaction_name": self.name
			})

			if existing_entry:
				skipped_count += 1
				continue

			try:
				attendance_entry = frappe.get_doc({
					"doctype": "Attendance Entry",
					"posting_date": self.posting_date,
					"student_code": row.faculty,
					"student_name": row.faculty_name,
					"attendance": row.status,
					"college": self.college,
					"transaction_type": "Faculty Attendance",
					"transaction_name": self.name,
				})

				attendance_entry.insert()
				attendance_entry.submit()

				created_count += 1

			except Exception as e:
				frappe.log_error(
					title="Attendance Entry Creation Error",
					message=f"faculty: {row.faculty} | Error: {str(e)}"
				)

				frappe.msgprint(
					_(f"Error creating attendance entry for student {row.faculty}: {str(e)}"),
					indicator='orange',
					alert=True
				)

		frappe.msgprint(
			_(f"Created: {created_count}, Skipped: {skipped_count}"),
			indicator='green'
		)

@frappe.whitelist()
def create_attendance(dt, dn):
    event = frappe.get_doc(dt, dn)
    if not event.get("faculty_register") or len(event.faculty_register) == 0:
        frappe.throw(_("Cannot create attendance - Staff Register is empty. Please add Staff first."))    
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

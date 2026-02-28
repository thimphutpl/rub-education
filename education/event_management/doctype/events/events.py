# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states
class Events(Document):
	# def validate(self):
	# 	validate_workflow_states(self)
	# 	if self.workflow_state != "Approved":
	# 		notify_workflow_states(self)
	# def on_submit(self):
	# 	notify_workflow_states(self)
	# def on_cancel(self):
	# 	notify_workflow_states(self)
	@frappe.whitelist()
	def has_attendance(self) -> dict[str, bool]:
		ea = frappe.qb.DocType("Event Attendance")
		event_attendance = (
			frappe.qb.from_(ea)
			.select(ea.name)
			.where(
				(ea.docstatus < 2)
				& (ea.event == self.name)
			)
		).run(as_dict=True)

		return {
			"has_attendance": bool(event_attendance)
		}


@frappe.whitelist()
def get_student_college(user=None):
	"""
	Returns the College of the logged-in Student
	"""
	if not user:
		user = frappe.session.user

	student = frappe.get_all(
		"Student",
		filters={"user": user, "status": "Active"},
		fields=["company"],
		limit_page_length=1
	)

	if student:
		return student[0].company
	return None
@frappe.whitelist()
def get_students_by_filters(filters):
	import json
	filters = json.loads(filters) if isinstance(filters, str) else filters

	all_students = []

	for f in filters:
		# Skip rows without complete filter
		if not (f.get("programme") and f.get("year") and f.get("semester")):
			continue

		# Ensure programme is always a list
		programme_list = f["programme"] if isinstance(f["programme"], list) else [f["programme"]]
		students = frappe.get_all(
			"Student",
			filters={
				"programme": ["in", programme_list],
				"year": f["year"],
				"semester": f["semester"],
				"status": "Active"
			},
			fields=["name", "student_email_id", "first_name", "last_name"]
		)

		all_students.extend(students)

	return all_students

@frappe.whitelist()
def get_programmes_by_college(doctype, txt, searchfield, start, page_len, filters):
    """
    Return Programme names filtered by selected college in child table.
    """
    college = filters.get("college")
    if not college:
        return []

    # Use correct child table column 'college'
    programmes = frappe.db.sql("""
        SELECT DISTINCT p.name
        FROM `tabProgramme` p
        JOIN `tabColleges` c ON c.parent = p.name
        WHERE c.company = %s
        AND p.name LIKE %s
        ORDER BY p.name
        LIMIT %s, %s
    """, (college, f"%{txt or ''}%", start, page_len), as_list=True)

    if not programmes:
        return []

    return programmes
@frappe.whitelist()
def get_faculty_by_college(college):
    """
    Returns employees (faculty) filtered by company/college
    """
    if not college:
        return []

    faculty = frappe.get_all(
        "Employee",
        filters={"company": college},
        fields=["name", "user_id as email", "employee_name as full_name"]
    )
    return faculty
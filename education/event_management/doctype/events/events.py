# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states
class Events(Document):
	def validate(self):
		# validate_workflow_states(self)
		# notify_workflow_states(self)
		self.validate_from_to_dates()
	def on_submit(self):
		pass
		# notify_workflow_states(self)
	def on_cancel(self):
		notify_workflow_states(self)
	def validate_from_to_dates(self):
		if self.start_date > self.end_date:
			frappe.throw("From Date cannot be after To Date")
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
	def has_faculty_attendance(self) -> dict[str, bool]:
		ea = frappe.qb.DocType("Faculty Attendance")
		event_faculty_attendance = (
			frappe.qb.from_(ea)
			.select(ea.name)
			.where(
				(ea.docstatus < 2)
				& (ea.event == self.name)
			)
		).run(as_dict=True)

		return {
			"has_faculty_attendance": bool(event_faculty_attendance)
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
# @frappe.whitelist()
# def get_students_by_filters(filters):

# 	import json
# 	filters = json.loads(filters) if isinstance(filters, str) else filters

# 	all_students = []

# 	for f in filters:
# 		# Skip rows without complete filter
# 		if not (f.get("programme") and f.get("year") and f.get("semester")):
# 			continue

# 		# Ensure programme is always a list
# 		programme_list = f["programme"] if isinstance(f["programme"], list) else [f["programme"]]
# 		students = frappe.get_all(
# 			"Student",
# 			filters={
# 				"programme": ["in", programme_list],
# 				"year": f["year"],
# 				"semester": f["semester"],
# 				"status": "Active"
# 			},
# 			fields=["name", "student_email_id", "first_name", "last_name"]
# 		)

# 		all_students.extend(students)

# 	return all_students
@frappe.whitelist()
def get_students_by_filters(filters=None, company=None):
	import json

	if filters:
		filters = json.loads(filters) if isinstance(filters, str) else filters
	else:
		filters = []

	# ✅ Base filter
	base_filters = {
		"status": "Active"
	}

	if company:
		base_filters["company"] = company

	# ✅ No filters → return all students of that company
	if not filters:
		return frappe.get_all(
			"Student",
			filters=base_filters,
			fields=["name", "student_email_id", "first_name", "last_name"]
		)

	all_students = []

	for f in filters:
		query_filters = base_filters.copy()

		if f.get("programme"):
			programme_list = f["programme"] if isinstance(f["programme"], list) else [f["programme"]]
			query_filters["programme"] = ["in", programme_list]

		if f.get("year"):
			query_filters["year"] = f["year"]

		if f.get("semester"):
			query_filters["semester"] = f["semester"]

		students = frappe.get_all(
			"Student",
			filters=query_filters,
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

@frappe.whitelist()
def get_company_employees():
	user = frappe.session.user
	user_company = frappe.db.get_value("User", user, "company")

	if not user_company:
		frappe.throw("Logged-in user's company is not set.")

	return frappe.get_list("Employee",
		filters={"company": user_company, "status": "Active"},
		fields=["name", "employee_name"]
	)
@frappe.whitelist()
def get_users_by_college(doctype, txt, filters=None, page_length=10, start=0):
	college = filters.get("college") if filters else None
	users = []

	# Get Students
	students = frappe.get_all(
		"Student",
		filters={"college": college, "enabled": 1},
		fields=["name as value", "student_email_id as description"],
		limit_start=start,
		limit_page_length=page_length
	)
	users.extend(students)

	# Get Employees
	employees = frappe.get_all(
		"Employee",
		filters={"company": college, "status": "Active"},
		fields=["name as value", "email as description"],
		limit_start=start,
		limit_page_length=page_length
	)
	users.extend(employees)

	return users   

@frappe.whitelist()
def get_employees_by_role_and_company(doctype, txt, searchfield, start, page_len, filters):
    """Get employees who have users with Event Approval role"""
    
    company = filters.get('company')
    role = filters.get('role', 'Event Approval')
    
    return frappe.db.sql("""
        SELECT 
            e.name,
            e.employee_name,
            e.user_id
        FROM `tabEmployee` e
        INNER JOIN `tabUser` u ON u.name = e.user_id
        INNER JOIN `tabHas Role` hr ON hr.parent = u.name
        WHERE e.company = %s
            AND hr.role = %s
            AND u.enabled = 1
            AND (e.name LIKE %s OR e.employee_name LIKE %s OR e.user_id LIKE %s)
        ORDER BY e.employee_name
        LIMIT %s OFFSET %s
    """, (company, role, f"%{txt}%", f"%{txt}%", f"%{txt}%", page_len, start))

def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	user_roles = frappe.get_roles(user)
	if user == "Administrator" or "System Manager" in user_roles:
		return ""
	if "Event Approval" in user_roles:
		company = frappe.db.get_value("Employee", {"user_id": user}, "company")
		return """(
			`tabEvents`.college = '{0}'
			and `tabEvents`.workflow_state in ('Waiting for Approval','Approved')
		)""".format(company)

	return """(`tabEvents`.owner = '{0}')""".format(user)


import frappe
from frappe import _, msgprint
# from frappe.utils import formatdate
from frappe.utils import getdate

# from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday

# from education.education.doctype.student_attendance.student_attendance import (
# 	get_holiday_list,
# )


def execute(filters=None):
	filters = filters or {}
	if not filters.get("from_date"):
		frappe.throw(_("Please select From Date"))

	if not filters.get("to_date"):
		frappe.throw(_("Please select To Date"))

	if not filters.get("college"):
		msgprint(_("Please select College"), raise_exception=1)

	if not filters.get("academic_term"):
		msgprint(_("Please select Academic Term"), raise_exception=1)

	if not filters.get("module"):
		msgprint(_("Please select module"), raise_exception=1)
	
	if getdate(filters.get("from_date")) > getdate(filters.get("to_date")):
		frappe.throw(_("From Date cannot be greater than To Date"))
	# Date is optional, so check holiday only when Date is selected
	# if filters.get("date"):
	# 	holiday_list = get_holiday_list()

	# 	if holiday_list and is_holiday(holiday_list, filters.get("date")):
	# 		msgprint(
	# 			_("No attendance has been marked for {0} as it is a Holiday").format(
	# 				frappe.bold(formatdate(filters.get("date")))
	# 			)
	# 		)

	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		{
			"label": _("Student ID"),
			"fieldname": "student",
			"fieldtype": "Link",
			"options": "Student",
			"width": 180,
		},
		{
			"label": _("Student Name"),
			"fieldname": "student_name",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			"label": _("Present"),
			"fieldname": "present_students",
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"label": _("Leave"),
			"fieldname": "leave_students",
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"label": _("Absent"),
			"fieldname": "absent_students",
			"fieldtype": "Int",
			"width": 100,
		},
		
		{
			"label": _("Contact Hours"),
			"fieldname": "contact_hours",
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"label": _("Attendance (%)"),
			"fieldname": "attendance",
			"fieldtype": "Percent",
			"width": 100
		},
		{
			"label": _("Status (Min.90%)"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
			
		}
	]
def get_allowed_colleges():
	# Administrator is not restricted by User Permission
	if frappe.session.user == "Administrator":
		return []

	return frappe.get_all(
		"User Permission",
		filters={
			"user": frappe.session.user,
			"allow": "Company",
		},
		pluck="for_value",
	)


def get_effective_college(filters):
	selected_college = filters.get("college")

	# Administrator can select any college
	if frappe.session.user == "Administrator":
		return selected_college

	allowed_colleges = get_allowed_colleges()

	if not allowed_colleges:
		frappe.throw(_("You do not have permission for any College"))

	if selected_college not in allowed_colleges:
		frappe.throw(
			_("You are not permitted to access {0}").format(
				frappe.bold(selected_college)
			)
		)

	return selected_college

def get_data(filters):

	selected_college = get_effective_college(filters)
	# ---------------------------------------------------------
	# 1. Mandatory filters
	# ---------------------------------------------------------

	attendance_filters = {
		
		"college": selected_college,
		"academic_term": filters.get("academic_term"),

		# Module actual fieldname
		"module": filters.get("module"),

		"docstatus": 1,
	}
	# From Date and To Date are mandatory
	attendance_filters["date"] = [
		"between",
		[
			filters.get("from_date"),
			filters.get("to_date"),
		],
	]
	# ---------------------------------------------------------
	# 2. Optional filters
	# ---------------------------------------------------------

	if filters.get("student_group"):
		attendance_filters["student_group"] = filters.get("student_group")

	# if filters.get("module"):
	# 	attendance_filters["module"] = filters.get("module")

	if filters.get("student"):
		attendance_filters["student"] = filters.get("student")

	# ---------------------------------------------------------
	# 3. Fetch Student Attendance directly
	# ---------------------------------------------------------

	attendance_records = frappe.get_all(
		"Student Attendance",
		filters=attendance_filters,
		fields=[
			"student",
			"student_name",
			"status",
			"date",
		],
		order_by="student_name asc, date asc",
	)

	if not attendance_records:
		return []

	# ---------------------------------------------------------
	# 4. Group attendance student-wise
	# ---------------------------------------------------------

	attendance_map = {}

	for attendance in attendance_records:

		if attendance.student not in attendance_map:
			attendance_map[attendance.student] = {
				"student": attendance.student,
				"student_name": attendance.student_name,
				"Present": 0,
				"Leave": 0,
				"Absent": 0,
			}

		if attendance.status == "Present":
			attendance_map[attendance.student]["Present"] += 1

		elif attendance.status == "Leave":
			attendance_map[attendance.student]["Leave"] += 1

		elif attendance.status == "Absent":
			attendance_map[attendance.student]["Absent"] += 1

	# ---------------------------------------------------------
	# 5. Prepare report rows
	# ---------------------------------------------------------

	# contact_hours = get_module_contact_hours(
    # college=selected_college,
    # module=filters.get("module"),
	contact_hours = get_module_contact_hours(
    filters.get("module")



)

	attendance_threshold = frappe.db.get_single_value(
		"Academic Settings",
		"attendance_threshold"
	) or 0
	
	data = []

	# total_present = 0
	# total_leave = 0
	# total_absent = 0
	
	for student in attendance_map.values():

		present = student["Present"]
		leave = student["Leave"]
		absent = student["Absent"]

		# total_present += present
		# total_leave += leave
		# total_absent += absent
		

		# attendance_percentage = 0

		attendance = 0

		if contact_hours:
			attendance = (present / contact_hours) * 100

		status = ""

		if attendance_threshold and attendance < attendance_threshold:
			status = "Shortage"
			

		data.append(
			{
				"student": student["student"],
				"student_name": student["student_name"],
				"present_students": present,
				"leave_students": leave,
				"absent_students": absent,
				"contact_hours": contact_hours,
				# "attendance": round(attendance_percentage, 2),
				"attendance": round(attendance, 2),
				"status": status,
				
			}
		)
	# total_contact_hours = contact_hours * len(attendance_map)

	# total_attendance = 0

	# if total_contact_hours:
	# 	total_attendance = (total_present / contact_hours) * 100

	# total_status = ""

	# if attendance_threshold and total_attendance < attendance_threshold:
	# 	total_status = "Shortage"

	# ---------------------------------------------------------
	# 6. Total row
	# ---------------------------------------------------------

	# if data:
	# 	data.append(
	# 		{
	# 			"student": "",
	# 			"student_name": "TOTAL",
	# 			"present_students": total_present,
	# 			"leave_students": total_leave,
	# 			"absent_students": total_absent,
	# 			"contact_hours": total_contact_hours,
	# 			"attendance": round(total_attendance, 2),
	# 			"status": total_status,
				
	# 		}
	# 	)

	return data

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_programme_query(
	doctype,
	txt,
	searchfield,
	start,
	page_len,
	filters,
):
	college = get_effective_college(filters)

	conditions = [
		"college = %(college)s",
		"link_nvfk IS NOT NULL",
		"link_nvfk != ''",
	]

	values = {
		"college": college,
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len,
	}

	if filters.get("academic_term"):
		conditions.append(
			"academic_term = %(academic_term)s"
		)
		values["academic_term"] = filters.get("academic_term")

	return frappe.db.sql(
		f"""
		SELECT DISTINCT
			link_nvfk
		FROM
			`tabStudent Attendance`
		WHERE
			{" AND ".join(conditions)}
			AND link_nvfk LIKE %(txt)s
		ORDER BY
			link_nvfk
		LIMIT %(start)s, %(page_len)s
		""",
		values,
	)
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_module_query(
	doctype,
	txt,
	searchfield,
	start,
	page_len,
	filters,
):
	college = get_effective_college(filters)
	conditions = [
		"college = %(college)s",
		"module IS NOT NULL",
		"module != ''",
	]

	values = {
		"college": college,
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len,
	}

	if filters.get("academic_term"):
		conditions.append(
			"academic_term = %(academic_term)s"
		)
		values["academic_term"] = filters.get("academic_term")

	if filters.get("link_nvfk"):
		conditions.append(
			"link_nvfk = %(link_nvfk)s"
		)
		values["link_nvfk"] = filters.get("link_nvfk")

	return frappe.db.sql(
		f"""
		SELECT DISTINCT
			module
		FROM
			`tabStudent Attendance`
		WHERE
			{" AND ".join(conditions)}
			AND module LIKE %(txt)s
		ORDER BY
			module
		LIMIT %(start)s, %(page_len)s
		""",
		values,
	)
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_student_section_query(
	doctype,
	txt,
	searchfield,
	start,
	page_len,
	filters,
):
	college = get_effective_college(filters)
	conditions = [
		"college = %(college)s",
		"student_group IS NOT NULL",
		"student_group != ''",
	]

	values = {
		"college": college,
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len,
	}

	if filters.get("academic_term"):
		conditions.append(
			"academic_term = %(academic_term)s"
		)
		values["academic_term"] = filters.get("academic_term")

	if filters.get("link_nvfk"):
		conditions.append(
			"link_nvfk = %(link_nvfk)s"
		)
		values["link_nvfk"] = filters.get("link_nvfk")

	if filters.get("module"):
		conditions.append(
			"module = %(module)s"
		)
		values["module"] = filters.get("module")

	return frappe.db.sql(
		f"""
		SELECT DISTINCT
			student_group
		FROM
			`tabStudent Attendance`
		WHERE
			{" AND ".join(conditions)}
			AND student_group LIKE %(txt)s
		ORDER BY
			student_group
		LIMIT %(start)s, %(page_len)s
		""",
		values,
	)	
# def get_programme_contact_hours(college, programme):

# 	if not college or not programme:
# 		return 0

# 	result = frappe.db.sql(
# 		"""
# 		SELECT
# 			m.contact_hours AS contact_hours
# 		FROM `tabModule` m

# 		INNER JOIN `tabModule College` mc
# 			ON mc.parent = m.name

# 		WHERE
# 			mc.college = %(college)s
# 			AND mc.programme = %(programme)s
# 		""",
# 		{
# 			"college": college,
# 			"programme": programme,
# 		},
# 		as_dict=True,
# 	)

# 	return result[0].contact_hours if result else 0

def get_module_contact_hours(module):
    if not module:
        return 0

    contact_hours = frappe.db.get_value(
        "Module",
        module,
        "contact_hours"
    )

    return contact_hours or 0
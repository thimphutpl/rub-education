import frappe
from frappe import _, msgprint
from frappe.utils import formatdate

from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday

from education.education.doctype.student_attendance.student_attendance import (
	get_holiday_list,
)


def execute(filters=None):
	filters = filters or {}

	if not filters.get("college"):
		msgprint(_("Please select College"), raise_exception=1)

	if not filters.get("academic_term"):
		msgprint(_("Please select Academic Term"), raise_exception=1)

	if not filters.get("link_nvfk"):
		msgprint(_("Please select Programme"), raise_exception=1)

	# Date is optional, so check holiday only when Date is selected
	if filters.get("date"):
		holiday_list = get_holiday_list()

		if holiday_list and is_holiday(holiday_list, filters.get("date")):
			msgprint(
				_("No attendance has been marked for {0} as it is a Holiday").format(
					frappe.bold(formatdate(filters.get("date")))
				)
			)

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
	]


def get_data(filters):

	# ---------------------------------------------------------
	# 1. Mandatory filters
	# ---------------------------------------------------------

	attendance_filters = {
		"college": filters.get("college"),
		"academic_term": filters.get("academic_term"),

		# Programme actual fieldname
		"link_nvfk": filters.get("link_nvfk"),

		"docstatus": 1,
	}

	# ---------------------------------------------------------
	# 2. Optional filters
	# ---------------------------------------------------------

	if filters.get("date"):
		attendance_filters["date"] = filters.get("date")

	if filters.get("student_group"):
		attendance_filters["student_group"] = filters.get("student_group")

	if filters.get("module"):
		attendance_filters["module"] = filters.get("module")

	if filters.get("tutor"):
		attendance_filters["tutor"] = filters.get("tutor")

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

	data = []

	total_present = 0
	total_leave = 0
	total_absent = 0

	for student in attendance_map.values():

		present = student["Present"]
		leave = student["Leave"]
		absent = student["Absent"]

		total_present += present
		total_leave += leave
		total_absent += absent

		data.append(
			{
				"student": student["student"],
				"student_name": student["student_name"],
				"present_students": present,
				"leave_students": leave,
				"absent_students": absent,
			}
		)

	# ---------------------------------------------------------
	# 6. Total row
	# ---------------------------------------------------------

	if data:
		data.append(
			{
				"student": "",
				"student_name": "TOTAL",
				"present_students": total_present,
				"leave_students": total_leave,
				"absent_students": total_absent,
			}
		)

	return data
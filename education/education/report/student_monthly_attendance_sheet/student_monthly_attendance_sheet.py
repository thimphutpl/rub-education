

# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from erpnext.support.doctype.issue.issue import get_holidays
from frappe import _, msgprint
from frappe.utils import add_days, cstr, date_diff, get_last_day, getdate

from education.education.doctype.student_attendance.student_attendance import (
	get_holiday_list,
)
MONTH_MAP = {
	"Jan": 1,
	"Feb": 2,
	"Mar": 3,
	"Apr": 4,
	"May": 5,
	"Jun": 6,
	"Jul": 7,
	"Aug": 8,
	"Sep": 9,
	"Oct": 10,
	"Nov": 11,
	"Dec": 12,
}
def execute(filters=None):
	filters = filters or {}
	
	# if not filters.get("from_date"):
	# 	frappe.throw(_("Please select From Date"))

	# if not filters.get("to_date"):
	# 	frappe.throw(_("Please select To Date"))

	if not filters.get("month"):
		msgprint(_("Please select Month"), raise_exception=1)

	if not filters.get("college"):
		msgprint(_("Please select College"), raise_exception=1)

	if not filters.get("academic_term"):
		msgprint(_("Please select Academic Term"), raise_exception=1)
	
	if not filters.get("module"):
		msgprint(_("Please select Module"), raise_exception=1)

	# if not filters.get("link_nvfk"):
	# 	msgprint(_("Please select Programme"), raise_exception=1)
		

	# ---------------------------------------------------------
	# Get Academic Year automatically from selected Academic Term
	# ---------------------------------------------------------
	academic_year = frappe.db.get_value(
		"Academic Term",
		filters.get("academic_term"),
		"academic_year",
	)

	if not academic_year:
		msgprint(
			_("Academic Year is not set in the selected Academic Term"),
			raise_exception=1,
		)

	month_number = MONTH_MAP.get(filters.get("month"))

	if not month_number:
		msgprint(_("Invalid Month"), raise_exception=1)

	# Example: 2026-09-01
	# Get Academic Year start and end dates
	year_dates = frappe.db.get_value(
		"Academic Year",
		academic_year,
		["year_start_date", "year_end_date"],
		as_dict=True,
	)

	if not year_dates:
		frappe.throw(_("Academic Year dates not found"))

	year_start = getdate(year_dates.year_start_date)
	year_end = getdate(year_dates.year_end_date)

	# Determine the correct calendar year for the selected month
	from_date = None

	for year in range(year_start.year, year_end.year + 1):
		candidate = getdate(f"{year}-{month_number:02d}-01")
		candidate_end = get_last_day(candidate)

		if candidate <= year_end and candidate_end >= year_start:
			from_date = max(candidate, year_start)
			to_date = min(candidate_end, year_end)
			break

	if not from_date:
		frappe.throw(_("Selected month is outside the Academic Year"))

	total_days_in_month = date_diff(to_date, from_date) + 1

	columns = get_columns(total_days_in_month)

	# ---------------------------------------------------------
	# Get students using College + Academic Term + Programme
	# Student Section is optional
	# ---------------------------------------------------------
	
	# contact_hours = get_programme_contact_hours( college=filters.get("college"), programme=filters.get("link_nvfk"), )
	students = get_students(filters, from_date, to_date)

	

	if not students:
		return columns, []

	students_list = get_students_list(students)

	att_map = get_attendance_list(
		from_date,
		to_date,
		filters,
		students_list,
	)

	data = []

	for stud in students:
		student_status = frappe.db.get_value(
			"Student",
			stud.student,
			"enabled",
		)

		date = from_date

		# total_present = 0
		# total_absent = 0
		# total_leave = 0
		# status=None

	

		row = {
			"student": stud.student,
			"student_name": stud.student_name,
			# "contact_hours": contact_hours
		}

		status_map = {
			"Present": "P",
			"Absent": "A",
			"None": "",
			"Inactive": "-",
			"Holiday": "H",
			"Leave": "L",
		}

		for day in range(total_days_in_month):
			status = "None"

			if att_map.get(stud.student):
				status = att_map.get(stud.student).get(date, "None")

			elif not student_status:
				status = "Inactive"

			else:
				status = "None"

			# if status == "Present":
			# 	total_present += 1

			# elif status == "Absent":
			# 	total_absent += 1

			# elif status == "Leave":
			# 	total_leave += 1

			row[cstr(day + 1)] = status_map.get(status, "")

			date = add_days(date, 1)
			# attendance = (
			# 			(total_present / contact_hours) * 100
			# 		)
			# attendance_threshold = frappe.db.get_single_value(
			# 	"Academic Settings",
			# 	"attendance_threshold"
			# )
			# if attendance < attendance_threshold: 
			# 	status = "Shortage" 
			# else: 
			# 	status = ""
			

		# row.update(
		# 	{
		# 		"Total Present": total_present,
		# 		"Total Leave": total_leave,
		# 		"Total Absent": total_absent,
		# 		"attendance": round(attendance,2),
		# 		"status":status
		# 	}
		# )

		data.append(row)

	return columns, data


def get_columns(days_in_month):
	columns = [
		{
			"label": _("Student"),
			"fieldname": "student",
			"fieldtype": "Link",
			"options": "Student",
			"width": 110,
		},
		{
			"label": _("Student Name"),
			"fieldname": "student_name",
			"fieldtype": "Data",
			"width": 160,
		},
	]

	for day in range(days_in_month):
		columns.append(
			{
				"label": cstr(day + 1),
				"fieldname": cstr(day + 1),
				"fieldtype": "Data",
				"width": 50,
			}
		)

	# columns += [
	# 	{
	# 		"label": _("Total Present"),
	# 		"fieldname": "Total Present",
	# 		"fieldtype": "Int",
	# 		"width": 95,
	# 	},
	# 	{
	# 		"label": _("Total Leave"),
	# 		"fieldname": "Total Leave",
	# 		"fieldtype": "Int",
	# 		"width": 90,
	# 	},
	# 	{
	# 		"label": _("Total Absent"),
	# 		"fieldname": "Total Absent",
	# 		"fieldtype": "Int",
	# 		"width": 90,
	# 	},
	# 	{
	# 		"label": _("Contact Hours"),
	# 		"fieldname": "contact_hours",
	# 		"fieldtype": "Int",
	# 		"width": 100,
	# 	},
	# 	{
	# 		"label": _("Attendance (%)"),
	# 		"fieldname": "attendance",
	# 		"fieldtype": "Percentage",
	# 		"width": 100
	# 	},
	# 	{
	# 		"label": _("Status (Min.90%)"),
	# 		"fieldname": "status",
	# 		"fieldtype": "Data",
	# 		"width": 100
			
	# 	}
   	
	# ]

	return columns


def get_students(filters, from_date, to_date):
	# ---------------------------------------------------------
	# Fetch students directly from Student Attendance.
	#
	# Required:
	# College + Academic Term + Programme + Month
	#
	# Optional:
	# Student Section
	# ---------------------------------------------------------

	conditions = {
		"college": filters.get("college"),
		"academic_term": filters.get("academic_term"),
		# "link_nvfk": filters.get("link_nvfk"),
		"docstatus": 1,
		"date": ["between", [from_date, to_date]],
	}
	# Student is optional

	if filters.get("module"):
		conditions["module"] = filters.get("module")

	if filters.get("student"):
		conditions["student"] = filters.get("student")


	if filters.get("student_section"):
		conditions["student_group"] = filters.get("student_section")

	attendance_students = frappe.get_all(
		"Student Attendance",
		filters=conditions,
		fields=[
			"student",
			"student_name",
		],
		order_by="student_name asc",
	)

	# Remove duplicate students
	student_map = {}

	for student in attendance_students:
		if student.student not in student_map:
			student_map[student.student] = frappe._dict(
				{
					"student": student.student,
					"student_name": student.student_name,
				}
			)

	return list(student_map.values())


def get_students_list(students):
	return [student.student for student in students]


# def get_programme_contact_hours(
# 	college,
# 	programme
# ):

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


def get_attendance_list(
	from_date,
	to_date,
	filters,
	students_list,
):
	# ---------------------------------------------------------
	# Attendance filters
	# ---------------------------------------------------------

	attendance_filters = {
		"college": filters.get("college"),
		"academic_term": filters.get("academic_term"),
		# "link_nvfk": filters.get("link_nvfk"),
		"student": ["in", students_list],
		"date": ["between", [from_date, to_date]],
		"docstatus": 1,
	}

	# Optional Student Section
	if filters.get("module"):
		attendance_filters["module"] = filters.get("module")
		
	if filters.get("student_section"):
		attendance_filters["student_group"] = filters.get(
			"student_section"
		)

	attendance_list = frappe.get_all(
		"Student Attendance",
		filters=attendance_filters,
		fields=[
			"student",
			"date",
			"status",
		],
		order_by="student asc, date asc",
	)

	att_map = {}

	students_with_leave_application = (
		get_students_with_leave_application(
			from_date,
			to_date,
			students_list,
		)
	)

	for attendance in attendance_list:
		att_map.setdefault(
			attendance.student,
			frappe._dict(),
		)

		if (
			students_with_leave_application
			and students_with_leave_application.get(attendance.date)
			and attendance.student
			in students_with_leave_application.get(attendance.date)
		):
			att_map[attendance.student][attendance.date] = "Present"

		else:
			att_map[attendance.student][attendance.date] = (
				attendance.status
			)

	att_map = mark_holidays(
		att_map,
		from_date,
		to_date,
		students_list,
	)

	return att_map


def get_students_with_leave_application(
	from_date,
	to_date,
	students_list,
):
	if not students_list:
		return {}

	leave_applications = frappe.db.sql(
		"""
		SELECT
			student,
			from_date,
			to_date
		FROM
			`tabStudent Leave Application`
		WHERE
			mark_as_present = 1
			AND docstatus = 1
			AND student IN %(students)s
			AND (
				from_date BETWEEN %(from_date)s AND %(to_date)s
				OR to_date BETWEEN %(from_date)s AND %(to_date)s
				OR (
					%(from_date)s BETWEEN from_date AND to_date
					AND %(to_date)s BETWEEN from_date AND to_date
				)
			)
		""",
		{
			"students": students_list,
			"from_date": from_date,
			"to_date": to_date,
		},
		as_dict=True,
	)

	students_with_leaves = {}

	for application in leave_applications:
		for date in daterange(
			application.from_date,
			application.to_date,
		):
			students_with_leaves.setdefault(
				date,
				[],
			).append(application.student)

	return students_with_leaves


def daterange(d1, d2):
	import datetime

	return (
		d1 + datetime.timedelta(days=i)
		for i in range((d2 - d1).days + 1)
	)


def mark_holidays(
	att_map,
	from_date,
	to_date,
	students_list,
):
	holiday_list = get_holiday_list()
	holidays = get_holidays(holiday_list)

	for dt in daterange(
		getdate(from_date),
		getdate(to_date),
	):
		if dt in holidays:
			for student in students_list:
				att_map.setdefault(
					student,
					frappe._dict(),
				).setdefault(
					dt,
					"Holiday",
				)

	return att_map

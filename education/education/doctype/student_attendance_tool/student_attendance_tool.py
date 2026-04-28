# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document


class StudentAttendanceTool(Document):
	pass


@frappe.whitelist()
def get_student_attendance_records(
	date=None, student_group=None, timetable_schedule_entry=None, course =None
):
	student_list = []
	student_attendance_list = []
	#--------------pre introduction to timetable schedule entry START-----------------------#
	# if based_on == "Course Schedule":
	# 	student_group = frappe.db.get_value(
	# 		"Course Schedule", course_schedule, "student_group"
	# 	)
	# 	if student_group:
	# 		student_list = frappe.get_all(
	# 			"Student Section Student",
	# 			fields=["student", "student_name", "group_roll_number"],
	# 			filters={"parent": student_group, "active": 1},
	# 			order_by="group_roll_number",
	# 		)

	# if not student_list:
	#--------------pre introduction to timetable schedule entry END-----------------------#

	student_list = frappe.get_all(
		"Student Section Student",
		fields=["student", "student_name", "group_roll_number"],
		filters={"parent": student_group, "active": 1},
		order_by="group_roll_number",
	)

	StudentAttendance = frappe.qb.DocType("Student Attendance")

	if timetable_schedule_entry:
		student_attendance_list = (
			frappe.qb.from_(StudentAttendance)
			.select(StudentAttendance.student, StudentAttendance.status)
			.where((StudentAttendance.timetable_schedule_entry_id == timetable_schedule_entry))
		).run(as_dict=True)
	# else:
	#--------------pre introduction to timetable schedule entry START-----------------------#

	# student_attendance_list = (
	# 	frappe.qb.from_(StudentAttendance)
	# 	.select(StudentAttendance.student, StudentAttendance.status)
	# 	.where(
	# 		(StudentAttendance.student_group == student_group)
	# 		& (StudentAttendance.date == date)
	# 		& (
	# 			(StudentAttendance.timetable_schedule_entry_id == "")
	# 			| (StudentAttendance.course_schedule.isnull())
	# 		)
	# 	)
	# ).run(as_dict=True)
	#--------------pre introduction to timetable schedule entry END-----------------------#

	for attendance in student_attendance_list:
		for student in student_list:
			if student.student == attendance.student:
				student.status = attendance.status

	return student_list

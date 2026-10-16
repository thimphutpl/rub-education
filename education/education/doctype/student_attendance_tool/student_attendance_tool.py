# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document

from datetime import datetime
class StudentAttendanceTool(Document):
    pass




@frappe.whitelist()
def get_student_attendance_records_student_group(
    date=None, student_group=None,timetable_schedule_entry=None,  course =None
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

    # student_list = frappe.get_all(
    # 	"Student Section Student",
    # 	fields=["student", "student_name", "group_roll_number"],
    # 	filters={"parent": student_group, "active": 1},
    # 	order_by="group_roll_number",
    # )

    student_list = frappe.get_all(
        "Student Section Student",
        fields=["student", "student_name", "section_name"],
        filters={
            "parent": student_group
            }
    )
    # frappe.throw(str(student_list))


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



@frappe.whitelist()
def get_student_attendance_records(
    date=None, student_group=None, timetable_schedule_entry=None, course =None,module_enrollment_key=None
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

    # student_list = frappe.get_all(
    # 	"Student Section Student",
    # 	fields=["student", "student_name", "group_roll_number"],
    # 	filters={"parent": student_group, "active": 1},
    # 	order_by="group_roll_number",
    # )

    student_list = frappe.get_all(
            "Module Enrolment",
            fields=["student", "student_name","student_section"],
            filters={
                "module_enrollment_key": module_enrollment_key
            }
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


# @frappe.whitelist()
# def get_timetable_period(name,date ):
# 	day = datetime.strptime(date, "%Y-%m-%d").strftime("%A")

# 	result = frappe.db.sql(
# 		"""
# 		SELECT
# 			tcap.day,
# 			tcap.from_time,
# 			tcap.to_time
# 		FROM `tabTimetable Schedule Entry` tse

# 		INNER JOIN `tabTimetable Constraint Academic Periods` tcap
# 			ON tse.name = tcap.parent

# 		WHERE
# 			tse.name = %(name)s
# 			AND tcap.day = %(day)s
# 		""",
# 		{
# 			"name": name,
# 			"day": day
# 		},
# 		as_dict=True
# 	)


# 	return result[0] if result else {}

@frappe.whitelist()
def get_timetable_period(name, date):
    day = datetime.strptime(date, "%Y-%m-%d").strftime("%A")

    result = frappe.db.sql(
        """
        SELECT
            tcap.day,
            MIN(tcap.from_time) AS from_time,
            MAX(tcap.to_time) AS to_time
        FROM `tabTimetable Schedule Entry` tse
        INNER JOIN `tabTimetable Constraint Academic Periods` tcap
            ON tse.name = tcap.parent
        WHERE
            tse.name = %(name)s
            AND tcap.day = %(day)s
            AND IFNULL(tcap.called_off, 0) = 0
        GROUP BY tcap.day
        """,
        {
            "name": name,
            "day": day
        },
        as_dict=True
    )

    return result[0] if result else {}



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def filter_student_group(
    doctype,
    txt,
    searchfield,
    start,
    page_len,
    filters,
):
    filters = frappe._dict(filters or {})

    entry = filters.get("timetable_schedule_entry")
    college = filters.get("college")
    academic_term = filters.get("academic_term")
    programme = filters.get("programme")
    class_type = filters.get("class_type")
    session_type = filters.get("session_type")

    if not entry or not college or not academic_term:
        return []

    # Get the selected timetable entry.
    entry_doc = frappe.db.get_value(
        "Timetable Schedule Entry",
        entry,
        ["session_type", "student_section"],
        as_dict=True,
    )

    if not entry_doc:
        return []

    sections = []

    # Combined sessions can have multiple sections in Combined Class Item.
    if (
        session_type in ("Combined", "Extra Class")
        or entry_doc.session_type in ("Combined", "Extra Class")
    ):
        sections = frappe.get_all(
            "Combined Class Item",
            filters={
                "parent": entry,
                "parenttype": "Timetable Schedule Entry",
                "parentfield": "combined_class",
            },
            pluck="section",
        )
  

    # Regular and Extra Class sessions use the parent section.
    else:
        if entry_doc.student_section:
            sections = [entry_doc.student_section]

    sections = list(set(section for section in sections if section))

    if not sections:
        return []

    conditions = [
        "sg.college = %(college)s",
        "sg.academic_term = %(academic_term)s",
        "IFNULL(sg.disabled, 0) = 0",
        "sg.name IN %(sections)s",
        """
        (
            sg.name LIKE %(txt)s
            OR sg.name LIKE %(txt)s
        )
        """,
    ]

    values = {
        "college": college,
        "academic_term": academic_term,
        "sections": tuple(sections),
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len,
    }

    if programme:
        conditions.append("sg.program = %(programme)s")
        values["programme"] = programme

    if class_type:
        conditions.append("sg.class_type = %(class_type)s")
        values["class_type"] = class_type

    return frappe.db.sql(
        """
        SELECT
            sg.name
        FROM `tabStudent Section` sg
        WHERE sg.name IN %(sections)s
        ORDER BY sg.name
        """,
        {
            "sections": tuple(sections),
        },
    )
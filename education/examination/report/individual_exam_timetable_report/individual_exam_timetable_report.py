from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data


def get_columns():
    return [
	    _("Exam Date") + ":Date:120",
  		_("Start Time") + ":Time:100",
        _("End Time") + ":Time:100",
		_("Exam Hall") + "::150",
        _("Exam ID") + ":Link/Exam Timetable:150",
        _("Academic Year") + ":Link/Academic Year:120",
        _("Academic Term") + ":Link/Academic Term:120",
        _("Assessment Component") + ":Link/Assessment Component:150",      
        _("Invigilators") + "::200",
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql(f"""
        SELECT
            et.name AS exam_id,
            et.college,
            et.academic_year,
            et.academic_term,
            et.assessment_component,
            r.room_name AS exam_hall,
            et.capacity,
            et.exam_date,
            et.start_time,
            et.end_time,
            GROUP_CONCAT(DISTINCT ei.invigilator_name SEPARATOR ', ') AS invigilators,
            COUNT(DISTINCT ets.student) AS total_students
        FROM `tabExam Timetable` et
        LEFT JOIN `tabRoom` r ON r.name = et.room
        LEFT JOIN `tabExam Invigilator` ei ON ei.parent = et.name
        LEFT JOIN `tabExam Timetable Student` ets ON ets.parent = et.name
        WHERE 1=1 {conditions}
        GROUP BY et.name
        ORDER BY et.exam_date, et.start_time
    """, as_dict=True)

    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("college"):
        conditions += f" AND et.college = '{filters.get('college')}'"
    if filters.get("academic_year"):
        conditions += f" AND et.academic_year = '{filters.get('academic_year')}'"
    if filters.get("academic_term"):
        conditions += f" AND et.academic_term = '{filters.get('academic_term')}'"
    if filters.get("exam_date"):
        conditions += f" AND et.exam_date = '{filters.get('exam_date')}'"
    if filters.get("room"):
        conditions += f" AND et.room = '{filters.get('room')}'"

    return conditions

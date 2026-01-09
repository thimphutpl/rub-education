from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def format_time(time_str):
    """Return HH:MM format from 'HH:MM:SS' string"""
    if not time_str:
        return ""
    return str(time_str)[:5]  # Take first 5 chars HH:MM


def get_columns():
    # Fetch all distinct time slots and create columns dynamically
    time_slots = frappe.db.sql("""
        SELECT DISTINCT start_time, end_time
        FROM `tabExam Timetable`
        ORDER BY start_time
    """, as_dict=True)

    columns = [
        {"label": "Exam Hall", "fieldname": "hall", "fieldtype": "Data", "width": 150},
        {"label": "Capacity", "fieldname": "capacity", "fieldtype": "Int", "width": 100}  # Capacity column
    ]

    for t in time_slots:
        col_name = f"{format_time(t['start_time'])}-{format_time(t['end_time'])}"
        columns.append({
            "label": col_name,
            "fieldname": col_name,
            "fieldtype": "Data",
            "width": 250
        })
    return columns


def get_data(filters):
    # Fetch all halls (filtered if room is specified)
    hall_conditions = ""
    if filters and filters.get("room"):
        hall_conditions = f"WHERE room = '{filters.get('room')}'"

    halls = frappe.db.sql(f"""
        SELECT DISTINCT room, capacity
        FROM `tabExam Timetable`
        {hall_conditions}
        ORDER BY room
    """, as_dict=True)

    # Fetch timetable entries with joined child tables
    timetables = frappe.db.sql(f"""
        SELECT 
            et.name AS exam_id,
            et.room AS exam_hall,
            et.start_time,
            et.end_time,
            et.capacity AS exam_capacity,
            et.exam_date,
            GROUP_CONCAT(DISTINCT em.module SEPARATOR ', ') AS modules,
            COUNT(DISTINCT ets.student) AS total_students,
            GROUP_CONCAT(DISTINCT ei.invigilator_name SEPARATOR ', ') AS invigilators
        FROM `tabExam Timetable` et
        LEFT JOIN `tabExam Module` em ON em.parent = et.name
        LEFT JOIN `tabExam Timetable Student` ets ON ets.parent = et.name
        LEFT JOIN `tabExam Invigilator` ei ON ei.parent = et.name
        WHERE 1=1
        {get_conditions(filters)}
        GROUP BY et.name
        ORDER BY et.start_time
    """, as_dict=True)

    # Build hall-wise matrix
    data = []
    time_slots = sorted(list(set((t['start_time'], t['end_time']) for t in timetables)))
    for hall in halls:
        row = {
            "hall": hall['room'],
            "capacity": hall.get('capacity', 0)
        }
        for slot in time_slots:
            exams = [et for et in timetables if et['exam_hall'] == hall['room']
                     and et['start_time'] == slot[0] and et['end_time'] == slot[1]]
            cell_content = []
            for e in exams:
                cell_content.append(
                    f"Modules: {e['modules']} ({e['total_students']} students) <br>"
                    f"Invigilators: {e['invigilators']}"
                )
            col_name = f"{format_time(slot[0])}-{format_time(slot[1])}"
            row[col_name] = "<br>".join(cell_content) if cell_content else "-"
        data.append(row)

    return data


def get_conditions(filters):
    conditions = ""
    if filters:
        if filters.get("exam_date"):
            conditions += f" AND et.exam_date = '{filters.get('exam_date')}'"
        if filters.get("room"):
            conditions += f" AND et.room = '{filters.get('room')}'"
    return conditions

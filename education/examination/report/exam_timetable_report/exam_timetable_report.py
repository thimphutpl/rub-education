from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def format_time(time_str):
    """Return HH:MM format from 'HH:MM:SS' string"""
    if not time_str:
        return ""
    return str(time_str)[:5]  # Take first 5 chars HH:MM


def get_weekday(date_str):
    """Return weekday name for a given date"""
    if not date_str:
        return ""
    try:
        date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
        return date_obj.strftime('%A')  # Returns full weekday name (Monday, Tuesday, etc.)
    except:
        return ""


def get_columns(filters=None):
    # Fetch all distinct time slots
    time_slots = frappe.db.sql("""
        SELECT DISTINCT start_time, end_time
        FROM `tabExam Timetable`
        WHERE docstatus = 1
        ORDER BY start_time
    """, as_dict=True)

    # Fetch distinct exam dates
    exam_dates = frappe.db.sql("""
        SELECT DISTINCT exam_date
        FROM `tabExam Timetable`
        WHERE docstatus = 1
        ORDER BY exam_date
    """, as_dict=True)

    columns = []
    
    # For each date, add Day, Date, Hall, Capacity, Total Students, Invigilators, then time slots
    for date in exam_dates:
        weekday = get_weekday(date['exam_date'])
        
        # Add Day column for this date
        columns.append({
            "label": "Day",
            "fieldname": f"day_{date['exam_date']}",
            "fieldtype": "Data",
            "width": 100
        })
        
        # Add Date column for this date
        columns.append({
            "label": "Date",
            "fieldname": f"date_{date['exam_date']}",
            "fieldtype": "Data",
            "width": 100
        })
        
        # Add Hall column for this date
        columns.append({
            "label": "Exam Hall",
            "fieldname": f"hall_{date['exam_date']}",
            "fieldtype": "Data",
            "width": 150
        })
        
        # Add Capacity column for this date
        columns.append({
            "label": "Capacity",
            "fieldname": f"capacity_{date['exam_date']}",
            "fieldtype": "Int",
            "width": 100
        })
        
        # Add Total Students column for this date
        columns.append({
            "label": "Total Students",
            "fieldname": f"total_students_{date['exam_date']}",
            "fieldtype": "Int",
            "width": 120
        })
        
        # Add Invigilators column for this date
        columns.append({
            "label": "Invigilators",
            "fieldname": f"invigilators_{date['exam_date']}",
            "fieldtype": "Data",
            "width": 200
        })
        
        # Add time slot columns for this date
        for t in time_slots:
            col_name = f"time_{date['exam_date']}_{format_time(t['start_time'])}-{format_time(t['end_time'])}"
            columns.append({
                "label": f"{format_time(t['start_time'])}-{format_time(t['end_time'])}",
                "fieldname": col_name,
                "fieldtype": "HTML",
                "width": 250
            })
    
    return columns


def get_data(filters):
    # Fetch all halls (filtered if room is specified)
    hall_conditions = ""
    if filters and filters.get("room"):
        hall_conditions = f"AND room = '{filters.get('room')}'"

    # Only fetch halls from submitted timetables
    halls = frappe.db.sql(f"""
        SELECT DISTINCT room, capacity
        FROM `tabExam Timetable`
        WHERE docstatus = 1  -- Only submitted timetables
        {hall_conditions}
        ORDER BY room
    """, as_dict=True)

    # Fetch timetable entries with joined child tables - only submitted
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
            GROUP_CONCAT(DISTINCT ei.invigilator SEPARATOR ', ') AS invigilators
        FROM `tabExam Timetable` et
        LEFT JOIN `tabExam Module` em ON em.parent = et.name
        LEFT JOIN `tabExam Timetable Student` ets ON ets.parent = et.name
        LEFT JOIN `tabExam Invigilator` ei ON ei.parent = et.name
        WHERE et.docstatus = 1  
        {get_conditions(filters)}
        GROUP BY et.name
        ORDER BY et.exam_date, et.start_time
    """, as_dict=True)

    # Get all unique dates and time slots
    unique_dates = sorted(list(set(t['exam_date'] for t in timetables)))
    unique_time_slots = sorted(list(set((t['start_time'], t['end_time']) for t in timetables)))

    # Build data rows
    data = []
    
    # For each date, create separate rows for each hall
    for exam_date in unique_dates:
        weekday = get_weekday(exam_date)
        
        # Filter halls that have exams on this date
        halls_for_date = [hall for hall in halls if any(
            et['exam_hall'] == hall['room'] and et['exam_date'] == exam_date 
            for et in timetables
        )]
        
        # If no halls for this date, skip
        if not halls_for_date:
            continue
            
        # For each hall on this date
        for hall in halls_for_date:
            row = {}
            
            # Add Day and Date
            row[f"day_{exam_date}"] = weekday
            row[f"date_{exam_date}"] = exam_date
            row[f"hall_{exam_date}"] = hall['room']
            row[f"capacity_{exam_date}"] = hall.get('capacity', 0)
            
            # Initialize total students and invigilators for this hall and date
            total_students = 0
            invigilators_list = []
            
            # For each time slot
            for slot in unique_time_slots:
                # Find exams matching hall, date, and time slot
                exams = [et for et in timetables 
                        if et['exam_hall'] == hall['room']
                        and et['exam_date'] == exam_date
                        and et['start_time'] == slot[0] 
                        and et['end_time'] == slot[1]]
                
                cell_content = []
                for e in exams:
                    # Accumulate total students and invigilators for this hall/date
                    total_students += e['total_students'] if e['total_students'] else 0
                    if e['invigilators']:
                        invigilators_list.append(e['invigilators'])
                    
                    # Format the cell content with exam details
                    cell_text = f"""
                    <div style="padding: 5px; border-bottom: 1px solid #eee;">
                        {e['modules']}<br>
                        Students: {e['total_students'] or 0}<br>
                        Invigilators: {e['invigilators'] or '-'}
                    </div>
                    """
                    cell_content.append(cell_text)
                
                col_name = f"time_{exam_date}_{format_time(slot[0])}-{format_time(slot[1])}"
                row[col_name] = "".join(cell_content) if cell_content else "<div style='color: #999; text-align: center;'>-</div>"
            
            # Add total students and invigilators to the row
            row[f"total_students_{exam_date}"] = total_students
            
            # Remove duplicates and join invigilators
            unique_invigilators = []
            for inv in invigilators_list:
                for inv_name in inv.split(', '):
                    if inv_name not in unique_invigilators and inv_name.strip():
                        unique_invigilators.append(inv_name.strip())
            row[f"invigilators_{exam_date}"] = ', '.join(unique_invigilators) if unique_invigilators else "-"
            
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
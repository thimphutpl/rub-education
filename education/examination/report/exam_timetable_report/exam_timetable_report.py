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
        return date_obj.strftime('%A')  # Returns full weekday name
    except:
        return ""


def get_columns(filters=None):
    # Fetch all distinct time slots from submitted timetables
    time_slots = frappe.db.sql("""
        SELECT DISTINCT start_time, end_time
        FROM `tabExam Timetable`
        WHERE docstatus = 1
        ORDER BY start_time
    """, as_dict=True)

    # Fetch distinct exam dates from submitted timetables
    exam_dates = frappe.db.sql("""
        SELECT DISTINCT exam_date
        FROM `tabExam Timetable`
        WHERE docstatus = 1
        ORDER BY exam_date
    """, as_dict=True)

    columns = []
    
    # For each date, add columns
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
        
        # Add Module column for this date
        columns.append({
            "label": "Module(s)",
            "fieldname": f"modules_{date['exam_date']}",
            "fieldtype": "Data",
            "width": 200
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
    # Build conditions
    conditions = get_conditions(filters)
    
    # Fetch timetable entries with all related data - only submitted timetables
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
        {conditions}
        GROUP BY et.name, et.room, et.start_time, et.end_time, et.exam_date
        ORDER BY et.exam_date, et.start_time, et.room
    """, as_dict=True)

    if not timetables:
        return []

    # Get all unique dates and time slots
    unique_dates = sorted(list(set(t['exam_date'] for t in timetables)))
    unique_time_slots = sorted(list(set((t['start_time'], t['end_time']) for t in timetables)))
    
    # Get all unique halls
    unique_halls = sorted(list(set(t['exam_hall'] for t in timetables)))

    # Build data rows - one row per hall per date
    data = []
    
    for exam_date in unique_dates:
        weekday = get_weekday(exam_date)
        
        # Filter timetables for this date
        date_timetables = [t for t in timetables if t['exam_date'] == exam_date]
        
        # Get halls for this date
        halls_for_date = sorted(list(set(t['exam_hall'] for t in date_timetables)))
        
        # If no halls for this date, skip
        if not halls_for_date:
            continue
            
        # For each hall on this date
        for hall in halls_for_date:
            row = {}
            
            # Filter timetables for this specific hall and date
            hall_timetables = [t for t in date_timetables if t['exam_hall'] == hall]
            
            # Add Day and Date
            row[f"day_{exam_date}"] = weekday
            row[f"date_{exam_date}"] = exam_date
            row[f"hall_{exam_date}"] = hall
            
            # Get capacity (from first timetable for this hall/date)
            capacity = hall_timetables[0].get('exam_capacity', 0) if hall_timetables else 0
            row[f"capacity_{exam_date}"] = capacity
            
            # Collect all modules for this hall/date
            all_modules = []
            total_students = 0
            invigilators_list = []
            
            # For each time slot
            for slot in unique_time_slots:
                # Find exams matching hall, date, and time slot
                slot_exams = [t for t in hall_timetables 
                            if t['start_time'] == slot[0] and t['end_time'] == slot[1]]
                
                cell_content = []
                for exam in slot_exams:
                    # Collect modules
                    if exam['modules']:
                        all_modules.append(exam['modules'])
                    
                    # Accumulate total students
                    if exam['total_students']:
                        total_students += exam['total_students']
                    
                    # Collect invigilators
                    if exam['invigilators']:
                        invigilators_list.append(exam['invigilators'])
                    
                    # Format the cell content with exam details
                    cell_text = f"""
                    <div style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-size: 12px;">
                        <strong>{exam['modules']}</strong><br>
                        <span style="color: #4a5568;">Students: {exam['total_students'] or 0}</span><br>
                        <span style="color: #4a5568;">Invigilators: {exam['invigilators'] or '-'}</span>
                    </div>
                    """
                    cell_content.append(cell_text)
                
                col_name = f"time_{exam_date}_{format_time(slot[0])}-{format_time(slot[1])}"
                if cell_content:
                    row[col_name] = "".join(cell_content)
                else:
                    row[col_name] = "<div style='padding: 8px; color: #cbd5e0; text-align: center;'>—</div>"
            
            # Add modules to row
            unique_modules = []
            for mod in all_modules:
                for module_name in mod.split(', '):
                    if module_name not in unique_modules and module_name.strip():
                        unique_modules.append(module_name.strip())
            row[f"modules_{exam_date}"] = ', '.join(unique_modules) if unique_modules else "-"
            
            # Add total students to row
            row[f"total_students_{exam_date}"] = total_students
            
            # Process unique invigilators
            unique_invigilators = []
            for inv in invigilators_list:
                for inv_name in inv.split(', '):
                    if inv_name not in unique_invigilators and inv_name.strip():
                        unique_invigilators.append(inv_name.strip())
            row[f"invigilators_{exam_date}"] = ', '.join(unique_invigilators) if unique_invigilators else "-"
            
            data.append(row)
    
    # If no data in the new format, fall back to group by time slot
    if not data:
        data = get_grouped_by_timeslot_data(timetables, unique_dates, unique_time_slots)
    
    return data


def get_grouped_by_timeslot_data(timetables, unique_dates, unique_time_slots):
    """
    Alternative data format: Group exams by time slot across all halls
    """
    data = []
    
    for exam_date in unique_dates:
        weekday = get_weekday(exam_date)
        
        # Filter timetables for this date
        date_timetables = [t for t in timetables if t['exam_date'] == exam_date]
        
        # For each time slot
        for slot in unique_time_slots:
            row = {}
            row["day"] = weekday
            row["date"] = exam_date
            row["time_slot"] = f"{format_time(slot[0])} - {format_time(slot[1])}"
            
            # Get exams for this time slot and date
            slot_exams = [t for t in date_timetables 
                         if t['start_time'] == slot[0] and t['end_time'] == slot[1]]
            
            # Create HTML content for halls
            hall_content = []
            for exam in slot_exams:
                hall_html = f"""
                <div style="margin-bottom: 10px; padding: 8px; background: #f7fafc; border-radius: 4px;">
                    <strong>Hall: {exam['exam_hall']}</strong><br>
                    Module: {exam['modules']}<br>
                    Students: {exam['total_students'] or 0}<br>
                    Invigilators: {exam['invigilators'] or '-'}
                </div>
                """
                hall_content.append(hall_html)
            
            row["exams"] = "".join(hall_content) if hall_content else "-"
            data.append(row)
    
    return data


def get_conditions(filters):
    """Build SQL conditions based on filters"""
    conditions = ""
    if filters:
        if filters.get("exam_date"):
            conditions += f" AND et.exam_date = '{filters.get('exam_date')}'"
        if filters.get("room"):
            conditions += f" AND et.room = '{filters.get('room')}'"
        if filters.get("academic_year"):
            conditions += f" AND et.academic_year = '{filters.get('academic_year')}'"
        if filters.get("academic_term"):
            conditions += f" AND et.academic_term = '{filters.get('academic_term')}'"
        if filters.get("college"):
            conditions += f" AND et.college = '{filters.get('college')}'"
        if filters.get("module"):
            # Filter by module in the Exam Module child table
            conditions += f""" AND et.name IN (
                SELECT DISTINCT parent FROM `tabExam Module` 
                WHERE module = '{filters.get('module')}'
            )"""
    return conditions


@frappe.whitelist()
def get_report_filters():
    """Return available filter options for the report"""
    academic_years = frappe.db.sql_list("SELECT DISTINCT academic_year FROM `tabExam Timetable` WHERE docstatus = 1 ORDER BY academic_year DESC")
    academic_terms = frappe.db.sql_list("SELECT DISTINCT academic_term FROM `tabExam Timetable` WHERE docstatus = 1 ORDER BY academic_term")
    colleges = frappe.db.sql_list("SELECT DISTINCT college FROM `tabExam Timetable` WHERE docstatus = 1 ORDER BY college")
    rooms = frappe.db.sql_list("SELECT DISTINCT room FROM `tabExam Timetable` WHERE docstatus = 1 ORDER BY room")
    modules = frappe.db.sql_list("""
        SELECT DISTINCT em.module 
        FROM `tabExam Module` em
        INNER JOIN `tabExam Timetable` et ON em.parent = et.name
        WHERE et.docstatus = 1
        ORDER BY em.module
    """)
    
    return {
        "academic_years": academic_years,
        "academic_terms": academic_terms,
        "colleges": colleges,
        "rooms": rooms,
        "modules": modules
    }
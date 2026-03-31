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
	cond = ""
	if filters.get("module"):
		cond = " and module = '{}'".format(filters.get("module"))
	modules = frappe.db.sql("""
		SELECT module
		FROM `tabModule Enrolment Key`
		WHERE docstatus = 1 and college = '{}' and
		programme = '{}' and academic_term = '{}'
		{}
	""".format(filters.get("college"), filters.get("programme"), filters.get("academic_term"), cond), as_dict=True)


	columns =	[
        {
            "fieldname": "student",
            "label": _("Student"),
            "fieldtype": "Link",
            "options": "Student",
            "width": 140
        },
        {
            "fieldname": "student_name",
            "label": _("Student Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "college",
            "label": _("College"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 120
        },
        {
            "fieldname": "programme",
            "label": _("Programme"),
            "fieldtype": "Link",
            "options":"Programme",
            "width": 150
        },
        {
            "fieldname": "section",
            "label": _("Student Section"),
            "fieldtype": "Link",
            "options":"Student Section",
            "width": 150
        }
	]
	# frappe.throw(str(modules))
	# For each date, add Day, Date, Hall, Capacity, Total Students, Invigilators, then time slots
	for m in modules:
		# label = m.module+"("+frappe.db.get_value("Module", m.module, "module_code")
		
		# Add Day column for this date
		if frappe.db.exists("Module College", {"module_semester": filters.get("semester"), "programme": filters.get("programme"), "college": filters.get("college"), "parent": m.module}):
			columns.append({
				"label": frappe.db.get_value("Module", m.module, "module_code"),
				"fieldname": str(m.module).lower(),
				"fieldtype": "Data",
				"width": 200
			})

	
	return columns


def get_data(filters):
	# Fetch all halls (filtered if room is specified)
	enrolment_conditions = ""
	student_conditions = ""
	if filters and filters.get("student"):
		enrolment_conditions = f"AND student = '{filters.get('student')}'"
	if filters.get("college"):
		student_conditions += " and company = '{}'".format(filters.get("college"))
	if filters.get("programme"):
		student_conditions += " and programme = '{}'".format(filters.get("programme"))
	if filters.get("semester"):
		student_conditions += " and semester = '{}'".format(filters.get("semester"))

	# Only fetch halls from submitted timetables
	students = frappe.db.sql(f"""
		SELECT name, student_name, company, programme, semester
		FROM `tabStudent`
		WHERE 1 = 1 {student_conditions}
		ORDER BY name asc
	""", as_dict=True)

	cond = ""
	if filters.get("module"):
		cond = " and module = '{}'".format(filters.get("module"))
	modules = frappe.db.sql("""
		SELECT module
		FROM `tabModule Enrolment Key`
		WHERE docstatus = 1 and college = '{}' and
		programme = '{}' and academic_term = '{}'
		{}
	""".format(filters.get("college"), filters.get("programme"), filters.get("academic_term"),  cond), as_dict=True)

	# Build data rows
	data = []
	
	# For each date, create separate rows for each hall
	for s in students:
		row = {}
		
		# Add Day and Date
		row["student"] = s.name
		row["student_name"] = s.student_name
		row["college"] = s.company
		row["programme"] = s.programme
		row["semester"] = s.semester
		for m in modules:
			if frappe.db.exists("Module College", {"module_semester": filters.get("semester"), "programme": filters.get("programme"), "college": filters.get("college"), "parent": m.module}):
				if frappe.db.exists("Module Enrolment", {"student": s.name, "course": m.module, "program": s.programme, "semester": filters.get("semester"), "college": s.company, "academic_term": filters.get("academic_term"), "docstatus": 1}):
					row[str(m.module).lower()] = "Enrolled"
				else:
					if frappe.db.exists("Module Enrolment Key", {"module": m.module, "programme": s.programme, "college": s.company, "academic_term": filters.get("academic_term"), "docstatus": 1}):
						row[str(m.module).lower()] = "Not Enrolled"
					else:
						row[str(m.module).lower()] = "Module Key not generated"

		# Initialize total students and invigilators for this hall and date
		# total_students = 0
		# invigilators_list = []
		
		# # For each time slot
		# for slot in unique_time_slots:
		# 	for e in exams:
		# 		# Accumulate total students and invigilators for this hall/date
		# 		total_students += e['total_students'] if e['total_students'] else 0
		# 		if e['invigilators']:
		# 			invigilators_list.append(e['invigilators'])
				
		# 		# Format the cell content with exam details
		# 		cell_text = f"""
		# 		<div style="padding: 5px; border-bottom: 1px solid #eee;">
		# 			{e['modules']}<br>
		# 			Students: {e['total_students'] or 0}<br>
		# 			Invigilators: {e['invigilators'] or '-'}
		# 		</div>
		# 		"""
		# 		cell_content.append(cell_text)
			
		# 	col_name = f"time_{exam_date}_{format_time(slot[0])}-{format_time(slot[1])}"
		# 	row[col_name] = "".join(cell_content) if cell_content else "<div style='color: #999; text-align: center;'>-</div>"
		
		# 	# Add total students and invigilators to the row
		# 	row[f"total_students_{exam_date}"] = total_students
			
		# 	# Remove duplicates and join invigilators
		# 	unique_invigilators = []
		# 	for inv in invigilators_list:
		# 		for inv_name in inv.split(', '):
		# 			if inv_name not in unique_invigilators and inv_name.strip():
		# 				unique_invigilators.append(inv_name.strip())
		# 	row[f"invigilators_{exam_date}"] = ', '.join(unique_invigilators) if unique_invigilators else "-"
			
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
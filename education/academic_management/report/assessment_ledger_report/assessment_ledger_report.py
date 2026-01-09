# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cstr
from frappe import msgprint, _


def execute(filters=None):
    columns = get_columns()          # no argument needed
    query = construct_query(filters) # singular is clearer
    data = get_data(query, filters)
    return columns, data

def get_columns():
    return [
		{"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "options": " ", "width": 100},
        {"fieldname": "student", "label": "Student", "fieldtype": "Link", "options": "Student", "width": 140},
        {"fieldname": "student_name", "label": "Student Name", "fieldtype": "Data", "width": 120},
        {"fieldname": "module", "label": "Module", "fieldtype": "Link", "options": "Module", "width": 110},
        {"fieldname": "assessment_component", "label": "Assessment Component", "fieldtype": "Link", "options": "Assessment Component", "width": 120},
        {"fieldname": "academic_term", "label": "Academic Term", "fieldtype": "Link", "options": "Academic Term", "width": 120},
        {"fieldname": "semester", "label": "Sem", "fieldtype": "Link", "options": "Semester", "width": 50},
		{"fieldname": "has_reassessment", "label": "Has Reassessment", "fieldtype": "Check", "width": 50},
        {"fieldname": "total_marks", "label": "Total Marks", "fieldtype": "Float", "width": 70},
        {"fieldname": "passing_marks", "label": "Passing Marks", "fieldtype": "Float", "width": 70},
        {"fieldname": "marks_obtained", "label": "Marks Obtained", "fieldtype": "Float", "width": 70},
		{"fieldname": "assessment_weightage", "label": "Assessment Weightage", "fieldtype": "Float", "width": 70},
        {"fieldname": "weightage_achieved", "label": "Weightage Achieved", "fieldtype": "Float", "width": 70},
		{"fieldname": "academic_year", "label": "Academic Year", "fieldtype": "Link", "options": "Academic Year", "width": 120},
		{"fieldname": "college", "label": "College", "fieldtype": "Link", "options": "Company", "width": 150},
		{"fieldname": "tutor", "label": "Tutor", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"fieldname": "tutor_name", "label": "Tutor Name", "fieldtype": "Data", "width": 150},
        {"fieldname": "programme", "label": "Programme", "fieldtype": "Link", "options": "Programme", "width": 150},
        {"fieldname": "reference_type", "label": "Reference Type", "fieldtype": "Link", "options": "DocType", "width": 150},
        {"fieldname": "reference_name", "label": "Reference Name", "fieldtype": "Dynamic Link", "options": "reference_type", "width": 150},
        {"fieldname": "is_cancelled", "label": "Is Cancelled", "fieldtype": "Check", "options": "", "width": 150},
    ]
def construct_query(filters):
    conditions = get_conditions(filters)
    query = f"""
        SELECT student, student_name, posting_date, college, programme, module, assessment_component,
       tutor, tutor_name, academic_year, academic_term, semester,
       total_marks, passing_marks, marks_obtained,
       assessment_weightage, weightage_achieved, has_reassessment,
       reference_type, reference_name, is_cancelled
        FROM `tabAssessment Ledger`
        WHERE 1=1 {conditions}
        ORDER BY student, creation, has_reassessment ASC, module, assessment_component

    """
    return query

def get_conditions(filters):
    conditions = ""
    if filters.get("college"):
        conditions += f" AND college = '{filters.get('college')}'"
    if filters.get("academic_year"):
        conditions += f" AND academic_year = '{filters.get('academic_year')}'"
    if filters.get("academic_term"):
        conditions += f" AND academic_term = '{filters.get('academic_term')}'"
    if filters.get("semester"):
        conditions += f" AND semester = '{filters.get('semester')}'"
    if filters.get("module"):
        conditions += f" AND module = '{filters.get('module')}'"
    if filters.get("tutor"):
        conditions += f" AND tutor = '{filters.get('tutor')}'"
    if filters.get("student"):
        conditions += f" AND student = '{filters.get('student')}'"
    if filters.get("assessment_component"):
        conditions += f" AND assessment_component = '{filters.get('assessment_component')}'"

    if not filters.get("show_previous_attempts"):
        conditions += " AND has_reassessment = 0"
    if not filters.get("show_cancelled_entries"):
        conditions += " AND is_cancelled = 0"
    
    return conditions

def get_data(query, filters):
    return frappe.db.sql(query, as_dict=True)
# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Sl. No."), "fieldname": "sl_no", "fieldtype": "Int", "width": 80},
        {"label": _("College"), "fieldname": "college", "fieldtype": "Data", "width": 200},
        {"label": _("Student ID"), "fieldname": "student_id", "fieldtype": "Data", "width": 120},
        {"label": _("Student Name"), "fieldname": "student_name", "fieldtype": "Data", "width": 180},
        {"label": _("Programme"), "fieldname": "programme", "fieldtype": "Data", "width": 150},
        {"label": _("Semester"), "fieldname": "semester", "fieldtype": "Data", "width": 120},
        {"label": _("Failed/Passed Modules Count"), "fieldname": "module_count", "fieldtype": "Int", "width": 200},
        {"label": _("Failed/Passed Module Codes"), "fieldname": "module_codes", "fieldtype": "Data", "width": 250},
        {"label": _("Result Status"), "fieldname": "result_status", "fieldtype": "Data", "width": 180}
    ]

def get_data(filters):
    data = []
    
    # Get the current user's company (college)
    user_company = get_user_company()
    if not user_company:
        frappe.msgprint(_("No company associated with your account. Please contact administrator."))
        return data
    
    # Get filters
    company = filters.get("company")
    programme = filters.get("programme")
    academic_term = filters.get("academic_term")
    semester = filters.get("semester")
    student_section = filters.get("student_section")
    
    # Base conditions - always filter by user's company
    conditions = f"rd.college = '{user_company}'"
    
    # Add additional filters if provided
    if programme:
        conditions += f" AND rd.programme = '{programme}'"
    if academic_term:
        conditions += f" AND rd.academic_term = '{academic_term}'"
    if semester:
        conditions += f" AND rd.semester = '{semester}'"
    if student_section:
        conditions += f" AND rd.student_section = '{student_section}'"
    
    # Query to get result declarations
    result_declarations = frappe.db.sql(f"""
        SELECT 
            rd.name,
            rd.college,
            rd.programme,
            rd.semester,
            rd.academic_term,
            rd.student_section,
            rd.docstatus
        FROM `tabResult Declaration` rd
        WHERE {conditions}
        AND rd.docstatus = 1
    """, as_dict=True)
    
    if not result_declarations:
        return data
    
    sl_no = 1
    
    for rd in result_declarations:
        # Get all items for this result declaration
        items = frappe.db.sql("""
            SELECT 
                rdi.student,
                rdi.student_name,
                rdi.module,
                rdi.overall_passed,
                rdi.remark
            FROM `tabResult Declaration Item` rdi
            WHERE rdi.parent = %s
        """, (rd.name), as_dict=True)
        
        if not items:
            continue
        
        # Group by student
        student_results = {}
        for item in items:
            student_id = item.student
            if student_id not in student_results:
                student_results[student_id] = {
                    "student_name": item.student_name,
                    "modules": [],
                    "failed_modules": []
                }
            
            module_info = {
                "module": item.module,
                "passed": item.overall_passed,
                "remark": item.remark
            }
            student_results[student_id]["modules"].append(module_info)
            
            if not item.overall_passed:
                student_results[student_id]["failed_modules"].append(item.module)
        
        # Process each student's results
        for student_id, student_data in student_results.items():
            total_modules = len(student_data["modules"])
            failed_modules = student_data["failed_modules"]
            failed_count = len(failed_modules)
            
            # Determine result status
            if failed_count >= 3:
                result_status = "Repeat / Failed "
            else:
                result_status = "Pass"
            
            # Prepare module codes string
            module_codes_str = ", ".join(failed_modules) if failed_modules else "None"
            
            # Add row to data
            data.append({
                "sl_no": sl_no,
                "college": rd.college,  # Display company as college
                "student_id": student_id,
                "student_name": student_data["student_name"],
                "programme": rd.programme,
                "semester": rd.semester,
                "module_count": f"{failed_count}/{total_modules}",  # Format: failed/total
                "module_codes": module_codes_str,
                "result_status": result_status
            })
            
            sl_no += 1
    
    return data

def get_user_company():
    """
    Get the company associated with the current user.
    Checks the Employee doctype where user_id matches the session user.
    """
    user = frappe.session.user
    
    # Query to get employee with matching user_id
    employee = frappe.db.sql("""
        SELECT name, company, employee_name
        FROM `tabEmployee`
        WHERE user_id = %s
        AND status = 'Active'
    """, (user), as_dict=True)
    
    if employee:
        return employee[0].get("company")
    
    return None
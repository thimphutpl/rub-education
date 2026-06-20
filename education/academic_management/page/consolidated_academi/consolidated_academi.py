import frappe

@frappe.whitelist()
def get_results(student=None, program=None, company=None):
    """
    Get results for a specific student or all students under a program/company
    """
    if not student and not program and not company:
        frappe.throw("Please provide either student, program, or company")
    
    # If student is provided (with optional company filter)
    if student:
        # Verify the student exists
        if not frappe.db.exists("Student", student):
            frappe.throw(f"Student {student} does not exist")
        
        # If company is provided, verify student belongs to that company
        if company:
            student_company = frappe.db.get_value("Student", student, "company")
            if student_company != company:
                frappe.throw(f"Student {student} does not belong to company {company}")
        
        # Get results for single student (using your working function)
        return get_student_results(student)
    
    # If program or company is provided, get all students under that program/company
    if program or company:
        conditions = []
        values = []
        
        if program:
            conditions.append("s.programme = %s")
            values.append(program)
        if company:
            conditions.append("s.company = %s")
            values.append(company)
        
        where_clause = " AND ".join(conditions)
        
        students_list = frappe.db.sql(f"""
            SELECT DISTINCT s.name as student_id, s.student_name
            FROM `tabStudent` s
            INNER JOIN `tabModule Enrolment` me ON me.student = s.name
            WHERE {where_clause} AND me.docstatus = 1
        """, values, as_dict=1)
        
        all_results = []
        for stu in students_list:
            student_result = get_student_results(stu.student_id)
            if student_result.get("results"):
                all_results.append(student_result)
        
        return {
            "students": all_results,
            "total_students": len(all_results)
        }

def get_student_results(student):
    """Your working function for a single student"""
    if not student:
        frappe.throw("Student is required")

    # Get modules with semester for the student
    modules = frappe.db.sql("""
        SELECT semester, course, m.module_credit as credit 
        FROM `tabModule Enrolment` me 
        INNER JOIN `tabModule` m ON me.course = m.name 
        WHERE me.student = %s
        AND me.docstatus = 1
        ORDER BY me.semester
    """, (student,), as_dict=1)

    result = []

    for m in modules:
        marks = frappe.db.sql("""
            SELECT 
                COALESCE(rea.weightage_obtained, 0) AS total,
                rea.passed,
                rea.academic_year
            FROM `tabResult Entry Item` rea
            INNER JOIN `tabResult Entry` re 
                ON rea.parent = re.name
            WHERE 
                re.student = %s
                AND rea.module = %s
        """, (student, m.course), as_dict=1)

        weighting = frappe.db.sql("""
            SELECT awi.weightage as weightage 
            FROM `tabProgram Weightage` pw 
            INNER JOIN `tabAcademic Weightage Item` awi ON pw.academic_weightage = awi.parent 
            WHERE awi.semester = %s
        """, (m.semester), as_dict=1)

        total = marks[0].total if marks and marks[0].total else 0
        year_of_passing = marks[0].academic_year if marks and marks[0].academic_year else 'Not Defined'
        weightage = weighting[0].weightage if weighting and weighting[0].weightage else 0

        result.append({
            "semester": m.semester,
            "module": m.course,
            "credit": m.credit,
            "weighting": weightage,
            "total": total,
            "year_of_passing": year_of_passing
        })

    return {
        "student": frappe.db.get_value("Student", student, "student_name"),
        "results": result
    }
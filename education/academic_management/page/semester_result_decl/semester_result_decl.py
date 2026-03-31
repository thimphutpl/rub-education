import frappe

@frappe.whitelist()
def get_results(college, programme, academic_term, student_section):

    # 🔹 Get modules
    modules = frappe.db.sql("""
        SELECT module
        FROM `tabModule Enrolment Key`
        WHERE college=%s
        AND programme=%s
        AND academic_term=%s
        AND student_section=%s 
        AND docstatus = 1
    """, (college, programme, academic_term, student_section), as_dict=1)

    module_list = [m.module for m in modules]

    # # 🔹 Get students
    students = frappe.db.sql("""
        SELECT student, student_name
        FROM `tabModule Enrolment`
        WHERE college=%s
        AND program=%s
        AND academic_term=%s
        AND student_section=%s
        And docstatus =1
    """, (college, programme, academic_term, student_section), as_dict=1)

    result = []

    for stu in students:
        student_data = {
            "student_no": stu.student,
            "student_name": stu.student_name,
            "results": {}
        }

        for m in module_list:
            # 🔹 Replace with your real marks table
            marks = frappe.db.sql("""
                SELECT 
                    SUM(CASE 
                        WHEN ac.assessment_component_type IN ('Continuous Assessment', 'Continuous Assessment (Theory)')
                        THEN al.weightage_achieved ELSE 0 END) AS ca,

                    SUM(CASE 
                        WHEN ac.assessment_component_type = 'Semester Exam'
                        THEN al.weightage_achieved ELSE 0 END) AS se

                FROM `tabAssessment Ledger` al
                INNER JOIN `tabAssessment Component` ac 
                    ON al.assessment_component = ac.name

                WHERE 
                    al.student = %s
                    AND al.module = %s
                    and is_cancelled = 0
            """, (stu.student, m), as_dict=1)

            if marks:
                ca = marks[0].ca or 0
                se = marks[0].se or 0
                total = ca + se

                student_data["results"][m] = {
                    "ca": ca,
                    "se": se,
                    "tl": total
                }
            else:
                student_data["results"][m] = {
                    "ca": 0,
                    "se": 0,
                    "tl": 0
                }

        result.append(student_data)
  
   

    return {
        "modules": module_list,
        "students": result
    }
import frappe

# @frappe.whitelist()
# def get_results(student):

#     # 🔹 Get modules
#     modules = frappe.db.sql("""
#         select semester, course from `tabModule Enrolment` where student='EDU-STU-2025-00001';
#     """, (college, programme, academic_term, student_section), as_dict=1)

#     module_list = [m.module for m in modules]

#     # # 🔹 Get students
#     students = frappe.db.sql("""
#         SELECT student, student_name
#         FROM `tabModule Enrolment`
#         WHERE college=%s
#         AND program=%s
#         AND academic_term=%s
#         AND student_section=%s
#         And docstatus =1
#     """, (college, programme, academic_term, student_section), as_dict=1)

#     result = []

#     for stu in students:
#         student_data = {
#             "student_no": stu.student,
#             "student_name": stu.student_name,
#             "results": {}
#         }

#         for m in module_list:
#             # 🔹 Replace with your real marks table
#             marks = frappe.db.sql("""
#                 SELECT 
#                     SUM(CASE 
#                         WHEN ac.assessment_component_type IN ('Continuous Assessment', 'Continuous Assessment (Theory)')
#                         THEN al.weightage_achieved ELSE 0 END) AS ca,

#                     SUM(CASE 
#                         WHEN ac.assessment_component_type = 'Semester Exam'
#                         THEN al.weightage_achieved ELSE 0 END) AS se

#                 FROM `tabAssessment Ledger` al
#                 INNER JOIN `tabAssessment Component` ac 
#                     ON al.assessment_component = ac.name

#                 WHERE 
#                     al.student = %s
#                     AND al.module = %s
#                     and is_cancelled = 0
#             """, (stu.student, m), as_dict=1)

#             if marks:
#                 ca = marks[0].ca or 0
#                 se = marks[0].se or 0
#                 total = ca + se

#                 student_data["results"][m] = {
#                     "ca": ca,
#                     "se": se,
#                     "tl": total
#                 }
#             else:
#                 student_data["results"][m] = {
#                     "ca": 0,
#                     "se": 0,
#                     "tl": 0
#                 }

#         result.append(student_data)
  
   

#     return {
#         "modules": module_list,
#         "students": result
#     }

@frappe.whitelist()
def get_results(student):
    if not student:
        frappe.throw("Student is required")

    # 🔹 Get modules with semester for the student
    #  SELECT semester, course
    #     FROM `tabModule Enrolment`
    #     WHERE student = %s
    #       AND docstatus = 1
    #     ORDER BY semester
    modules = frappe.db.sql("""
        SELECT semester, course, m.module_credit as credit 
        FROM `tabModule Enrolment` me inner join 
        `tabModule` m on me.course= m.name where 
        me.student = %s
        AND me.docstatus = 1
        ORDER BY me.semester;
    """, (student,), as_dict=1)

    result = []

    for m in modules:
        marks = frappe.db.sql("""
            SELECT 
                SUM(al.weightage_achieved) AS total
            FROM `tabAssessment Ledger` al
            INNER JOIN `tabAssessment Component` ac 
                ON al.assessment_component = ac.name
            WHERE al.student = %s
              AND al.module = %s
              AND al.is_cancelled = 0
        """, (student, m.course), as_dict=1)

        weighting = frappe.db.sql("""
            SELECT awi.weightage as weightage from `tabProgram Weightage` 
            pw inner join `tabAcademic Weightage Item` awi on 
            pw.academic_weightage=awi.parent where awi.semester=%s;
        """, (m.semester), as_dict=1)

        total = marks[0].total or 0 if marks else 0
        weightage = weighting[0].weightage or 0 if weighting else 0


        result.append({
            "semester": m.semester,
            "module": m.course,
            "credit":m.credit,
            "weighting":weightage,
            "total": total
        })

    return {
        "student": frappe.get_value("Student", student, "student_name"),
        "results": result
    }
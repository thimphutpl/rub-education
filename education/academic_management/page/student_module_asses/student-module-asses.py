# data = frappe.db.sql(
#     """
#     SELECT 
#         al.student,
#         al.module,
#         al.programme,
#         al.assessment_component,
#         ac.assessment_component_type,
#         al.weightage_achieved
#     FROM `tabAssessment Ledger` al
#     INNER JOIN `tabAssessment Component` ac 
#         ON al.assessment_component = ac.name
#     WHERE 
#         al.college = %(college)s
#         AND al.academic_term = %(academic_term)s
#         AND al.module = %(module)s
#         AND al.is_cancelled = 0
#     ORDER BY al.student, ac.assessment_component_type
#     """,
#     {
#         "college": college,
#         "academic_term": academic_term,
#         "module": module
#     },
#     as_dict=True
# )
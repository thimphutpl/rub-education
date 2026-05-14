import frappe
from frappe import _

@frappe.whitelist()
def get_ca_report(module_enrollment):

    values = frappe.get_value(
        "Module Enrolment Key",
        module_enrollment,
        ["college", "programme", "academic_term", "module"],
        as_dict=True
    )

    if not values:
        frappe.throw(_("Module Enrolment Key not found"))

    # =========================
    # COMPONENTS
    # =========================
    components = frappe.db.sql("""
        SELECT 
            mai.assessment_name
        FROM `tabModule Assessment Item` mai
        INNER JOIN `tabModule Assessment Criteria` mac 
            ON mai.parent = mac.name
        WHERE 
            mac.college = %s
            AND mac.academic_term = %s
            AND mac.programme = %s
            AND mac.module = %s
            AND mai.docstatus=1
        ORDER BY mai.idx
    """, (values.college, values.academic_term, values.programme, values.module), as_dict=True)

    # frappe.throw(str(components))

    # =========================
    # RAW DATA
    # =========================
    rows = frappe.db.sql("""
        SELECT 
            al.student,
            al.student_name,
            al.assessment_component,
            al.weightage_achieved
        FROM `tabAssessment Ledger` al
        WHERE 
            al.college = %(college)s
            AND al.academic_term = %(academic_term)s
            AND al.module = %(module)s
            AND al.programme = %(programme)s
            AND al.is_cancelled = 0
            And al.has_reassessment = 0
    """, values, as_dict=True)

    # =========================
    # STEP 1: AGGREGATE PER STUDENT + COMPONENT
    # =========================
    temp = {}

    for r in rows:
        key = (r.student, r.assessment_component)

        if key not in temp:
            temp[key] = {
                "student": r.student,
                "student_name": r.student_name,
                "component": r.assessment_component,
                "value": 0
            }

        temp[key]["value"] += r.weightage_achieved or 0

    # =========================
    # STEP 2: BUILD FINAL STRUCTURE
    # =========================
    students = {}

    for t in temp.values():
        sid = t["student"]

        if sid not in students:
            students[sid] = {
                "student": sid,
                "student_name": t["student_name"],
                "assessments": {},
                "total": 0
            }

        students[sid]["assessments"][t["component"]] = t["value"]
        students[sid]["total"] += t["value"]


    return {
        "components": components,
        "students": list(students.values())
    }
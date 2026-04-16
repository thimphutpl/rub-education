import frappe
from frappe.utils import today

@frappe.whitelist()
def get_timetable(college, programme, academic_term):
    timetable = frappe.get_all(
        "Timetable Schedule Entry",
        filters={"college": college, "programme": programme, "academic_term": academic_term},
        fields=["day","from_time","to_time","module_code","tutor","class_type","tutor_name","room_name"],
        order_by="from_time asc"
    )

    constraint = frappe.get_doc("Timetable Constraints", {"academic_term":"2025 Spring Semester"})
    blocked = []
    if timetable:
        for p in constraint.periods:
            period_name = p.period_name or "Non-Academic"
            for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
                if getattr(p, d):
                    blocked.append({
                        "day": d.capitalize(),
                        "from_time": p.from_time,
                        "to_time": p.to_time,
                        "period_name": period_name
                    })

    return {
        "timetable": timetable,
        "blocked": blocked
    }

@frappe.whitelist()
def get_student_details(user):
    college = ""
    programme = ""
    current_academic_term = ""
    if frappe.db.exists("Student", {"user": user}):
        college = frappe.db.get_value("Student", {"user": user}, "company")
        programme = frappe.db.get_value("Student", {"user": user}, "programme")
    current_at = frappe.db.get_value("Academic Term", {"term_start_date": ["<=", today()], "term_end_date": [">=", today()], "college": college})
    return college, programme, current_at

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
        # marks = frappe.db.sql("""
        #     SELECT 
        #         SUM(al.weightage_achieved) AS total
        #     FROM `tabAssessment Ledger` al
        #     INNER JOIN `tabAssessment Component` ac 
        #         ON al.assessment_component = ac.name
        #     WHERE al.student = %s
        #       AND al.module = %s
        #       AND al.is_cancelled = 0

            
        # """, (student, m.course), as_dict=1)

        marks = frappe.db.sql("""
            SELECT 
            COALESCE(rea.ca, 0) AS ca,
            COALESCE(rea.se, 0) AS se,
            COALESCE(rea.weightage_obtained, 0) AS total,
            rea.passed as passed,
            rea.academic_year

        FROM `tabResult Entry Item` rea
        INNER JOIN `tabResult Entry` re 
            ON rea.parent = re.name

        WHERE 
            re.student = %s
            AND rea.module = %s
            
        """, (student, m.course), as_dict=1)

        # frappe.throw(str(marks))

        weighting = frappe.db.sql("""
            SELECT awi.weightage as weightage from `tabProgram Weightage` 
            pw inner join `tabAcademic Weightage Item` awi on 
            pw.academic_weightage=awi.parent where awi.semester=%s;
        """, (m.semester), as_dict=1)

        total = marks[0].total or 0 if marks else 0
        ca = marks[0].ca or 0 if marks else 0
        se = marks[0].se or 0 if marks else 0
        passed = marks[0].passed or 0 if marks else 0
        year_of_passing = marks[0].academic_year or 0 if marks else 'Not Defined'
        weightage = weighting[0].weightage or 0 if weighting else 0


        result.append({
            "semester": m.semester,
            "module": m.course,
            "credit":m.credit,
            "weighting":weightage,
            "ca":ca,
            "se":se,
            "total": total,
            "year_of_passing":year_of_passing,
            "passed":passed
        })

    # frappe.throw(frappe.as_json(result))

    return {
        "student": frappe.get_value("Student", student, "student_name"),
        "results": result
    }


@frappe.whitelist()
def apply_review(student, module, semester,request_type):
    # frappe.throw('hi')
    # frappe.throw((academic_term))
    
    doc = frappe.new_doc("Examination Review Application")
    doc.exam_review_type = request_type
    doc.student = student
    doc.module = module
    doc.semester = semester

    # doc.student_name = 'kinley Zangmo'
    # doc.college ='Gedu College of Business Studies'
    # doc.academic_term='2026-Autum Semester-GCBS'
    # doc.programme ='Bachelor of Business Intelligence (Majors: Financial Engineering and Machine Learnining & Automation)'

    std_name = frappe.db.get_value("Student",{"name":student},"student_name")
    college = frappe.db.get_value("Student",{"name":student},"company")
    programme = frappe.db.get_value("Student",{"name":student},"programme")
    records = frappe.get_all(
        "Module Enrolment",
        filters={
            "student": student,
            "course": module
        },
        fields=["academic_term"],
        order_by="enrollment_date desc",
        limit=1
    )

    academic_term = records[0].academic_term if records else None
   
    
    doc.student_name = std_name
    doc.college = college
    doc.programme =programme
    doc.assessment_component = "Semester Exam"
    doc.academic_term=academic_term
   

    doc.save()
    frappe.db.commit()



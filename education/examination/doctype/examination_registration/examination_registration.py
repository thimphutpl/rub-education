# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _

class ExaminationRegistration(Document):
    def validate(self):
        self.check_assessment_component()
        self.check_duplicate_ass_component()
        self.check_duplicate_ra()
        self.fetch_exam_registration()
        
    def on_submit(self):
        self.check_exam_marks_entry()
        
    def check_duplicate_ra(self):
        duplicate = frappe.db.get_value(
            "Examination Registration",
            {
                "reassesment": 1,
                "examination_registration": self.examination_registration,
                "docstatus": 1
            },
            "name"
        )
        
        if duplicate:
            frappe.throw(
                f"Reassessment already registered for the regular exam <b>{self.examination_registration}</b>. "
                f"The Registered Number is <a href='/app/examination-registration/{duplicate}' target='_blank'>{duplicate}</a>",
                title="Duplicate Reassessment Found"
            )
                
    def fetch_exam_registration(self):
        if self.reassesment:
            # Get assessment component to check role
            assessment_component = frappe.db.get_value(
                "Assessment Component",
                self.assessment_component,
                "assessment_role"
            )
            
            # Build query based on assessment role
            if assessment_component == "Exam Cell":
                exam_registration = frappe.db.sql("""
                    SELECT name 
                    FROM `tabExamination Registration`
                    WHERE module = %s
                    AND semester = %s
                    AND academic_term = %s
                    AND company = %s
                    AND assessment_component = %s
                    AND docstatus = 1
                    ORDER BY posting_date DESC 
                    LIMIT 1
                """, 
                (self.module, self.semester, self.academic_term, self.company, 
                 self.assessment_component),
                as_dict=True)
            else:
                exam_registration = frappe.db.sql("""
                    SELECT name 
                    FROM `tabExamination Registration`
                    WHERE module = %s
                    AND semester = %s
                    AND academic_term = %s
                    AND company = %s
                    AND assessment_component = %s
                    AND tutor = %s
                    AND docstatus = 1
                    ORDER BY posting_date DESC 
                    LIMIT 1
                """, 
                (self.module, self.semester, self.academic_term, self.company, 
                 self.assessment_component, self.tutor),
                as_dict=True)

            if exam_registration:
                self.examination_registration = exam_registration[0].get('name')
            else:
                frappe.throw(f"Examination Registration not found for {self.assessment_component}")
                
    def check_exam_marks_entry(self):
        if int(self.reassesment) == 1: 
            exam_registration = frappe.db.exists(
                "Examination Marks Entry",
                {
                    "examination_registration": self.examination_registration,
                    "docstatus": 1
                }
            )
            if not exam_registration:
                frappe.throw(f"You cannot create the reassessment for '{self.examination_registration}' unless you create an examination entry for it first")

    def check_assessment_component(self):
        ass_com = frappe.db.sql("""
            SELECT 1 
            FROM `tabModule Assessment Item` mai
            INNER JOIN `tabModule Assessment Criteria` mac 
                ON mai.parent = mac.name
            WHERE mac.module = %s
                AND mai.assessment_name = %s
                AND mac.academic_term = %s
                AND mac.college = %s
        """, (
            self.module,
            self.assessment_component,
            self.academic_term,
            self.company
        ))

        if not ass_com:
            frappe.throw("The component {} dont exist for module {}".format(self.assessment_component,self.module))
        # Check if the assessment component exists in Module Assessment Item
        # ass_com = frappe.db.exists(
        #     "Module Assessment Item",
        #     {
        #         "parent": self.module,
        #         "assessment_name": self.assessment_component
        #     }
        # )

        # if not ass_com:
        #     frappe.throw(
        #         f"The Assessment Component '{self.assessment_component}' "
        #         f"does not exist for module '{self.module}'"
        #     )

    def check_duplicate_ass_component(self):
        if int(self.reassesment) == 0:
            # Get assessment component to check role
            assessment_component = frappe.db.get_value(
                "Assessment Component",
                self.assessment_component,
                "assessment_role"
            )
            
            # Build query based on assessment role
            if assessment_component == "Exam Cell":
                duplicate = frappe.db.exists(
                    "Examination Registration",
                    {
                        "company": self.company,
                        "assessment_component": self.assessment_component,
                        "module": self.module,
                        "academic_term": self.academic_term,
                        "docstatus": 1
                    }
                )
                tutor_msg = ""
            else:
                duplicate = frappe.db.exists(
                    "Examination Registration",
                    {
                        "company": self.company,
                        "assessment_component": self.assessment_component,
                        "module": self.module,
                        "academic_term": self.academic_term,
                        "tutor": self.tutor,
                        "docstatus": 1
                    }
                )
                tutor_msg = f" for tutor '{self.tutor}'"
                
            if duplicate:
                frappe.throw(f"""
                    The Examination Registration for Assessment Component '{self.assessment_component}'
                    already exists for academic term '{self.academic_term}'{tutor_msg}.
                    You can create registration only for reassessment.
                    """)


@frappe.whitelist()
def get_students(academic_year, academic_term, module, company, tutor, reassesment, assessment_component):
    """Get students for examination registration with attendance percentage"""
    
    # Validate required fields
    required_fields = {
        "assessment_component": "Assessment Component",
        "academic_year": "Academic Year",
        "academic_term": "Academic Term", 
        "module": "Module",
        "company": "College",
        "reassesment": "Reassessment"
    }
    
    for field, label in required_fields.items():
        if not locals().get(field):
            frappe.throw(_("Please select {0}").format(label))
    
    # Get assessment component settings including the flags and role
    assessment_component_settings = frappe.db.get_value(
        "Assessment Component", 
        assessment_component, 
        ["assessment_role", "attendance_included", "disciplinary_included", "credit_clearance_included"],
        as_dict=True
    )
    
    if not assessment_component_settings:
        frappe.throw(_("Assessment Component not found"))
    
    assessment_role = assessment_component_settings.get("assessment_role", "Tutor")
    attendance_included = assessment_component_settings.get("attendance_included", 0)
    disciplinary_included = assessment_component_settings.get("disciplinary_included", 0)
    credit_clearance_included = assessment_component_settings.get("credit_clearance_included", 0)
    
    # Validate tutor only for Tutor role
    if assessment_role == "Tutor" and not tutor:
        frappe.throw(_("Please select Tutor for this assessment component"))
    
    if int(reassesment) == 1:
        all_students = get_reassessment_students(academic_term, module, company, tutor, assessment_component, assessment_role)
    else:
        all_students = get_regular_students(academic_year, academic_term, module, company, tutor, assessment_role)
    
    all_students = calculate_attendance_percentage(all_students)
    
    non_eligible_students = []
    eligible_students = []
    
    # Get data based on checked conditions
    low_attendance_students = {}
    disciplinary_student_ids = set()
    unpaid_student_ids = set()
    if attendance_included:
        low_attendance_students = get_students_with_low_attendance(module, academic_term, company)
    
    if disciplinary_included:
        disciplinary_student_ids = get_students_with_disciplinary_actions(company, academic_term)
    
    if credit_clearance_included:
        unpaid_student_ids = get_students_with_unpaid_credit_clearance(company, academic_term)
    
    for student in all_students:
        student_id = student["student"]
        exclusion_reasons = []
        if attendance_included and student_id in low_attendance_students:
            exclusion_reasons.append(f"Low Attendance ({low_attendance_students[student_id]}%)")
            student["attendance_issue"] = 1
        
        if disciplinary_included and student_id in disciplinary_student_ids:
            exclusion_reasons.append("Disciplinary Action")
            # Get disciplinary details
            disciplinary_details = get_disciplinary_details(student_id, company)
            if disciplinary_details:
                student["disciplinary_issue_type"] = disciplinary_details.get("disciplinary_issue_type", "")
                student["disciplinary_issue_description"] = disciplinary_details.get("issue_description", "")
            student["disciplinary_issue"] = 1
        
        if credit_clearance_included and student_id in unpaid_student_ids:
            exclusion_reasons.append("Unpaid Credit Clearance")
            # Get credit clearance details
            credit_details = get_credit_clearance_details(student_id, company)
            if credit_details:
                student["credit_clearance_amount"] = credit_details.get("amount", 0)
                student["credit_clearance_status"] = credit_details.get("status", "")
            student["credit_issue"] = 1
        
        if exclusion_reasons:
            student["excluded"] = 1
            student["exclusion_reasons"] = ", ".join(exclusion_reasons)
            non_eligible_students.append(student)
        else:
            student["excluded"] = 0
            student["exclusion_reasons"] = ""
            eligible_students.append(student)
    
    # Calculate total counts
    total_students = len(all_students)
    total_non_eligible = len(non_eligible_students)
    total_eligible = len(eligible_students)
    
    result_data = eligible_students + non_eligible_students
    
    response = {
        "students": result_data,
        "summary": {
            "total_students": total_students,
            "total_eligible": total_eligible,
            "total_non_eligible": total_non_eligible,
            "formula": f"{total_eligible} = {total_students} - {total_non_eligible}"
        }
    }
    
    return response


def get_reassessment_students(academic_term, module, company, tutor, assessment_component, assessment_role):
    """Get students from Examination Review Application for reassessment"""
    
    if assessment_role == "Tutor":
        return frappe.db.sql("""
            SELECT 
                student, 
                student_name,
                "Review" as datatype
            FROM `tabExamination Review Application`
            WHERE academic_term = %s
                AND module = %s
                AND college = %s
                AND tutor = %s
                AND assessment_component = %s
                AND exam_review_type = "Exam Re-Assessment"
                AND docstatus = 1
        """, (academic_term, module, company, tutor, assessment_component), as_dict=True)
    else:
        # Exam Cell - get all students without tutor filter
        return frappe.db.sql("""
            SELECT 
                student, 
                student_name,
                "Review" as datatype
            FROM `tabExamination Review Application`
            WHERE academic_term = %s
                AND module = %s
                AND college = %s
                AND assessment_component = %s
                AND exam_review_type = "Exam Re-Assessment"
                AND docstatus = 1
        """, (academic_term, module, company, assessment_component), as_dict=True)


def get_regular_students(academic_year, academic_term, module, company, tutor, assessment_role):
    """Get students from Module Enrolment for regular assessment"""

    # frappe.throw("hi")
    
    if assessment_role == "Tutor":
        # frappe.throw("""
        #     SELECT 
        #         student, 
        #         student_name,
        #         "Course Enrolment" as datatype
        #     FROM `tabModule Enrolment`
        #     WHERE academic_term = '{}'
        #         AND course = '{}'
        #         AND academic_year = '{}'
        #         AND college = '{}'
        #         AND tutor = '{}'
        # """.format(academic_term, module, academic_year, company, tutor))

        
        # return frappe.db.sql("""
        #     SELECT 
        #         student, 
        #         student_name,
        #         "Course Enrolment" as datatype
        #     FROM `tabModule Enrolment`
        #     WHERE academic_term = %s
        #         AND course = %s
        #         AND academic_year = %s
        #         AND college = %s
        #         AND docstatus= 1
        #         AND tutor = %s
        # """, (academic_term, module, academic_year, company, tutor), as_dict=True)

        return frappe.db.sql("""
            select student, student_name,
            "Course Enrolment" as datatype 
            FROM `tabModule Enrolment`
            me inner join `tabModule Enrolment Tutor` 
            met on me.name=met.parent
            WHERE academic_term = %s
                AND me.course = %s
                AND me.academic_year = %s
                AND me.college = %s
                AND me.docstatus= 1
                AND met.tutor = %s
            ;
        """, (academic_term, module, academic_year, company, tutor), as_dict=True)
    else:
        # Exam Cell - get all students without tutor filter
        return frappe.db.sql("""
            SELECT 
                student, 
                student_name,
                "Course Enrolment" as datatype
            FROM `tabModule Enrolment`
            WHERE academic_term = %s
                AND course = %s
                AND academic_year = %s
                AND docstatus= 1
                AND college = %s
        """, (academic_term, module, academic_year, company), as_dict=True)


def calculate_attendance_percentage(students):
    """Calculate attendance percentage for each student"""
    if not students:
        return students
    
    # Get all student IDs
    student_ids = [student["student"] for student in students]
    attendance_data = frappe.db.sql("""
        SELECT 
            student,
            ROUND(
                (SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100,
                2
            ) as attendance_percentage
        FROM `tabStudent Attendance`
        WHERE student IN %s
        AND docstatus= 1
        GROUP BY student
    """, [student_ids], as_dict=True)
    
    attendance_dict = {item["student"]: item["attendance_percentage"] for item in attendance_data}
    
    for student in students:
        student["attendance_percentage"] = attendance_dict.get(student["student"], 0)
    
    return students


def get_students_with_low_attendance(module, academic_term, company):
    """Get students with attendance below 75%"""
    low_attendance_students = frappe.db.sql("""
        SELECT 
            student,
            ROUND(
                (SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100,
                2
            ) as attendance_percentage
        FROM `tabStudent Attendance`
        WHERE student IN (
            SELECT student 
            FROM `tabModule Enrolment` 
            WHERE course = %s
                AND academic_term = %s
                AND college = %s
                AND docstatus= 1
        )
        GROUP BY student
        HAVING attendance_percentage < 75
    """, (module, academic_term, company), as_dict=True)
    
    return {item["student"]: item["attendance_percentage"] for item in low_attendance_students}


def get_students_with_disciplinary_actions(company, academic_term):
    """Get list of student IDs who have disciplinary actions"""
    disciplinary_students = frappe.db.sql("""
        SELECT DISTINCT student_code as student
        FROM `tabDisciplinary Action`
        WHERE company = %s
            AND docstatus = 1
            AND decision="Terminate"
            AND student_code IN (
                SELECT student 
                FROM `tabModule Enrolment` 
                WHERE academic_term = %s
                AND college = %s
                AND docstatus= 1
            )
    """, (company, academic_term, company), as_dict=True)
    
    return {student["student"] for student in disciplinary_students}


def get_students_with_unpaid_credit_clearance(company, academic_term):
    """Get list of student IDs who have unpaid credit clearance"""
    try:
        unpaid_students = frappe.db.sql("""
            SELECT DISTINCT student_code as student
            FROM `tabCredit Clearance Details`
            WHERE status = 'Unpaid'
                AND student_code IN (
                    SELECT student 
                    FROM `tabModule Enrolment` 
                    WHERE academic_term = %s
                    AND college = %s
                )
        """, (academic_term, company), as_dict=True)
    except Exception as e:
        frappe.log_error(f"Error fetching unpaid credit clearance: {str(e)}")
        unpaid_students = []
    
    return {student["student"] for student in unpaid_students}


def get_disciplinary_details(student_code, company):
    """Get disciplinary details for a specific student"""
    disciplinary_details = frappe.db.sql("""
        SELECT 
            da.disciplinary_issue_type,
            da.date_of_the_issue
        FROM `tabDisciplinary Action` da
        LEFT JOIN `tabDisciplinary Issue Type` dit ON da.disciplinary_issue_type = dit.name
        WHERE da.student_code = %s
            AND da.company = %s
            AND da.docstatus = 1
        ORDER BY da.date_of_the_issue DESC
        LIMIT 1
    """, (student_code, company), as_dict=True)
    
    return disciplinary_details[0] if disciplinary_details else None


def get_credit_clearance_details(student_code, company):
    """Get credit clearance details for a specific student"""
    try:
        credit_details = frappe.db.sql("""
            SELECT 
                sum(amount) as amount,
                status
            FROM `tabCredit Clearance Details`
            WHERE student_code = %s
                AND status = 'Unpaid'
            ORDER BY creation DESC
        """, (student_code,), as_dict=True)
    except Exception as e:
        frappe.log_error(f"Error fetching credit clearance details: {str(e)}")
        credit_details = []
    
    return credit_details[0] if credit_details else None
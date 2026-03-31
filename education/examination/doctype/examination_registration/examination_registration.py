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
        
    def on_submit(self):
        pass
        
    def check_assessment_component(self):
        # Get assessment role first
        assessment_role = frappe.db.get_value(
            "Assessment Component",
            self.assessment_component,
            "assessment_role"
        )
        
        # For Exam Cell, module is optional - skip the module validation
        if assessment_role == "Exam Cell":
            # Only validate that the assessment component exists without module
            ass_com = frappe.db.sql("""
                SELECT 1 
                FROM `tabModule Assessment Item` mai
                INNER JOIN `tabModule Assessment Criteria` mac 
                    ON mai.parent = mac.name
                WHERE mac.academic_term = %s
                    AND mac.college = %s
                    AND mai.assessment_name = %s
            """, (
                self.academic_term,
                self.company,
                self.assessment_component
            ))
        else:
            # For Tutor role, validate with module
            if not self.module:
                frappe.throw(_("Module is required for Tutor assessment component"))
                
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
            if assessment_role == "Exam Cell":
                frappe.throw("The component {} doesn't exist for this academic term and college".format(self.assessment_component))
            else:
                frappe.throw("The component {} doesn't exist for module {}".format(self.assessment_component, self.module))

    def check_duplicate_ass_component(self):
        if int(self.reassesment) == 0:
            # Get assessment component to check role
            assessment_role = frappe.db.get_value(
                "Assessment Component",
                self.assessment_component,
                "assessment_role"
            )
            
            # Build query based on assessment role
            if assessment_role == "Exam Cell":
                duplicate = frappe.db.exists(
                    "Examination Registration",
                    {
                        "company": self.company,
                        "assessment_component": self.assessment_component,
                        "academic_term": self.academic_term,
                        "docstatus": 1
                    }
                )
                tutor_msg = ""
            else:
                # For Tutor role, module is required
                if not self.module:
                    frappe.throw(_("Module is required for Tutor assessment component"))
                    
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
    """Get students for reassessment from Examination Review Application"""
    
    # Only process reassessment
    if int(reassesment) != 1:
        frappe.throw(_("This function is only for reassessment purposes"))
    
    # Validate required fields
    required_fields = {
        "assessment_component": "Assessment Component",
        "academic_term": "Academic Term", 
        "company": "College",
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
    if assessment_role == "Tutor":
        if not tutor:
            frappe.throw(_("Please select Tutor for this assessment component"))
        if not module:
            frappe.throw(_("Please select Module for this assessment component"))
    
    # Get students from Examination Review Application for reassessment
    all_students = get_reassessment_students(
        academic_term, module, company, tutor, assessment_component, assessment_role
    )
    
    # Calculate attendance percentage for all students
    all_students = calculate_attendance_percentage(all_students, academic_term, company, module, assessment_role)
    
    non_eligible_students = []
    eligible_students = []
    
    # Get data based on checked conditions
    low_attendance_students = {}
    disciplinary_student_ids = set()
    unpaid_student_ids = set()
    
    if attendance_included:
        low_attendance_students = get_students_with_low_attendance(module, academic_term, company, assessment_role)
    
    if disciplinary_included:
        disciplinary_student_ids = get_students_with_disciplinary_actions(company, academic_term, module, assessment_role)
    
    if credit_clearance_included:
        unpaid_student_ids = get_students_with_unpaid_credit_clearance(company, academic_term, module, assessment_role)
    
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
    
    # Base query with correct field names from Examination Review Application
    query = """
        SELECT 
            era.student as student,
            era.student_name as student_name,
            "Examination Review Application" as datatype,
            era.module,
            era.assessment_component,
            era.semester,
            era.academic_term,
            era.college,
            era.tutor,
            era.amount_paid,
            era.journal_entry
        FROM `tabExamination Review Application` era
        WHERE era.academic_term = %s
            AND era.college = %s
            AND era.assessment_component = %s
            AND era.exam_review_type = "Exam Re-Assessment"
            AND era.docstatus = 1
    """
    
    params = [academic_term, company, assessment_component]
    
    if module:
        query += " AND era.module = %s"
        params.append(module)

    if assessment_role == "Tutor" and tutor:
        query += " AND era.tutor = %s"
        params.append(tutor)
    
    query += " ORDER BY era.student_name"
    
    students = frappe.db.sql(query, params, as_dict=True)
    
    if not students:
        frappe.msgprint(_("No reassessment applications found for the given criteria"))
    
    return students


def calculate_attendance_percentage(students, academic_term, company, module=None, assessment_role=None):
    """Calculate attendance percentage for each student"""
    if not students:
        return students
    
    # Get all student IDs
    student_ids = [student["student"] for student in students]
    
    if not student_ids:
        return students
    
    # Build query based on role
    if assessment_role == "Exam Cell" or not module:
        # For Exam Cell, get attendance for all students
        attendance_data = frappe.db.sql("""
            SELECT 
                student,
                ROUND(
                    (SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100,
                    2
                ) as attendance_percentage
            FROM `tabStudent Attendance`
            WHERE student IN %s
            AND docstatus = 1
            GROUP BY student
        """, [student_ids], as_dict=True)
    else:
        # For Tutor role, filter by module
        attendance_data = frappe.db.sql("""
            SELECT 
                sa.student,
                ROUND(
                    (SUM(CASE WHEN sa.status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100,
                    2
                ) as attendance_percentage
            FROM `tabStudent Attendance` sa
            INNER JOIN `tabModule Enrolment` me 
                ON me.student = sa.student 
                AND me.course = %s 
                AND me.academic_term = %s 
                AND me.college = %s
                AND me.docstatus = 1
            WHERE sa.student IN %s
            AND sa.docstatus = 1
            GROUP BY sa.student
        """, (module, academic_term, company, student_ids), as_dict=True)
    
    attendance_dict = {item["student"]: item["attendance_percentage"] for item in attendance_data}
    
    for student in students:
        student["attendance_percentage"] = attendance_dict.get(student["student"], 0)
    
    return students


def get_students_with_low_attendance(module, academic_term, company, assessment_role=None):
    """Get students with attendance below 75%"""
    if assessment_role == "Exam Cell" or not module:
        # For Exam Cell, get low attendance across all modules
        low_attendance_students = frappe.db.sql("""
            SELECT 
                student,
                ROUND(
                    (SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100,
                    2
                ) as attendance_percentage
            FROM `tabStudent Attendance`
            WHERE docstatus = 1
            GROUP BY student
            HAVING attendance_percentage < 75
        """, [], as_dict=True)
    else:
        # For Tutor role, filter by module
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
                    AND docstatus = 1
            )
            AND docstatus = 1
            GROUP BY student
            HAVING attendance_percentage < 75
        """, (module, academic_term, company), as_dict=True)
    
    return {item["student"]: item["attendance_percentage"] for item in low_attendance_students}


def get_students_with_disciplinary_actions(company, academic_term, module=None, assessment_role=None):
    """Get list of student IDs who have disciplinary actions"""
    if assessment_role == "Exam Cell" or not module:
        # For Exam Cell, get all students with disciplinary actions
        disciplinary_students = frappe.db.sql("""
            SELECT DISTINCT student_code as student
            FROM `tabDisciplinary Action`
            WHERE company = %s
                AND docstatus = 1
                AND decision = "Terminate"
        """, (company,), as_dict=True)
    else:
        # For Tutor role, filter by module
        disciplinary_students = frappe.db.sql("""
            SELECT DISTINCT student_code as student
            FROM `tabDisciplinary Action`
            WHERE company = %s
                AND docstatus = 1
                AND decision = "Terminate"
                AND student_code IN (
                    SELECT student 
                    FROM `tabModule Enrolment` 
                    WHERE course = %s
                    AND academic_term = %s
                    AND college = %s
                    AND docstatus = 1
                )
        """, (company, module, academic_term, company), as_dict=True)
    
    return {student["student"] for student in disciplinary_students}


def get_students_with_unpaid_credit_clearance(company, academic_term, module=None, assessment_role=None):
    """Get list of student IDs who have unpaid credit clearance"""
    try:
        if assessment_role == "Exam Cell" or not module:
            # For Exam Cell, get all students with unpaid credit clearance
            unpaid_students = frappe.db.sql("""
                SELECT DISTINCT student_code as student
                FROM `tabCredit Clearance Details`
                WHERE status = 'Unpaid'
            """, (), as_dict=True)
        else:
            # For Tutor role, filter by module
            unpaid_students = frappe.db.sql("""
                SELECT DISTINCT student_code as student
                FROM `tabCredit Clearance Details`
                WHERE status = 'Unpaid'
                    AND student_code IN (
                        SELECT student 
                        FROM `tabModule Enrolment` 
                        WHERE course = %s
                        AND academic_term = %s
                        AND college = %s
                        AND docstatus = 1
                    )
            """, (module, academic_term, company), as_dict=True)
    except Exception as e:
        frappe.log_error(f"Error fetching unpaid credit clearance: {str(e)}")
        unpaid_students = []
    
    return {student["student"] for student in unpaid_students}


def get_disciplinary_details(student_code, company):
    """Get disciplinary details for a specific student"""
    disciplinary_details = frappe.db.sql("""
        SELECT 
            da.disciplinary_issue_type,
            da.issue_description,
            da.date_of_the_issue
        FROM `tabDisciplinary Action` da
        WHERE da.student_code = %s
            AND da.company = %s
            AND da.docstatus = 1
            AND da.decision = "Terminate"
        ORDER BY da.date_of_the_issue DESC
        LIMIT 1
    """, (student_code, company), as_dict=True)
    
    return disciplinary_details[0] if disciplinary_details else None


def get_credit_clearance_details(student_code, company):
    """Get credit clearance details for a specific student"""
    try:
        credit_details = frappe.db.sql("""
            SELECT 
                SUM(amount) as amount,
                status
            FROM `tabCredit Clearance Details`
            WHERE student_code = %s
                AND status = 'Unpaid'
            GROUP BY student_code
        """, (student_code,), as_dict=True)
    except Exception as e:
        frappe.log_error(f"Error fetching credit clearance details: {str(e)}")
        credit_details = []
    
    return credit_details[0] if credit_details else None
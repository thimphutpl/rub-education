# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _
from frappe.utils import get_url
from frappe.email.doctype.email_template.email_template import get_email_template

class IneligibleStudent(Document):
    def validate(self):
        pass  # Remove all validation methods
    
    def on_submit(self):
        pass  # Remove on_submit method


@frappe.whitelist()
def get_students(academic_year, academic_term, company):
    """Get all students for the given academic year, term and company with eligibility status"""
    
    # Validate required fields
    required_fields = {
        "academic_year": "Academic Year",
        "academic_term": "Academic Term", 
        "company": "College"
    }
    
    for field, label in required_fields.items():
        if not locals().get(field):
            frappe.throw(_("Please select {0}").format(label))
    
    # Get all students from Module Enrolment
    all_students = frappe.db.sql("""
        SELECT 
            student, 
            student_name,
            "Course Enrolment" as datatype
        FROM `tabModule Enrolment`
        WHERE academic_term = %s
            AND academic_year = %s
            AND college = %s
            AND docstatus = 1
    """, (academic_term, academic_year, company), as_dict=True)
    
    if not all_students:
        return {
            "students": [],
            "summary": {
                "total_students": 0,
                "total_eligible": 0,
                "total_non_eligible": 0,
                "formula": "0 = 0 - 0"
            }
        }
    
    # Calculate attendance percentage for all students
    all_students = calculate_attendance_percentage(all_students)
    
    # Get data for eligibility checks
    low_attendance_students = get_students_with_low_attendance(academic_term, company)
    disciplinary_student_ids = get_students_with_disciplinary_actions(company, academic_term)
    unpaid_student_ids = get_students_with_unpaid_credit_clearance(company, academic_term)
    
    non_eligible_students = []
    eligible_students = []
    
    for student in all_students:
        student_id = student["student"]
        exclusion_reasons = []
        
        # Check attendance
        if student_id in low_attendance_students:
            exclusion_reasons.append(f"Low Attendance ({low_attendance_students[student_id]}%)")
            student["attendance_issue"] = 1
        
        # Check disciplinary actions
        if student_id in disciplinary_student_ids:
            exclusion_reasons.append("Disciplinary Action")
            disciplinary_details = get_disciplinary_details(student_id, company)
            if disciplinary_details:
                student["disciplinary_issue_type"] = disciplinary_details.get("disciplinary_issue_type", "")
                student["disciplinary_issue_description"] = disciplinary_details.get("issue_description", "")
            student["disciplinary_issue"] = 1
        
        # Check credit clearance
        if student_id in unpaid_student_ids:
            exclusion_reasons.append("Unpaid Credit Clearance")
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
        AND docstatus = 1
        GROUP BY student
    """, [student_ids], as_dict=True)
    
    attendance_dict = {item["student"]: item["attendance_percentage"] for item in attendance_data}
    
    for student in students:
        student["attendance_percentage"] = attendance_dict.get(student["student"], 0)
    
    return students


def get_students_with_low_attendance(academic_term, company):
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
            WHERE academic_term = %s
                AND college = %s
                AND docstatus = 1
        )
        GROUP BY student
        HAVING attendance_percentage < 75
    """, (academic_term, company), as_dict=True)
    
    return {item["student"]: item["attendance_percentage"] for item in low_attendance_students}


def get_students_with_disciplinary_actions(company, academic_term):
    """Get list of student IDs who have disciplinary actions"""
    disciplinary_students = frappe.db.sql("""
        SELECT DISTINCT student_code as student
        FROM `tabDisciplinary Action`
        WHERE company = %s
            AND docstatus = 1
            AND student_code IN (
                SELECT student 
                FROM `tabModule Enrolment` 
                WHERE academic_term = %s
                AND college = %s
                AND docstatus = 1
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
                SUM(amount) as amount,
                status
            FROM `tabCredit Clearance Details`
            WHERE student_code = %s
                AND status = 'Unpaid'
        """, (student_code,), as_dict=True)
    except Exception as e:
        frappe.log_error(f"Error fetching credit clearance details: {str(e)}")
        credit_details = []
    
    return credit_details[0] if credit_details else None


@frappe.whitelist()
def notify_non_eligible_students(docname, non_eligible_students):
    """Send notifications to non-eligible students"""
    
    # Parse the JSON string if it's a string, otherwise use as is
    if isinstance(non_eligible_students, str):
        try:
            non_eligible_students = json.loads(non_eligible_students)
        except json.JSONDecodeError as e:
            frappe.log_error(f"Failed to parse non_eligible_students data: {str(e)}")
            frappe.throw(_("Invalid student data format"))
    
    # Validate that we have a list
    if not isinstance(non_eligible_students, list):
        frappe.throw(_("Invalid student data format. Expected a list."))
    
    # Get the email template from HR Settings
    email_template_name = frappe.db.get_single_value('HR Settings', 'ineligible_student_notification')
    
    if not email_template_name:
        frappe.throw(_("Please configure 'Ineligible Student Notification' email template in HR Settings"))
    
    # Get the email template
    try:
        email_template = frappe.get_doc("Email Template", email_template_name)
    except Exception as e:
        frappe.log_error(f"Failed to fetch email template: {str(e)}")
        frappe.throw(_("Email template '{0}' not found").format(email_template_name))
    
    success_count = 0
    failed_count = 0
    failed_students = []
    
    # Get the Ineligible Student document for context
    try:
        ineligible_doc = frappe.get_doc("Ineligible Student", docname)
    except Exception as e:
        frappe.log_error(f"Failed to fetch Ineligible Student document: {str(e)}")
        frappe.throw(_("Ineligible Student document not found"))
    
    for student_data in non_eligible_students:
        try:
            # Ensure student_data is a dictionary
            if isinstance(student_data, str):
                student_data = json.loads(student_data)
            
            # Get student document to fetch the user/email
            student = frappe.get_doc("Student", student_data.get("student"))
            
            # Get user email from student's user field
            user_email = None
            if student.user:
                user = frappe.get_doc("User", student.user)
                user_email = user.email
            else:
                # Try to get email from student's email field if available
                if hasattr(student, 'student_email') and student.student_email:
                    user_email = student.student_email
            
            if not user_email:
                error_msg = f"No email address found for student: {student_data.get('student_name')}"
                frappe.log_error(error_msg, "Ineligible Student Notification")
                failed_count += 1
                failed_students.append({
                    "student_name": student_data.get("student_name"),
                    "student": student_data.get("student"),
                    "reason": "No email address found"
                })
                continue
            
            # Prepare context for email template
            context = {
                "student_name": student_data.get("student_name"),
                "attendance_percentage": student_data.get("attendance_percentage", 0),
                "disciplinary_issue": student_data.get("disciplinary_issue", ""),
                "financial_issue": student_data.get("financial_issue", ""),
                "exclusion_reasons": student_data.get("exclusion_reasons", ""),
                "academic_year": ineligible_doc.get("academic_year", ""),
                "academic_term": ineligible_doc.get("academic_term", ""),
                "company": ineligible_doc.get("company", ""),
                "consider_attendance": student_data.get("consider_attendance", 0),
                "reason_for_consideration": student_data.get("reason_for_consideration", "")
            }
            
            # Render email content
            subject = frappe.render_template(email_template.subject, context)
            message = frappe.render_template(email_template.response, context)
            
            # Send email
            frappe.sendmail(
                recipients=[user_email],
                subject=subject,
                message=message,
                reference_doctype="Ineligible Student",
                reference_name=docname,
                now=True  # Send immediately
            )
            
            success_count += 1
            frappe.log_error(f"Email sent successfully to {student_data.get('student_name')} ({user_email})", "Ineligible Student Notification")
            
        except Exception as e:
            frappe.log_error(
                f"Failed to send email to {student_data.get('student_name')}: {str(e)}",
                "Ineligible Student Notification"
            )
            failed_count += 1
            failed_students.append({
                "student_name": student_data.get("student_name"),
                "student": student_data.get("student"),
                "reason": str(e)
            })
    
    # Return the result
    return {
        "success": success_count > 0,
        "success_count": success_count,
        "failed_count": failed_count,
        "failed_students": failed_students
    }
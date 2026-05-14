from frappe.model.document import Document
import frappe
import pandas as pd
from frappe.utils.file_manager import get_file
from datetime import datetime, time

class ExamTimetable(Document):
    def validate(self):
        self.validate_capacity()
        self.validate_hall_availability()
        self.validate_student_allocation()

    def validate_capacity(self):
        """
        Validates that the number of students in the child table
        does not exceed the defined capacity.
        """
        if self.capacity:
            try:
                capacity = int(self.capacity)
            except ValueError:
                frappe.throw(f"Capacity value '{self.capacity}' is not a valid number.")

            total_students = len(self.get("exam_timetable_student"))
            if total_students > capacity:
                frappe.throw(
                    f"Number of students {total_students} exceeds the capacity {capacity}."
                )

    def validate_hall_availability(self):
        """
        Validates that no other exam is scheduled in the same exam hall
        within the same time range.
        """
        if not self.room or not self.start_time or not self.end_time or not self.exam_date:
            return

        start_time = self.start_time
        end_time = self.end_time
        
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, "%H:%M:%S").time()

        # Check for conflicting exams in the same hall on the same date
        conflicting_exams = frappe.db.sql("""
            SELECT name, start_time, end_time
            FROM `tabExam Timetable`
            WHERE name != %s
                AND room = %s
                AND exam_date = %s
                AND docstatus < 2
                AND (
                    (start_time <= %s AND end_time > %s) OR
                    (start_time < %s AND end_time >= %s) OR
                    (start_time >= %s AND end_time <= %s)
                )
        """, (self.name or "New", self.room, self.exam_date, start_time, start_time, end_time, end_time, start_time, end_time), as_dict=True)

        if conflicting_exams:
            exam_details = conflicting_exams[0]
            frappe.throw(
                f"Exam Hall '{self.room}' is already booked on {self.exam_date} from {exam_details.start_time} to {exam_details.end_time}. "
            )

    def validate_student_allocation(self):
        """
        Validates that no student is allocated to multiple exams/rooms
        within the same time range and date.
        """
        if not self.start_time or not self.end_time or not self.exam_date:
            return

        current_students = [row.student for row in self.get("exam_timetable_student") if row.student]
        
        if not current_students:
            return

        start_time = self.start_time
        end_time = self.end_time
        
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, "%H:%M:%S").time()

        # Find conflicting student allocations on the same date
        conflicting_allocations = frappe.db.sql("""
            SELECT 
                et.name as exam_timetable,
                et.room,
                et.start_time,
                et.end_time,
                ets.student,
                ets.student_name
            FROM `tabExam Timetable` et
            INNER JOIN `tabExam Timetable Student` ets ON ets.parent = et.name
            WHERE et.name != %s
                AND et.docstatus < 2
                AND et.exam_date = %s
                AND ets.student IN %s
                AND (
                    (et.start_time <= %s AND et.end_time > %s) OR
                    (et.start_time < %s AND et.end_time >= %s) OR
                    (et.start_time >= %s AND et.end_time <= %s)
                )
            ORDER BY ets.student, et.start_time
        """, (
            self.name or "New",
            self.exam_date,
            tuple(current_students), 
            start_time, start_time, 
            end_time, end_time, 
            start_time, end_time
        ), as_dict=True)

        if conflicting_allocations:
            student_conflicts = {}
            for conflict in conflicting_allocations:
                if conflict.student not in student_conflicts:
                    student_conflicts[conflict.student] = []
                student_conflicts[conflict.student].append(conflict)

            error_msg = "The following students are already allocated to other exams on this date during the same time period:\n\n"
            for student, conflicts in student_conflicts.items():
                student_name = conflicts[0].student_name or "Unknown"
                error_msg += f"Student: {student} - {student_name}\n"
                for conf in conflicts:
                    error_msg += f"  • Room: {conf.room}, Time: {conf.start_time} to {conf.end_time} (Exam: {conf.exam_timetable})\n"
                error_msg += "\n"

            frappe.throw(error_msg)


# File Upload Function
@frappe.whitelist()
def upload_excel(file_url, docname):
    """
    Uploads an Excel file and adds students to the ExamTimetable child table.
    Expects columns: Student, Module Enrolment, Module
    """
    try:
        file_doc = get_file(file_url)
        file_path = file_doc[1]
        
        df = pd.read_excel(file_path)
        expected_columns = ["Student", "Module Enrolment", "Module"]
        
        for col in expected_columns:
            if col not in df.columns:
                frappe.throw(f"Missing column '{col}' in Excel file.")
        
        doc = frappe.get_doc("Exam Timetable", docname)
        doc.set("exam_timetable_student", [])  
        
        for _, row in df.iterrows():
            # Verify the module enrolment exists
            module_enrolment = frappe.db.exists("Module Enrolment", row["Module Enrolment"])
            if not module_enrolment:
                frappe.msgprint(f"Warning: Module Enrolment '{row['Module Enrolment']}' not found. Skipping row.")
                continue
                
            doc.append("exam_timetable_student", {
                "student": row["Student"],
                "module_enrolment": row["Module Enrolment"],
                "module": row["Module"]
            })
        
        doc.validate_capacity()
        doc.validate_student_allocation()
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success", "message": f"Successfully imported {len(df)} students"}
    except Exception as e:
        frappe.log_error(f"Error in upload_excel: {str(e)}")
        frappe.throw(f"Error uploading file: {str(e)}")


# Get Students Function - Simplified with only necessary filters
@frappe.whitelist()
def get_students(academic_year, academic_term, college, module, docname=None):
    """
    Fetches students directly from Module Enrolment.
    Only uses filters that match between both doctypes.
    """
    # Validate required fields
    if not all([academic_year, academic_term, college, module]):
        frappe.throw("Please provide Academic Year, Academic Term, College, and Module")

    # Fetch students directly from Module Enrolment
    # The course (module) and other fields are automatically matched
    module_enrolments = frappe.get_all(
        "Module Enrolment",
        filters={
            "college": college,
            "academic_year": academic_year,
            "academic_term": academic_term,
            "course": module,  # 'course' field in Module Enrolment stores the module
            "docstatus": 1
        },
        fields=["name", "student", "student_name", "course", "semester", "program", "student_section"]
    )

    if not module_enrolments:
        frappe.msgprint(f"No students found in Module Enrolment for Module: {module}")
        return []

    # Prepare data - directly from Module Enrolment
    data = []
    for enrolment in module_enrolments:
        data.append({
            "student": enrolment.student,
            "student_name": enrolment.student_name,
            "module_enrolment": enrolment.name,
            "module": enrolment.course,  # 'course' field stores the module
            "program": enrolment.program,
            "semester": enrolment.semester,
            "student_section": enrolment.student_section
        })

    # Remove duplicates based on student
    seen_students = set()
    unique_data = []
    for s in data:
        if s["student"] not in seen_students:
            seen_students.add(s["student"])
            unique_data.append(s)

    # If docname is provided, update the Exam Timetable directly
    if docname:
        doc = frappe.get_doc("Exam Timetable", docname)
        
        # Clear existing students for this module to avoid duplicates
        existing_students = [s for s in doc.exam_timetable_student if s.module != module]
        doc.set("exam_timetable_student", existing_students)

        # Add new students
        for s in unique_data:
            doc.append("exam_timetable_student", {
                "student": s["student"],
                "student_name": s["student_name"],
                "module_enrolment": s["module_enrolment"],
                "module": s["module"]
            })

        doc.validate_capacity()
        doc.validate_student_allocation()
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    return unique_data


# Function to check hall availability
@frappe.whitelist()
def check_hall_availability(room, exam_date, start_time, end_time, current_docname=None):
    """
    Checks if an exam hall is available for the given date and time range.
    """
    if not all([room, exam_date, start_time, end_time]):
        return {"available": False, "message": "Missing required parameters"}
    
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, "%H:%M:%S").time()
    
    conflicting_exams = frappe.db.sql("""
        SELECT name, module, start_time, end_time
        FROM `tabExam Timetable`
        WHERE name != %s
            AND room = %s
            AND exam_date = %s
            AND docstatus < 2
            AND (
                (start_time <= %s AND end_time > %s) OR
                (start_time < %s AND end_time >= %s) OR
                (start_time >= %s AND end_time <= %s)
            )
    """, (current_docname or "", room, exam_date, start_time, start_time, end_time, end_time, start_time, end_time), as_dict=True)
    
    if conflicting_exams:
        exam = conflicting_exams[0]
        return {
            "available": False,
            "message": f"Hall is already booked on {exam_date} for {exam.module} from {exam.start_time} to {exam.end_time}",
            "conflicting_exam": exam
        }
    
    return {"available": True, "message": "Hall is available for this time slot"}


# Function to check student availability
@frappe.whitelist()
def check_student_availability(student, exam_date, start_time, end_time, current_docname=None):
    """
    Checks if a student is available for the given date and time range.
    """
    if not all([student, exam_date, start_time, end_time]):
        return {"available": False, "message": "Missing required parameters"}
    
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, "%H:%M:%S").time()
    
    conflicting_allocations = frappe.db.sql("""
        SELECT 
            et.name as exam_timetable,
            et.room,
            et.start_time,
            et.end_time
        FROM `tabExam Timetable` et
        INNER JOIN `tabExam Timetable Student` ets ON ets.parent = et.name
        WHERE et.name != %s
            AND et.docstatus < 2
            AND et.exam_date = %s
            AND ets.student = %s
            AND (
                (et.start_time <= %s AND et.end_time > %s) OR
                (et.start_time < %s AND et.end_time >= %s) OR
                (et.start_time >= %s AND et.end_time <= %s)
            )
    """, (current_docname or "", exam_date, student, start_time, start_time, end_time, end_time, start_time, end_time), as_dict=True)
    
    if conflicting_allocations:
        exam = conflicting_allocations[0]
        return {
            "available": False,
            "message": f"Student is already allocated on {exam_date} to Room {exam.room} from {exam.start_time} to {exam.end_time} (Exam: {exam.exam_timetable})",
            "conflicting_exam": exam
        }
    
    return {"available": True, "message": "Student is available for this time slot"}
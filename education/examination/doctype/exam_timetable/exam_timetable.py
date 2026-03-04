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
                capacity = int(self.capacity)  # convert to integer
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
        if not self.room or not self.start_time or not self.end_time:
            return  # Skip validation if required fields are missing

        # Convert string times to time objects for comparison
        start_time = self.start_time
        end_time = self.end_time
        
        # If start_time/end_time are strings, convert them to time objects
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, "%H:%M:%S").time()

        # Check for conflicting exams in the same hall
        conflicting_exams = frappe.db.sql("""
            SELECT name, start_time, end_time
            FROM `tabExam Timetable`
            WHERE name != %s
                AND room = %s
                AND docstatus < 2
                AND (
                    (start_time <= %s AND end_time > %s) OR
                    (start_time < %s AND end_time >= %s) OR
                    (start_time >= %s AND end_time <= %s)
                )
        """, (self.name or "New", self.room, start_time, start_time, end_time, end_time, start_time, end_time), as_dict=True)

        if conflicting_exams:
            exam_details = conflicting_exams[0]
            frappe.throw(
                f"Exam Hall '{self.room}' is already booked from {exam_details.start_time} to {exam_details.end_time}. "
            )

    def validate_student_allocation(self):
        """
        Validates that no student is allocated to multiple exams/rooms
        within the same time range.
        """
        if not self.start_time or not self.end_time:
            return  # Skip validation if time fields are missing

        # Get all students in current document
        current_students = [row.student for row in self.get("exam_timetable_student") if row.student]
        
        if not current_students:
            return  # Skip if no students

        # Convert times for comparison
        start_time = self.start_time
        end_time = self.end_time
        
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, "%H:%M:%S").time()

        # Find conflicting student allocations in other exam timetables
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
                AND ets.student IN %s
                AND (
                    (et.start_time <= %s AND et.end_time > %s) OR
                    (et.start_time < %s AND et.end_time >= %s) OR
                    (et.start_time >= %s AND et.end_time <= %s)
                )
            ORDER BY ets.student, et.start_time
        """, (
            self.name or "New", 
            tuple(current_students), 
            start_time, start_time, 
            end_time, end_time, 
            start_time, end_time
        ), as_dict=True)

        if conflicting_allocations:
            # Group conflicts by student for better error message
            student_conflicts = {}
            for conflict in conflicting_allocations:
                if conflict.student not in student_conflicts:
                    student_conflicts[conflict.student] = []
                student_conflicts[conflict.student].append(conflict)

            # Build error message
            error_msg = "The following students are already allocated to other exams during this time period:\n\n"
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
    Validates that the total students do not exceed capacity.
    """
    file_doc = get_file(file_url)
    file_path = file_doc[1]

    df = pd.read_excel(file_path)
    expected_columns = ["Student", "Examination Registration", "Module"]

    for col in expected_columns:
        if col not in df.columns:
            frappe.throw(f"Missing column '{col}' in Excel file.")

    doc = frappe.get_doc("Exam Timetable", docname)
    doc.set("exam_timetable_student", [])  

    for _, row in df.iterrows():
        doc.append("exam_timetable_student", {
            "student": row["Student"],
            "examination_registration": row["Examination Registration"],
            "module": row["Module"]
        })

    doc.validate_capacity()
    doc.validate_student_allocation()  # Also validate student allocation
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return "Success"


# Get Students Function
@frappe.whitelist()
def get_students(academic_year, academic_term, assessment_component, module, company, docname=None):
    """
    Fetches students from Examination Registration and refreshes
    the ExamTimetable child table (no duplicates).
    """
    if not academic_year:
        frappe.throw("Please select Academic Year")
    if not assessment_component:
        frappe.throw("Please select Assessment Component")
    if not academic_term:
        frappe.throw("Please select Academic Term")
    if not module:
        frappe.throw("Please select Module")
    if not company:
        frappe.throw("Please select College")

    exam_regs = frappe.get_all(
        "Examination Registration",
        filters={
            "company": company,
            "academic_year": academic_year,
            "academic_term": academic_term,
            "assessment_component": assessment_component,
            "module": module,
            "docstatus": 1
        },
        fields=["name", "module"]
    )

    data = []
    for reg in exam_regs:
        child_students = frappe.get_all(
            "Exam Students",
            filters={"parent": reg.name},
            fields=["student", "student_name"]
        )
        for s in child_students:
            s["module"] = reg.module
            s["examination_registration"] = reg.name
            data.append(s)

    if docname:
        doc = frappe.get_doc("Exam Timetable", docname)
        doc.set("exam_timetable_student", [])

        for s in data:
            doc.append("exam_timetable_student", {
                "student": s["student"],
                "student_name": s["student_name"],
                "examination_registration": s["examination_registration"],
                "module": s["module"]
            })

        doc.validate_capacity()
        doc.validate_student_allocation()  # Also validate student allocation
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    return data


# Function to check hall availability without saving
@frappe.whitelist()
def check_hall_availability(room, start_time, end_time, current_docname=None):
    """
    Checks if an exam hall is available for the given time range.
    Returns True if available, False if conflicting exam exists.
    """
    if not room or not start_time or not end_time:
        return {"available": False, "message": "Missing required parameters"}
    
    # Convert string times to time objects for comparison
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, "%H:%M:%S").time()
    
    # Check for conflicting exams
    conflicting_exams = frappe.db.sql("""
        SELECT name, module, start_time, end_time
        FROM `tabExam Timetable`
        WHERE name != %s
            AND room = %s
            AND docstatus < 2
            AND (
                (start_time <= %s AND end_time > %s) OR
                (start_time < %s AND end_time >= %s) OR
                (start_time >= %s AND end_time <= %s)
            )
    """, (current_docname or "", room, start_time, start_time, end_time, end_time, start_time, end_time), as_dict=True)
    
    if conflicting_exams:
        exam = conflicting_exams[0]
        return {
            "available": False,
            "message": f"Hall is already booked for {exam.module} from {exam.start_time} to {exam.end_time}",
            "conflicting_exam": exam
        }
    
    return {"available": True, "message": "Hall is available for this time slot"}


# Function to check student availability without saving
@frappe.whitelist()
def check_student_availability(student, start_time, end_time, current_docname=None):
    """
    Checks if a student is available for the given time range.
    Returns True if available, False if student has conflicting exam.
    """
    if not student or not start_time or not end_time:
        return {"available": False, "message": "Missing required parameters"}
    
    # Convert string times to time objects for comparison
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, "%H:%M:%S").time()
    
    # Check for conflicting student allocations
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
            AND ets.student = %s
            AND (
                (et.start_time <= %s AND et.end_time > %s) OR
                (et.start_time < %s AND et.end_time >= %s) OR
                (et.start_time >= %s AND et.end_time <= %s)
            )
    """, (current_docname or "", student, start_time, start_time, end_time, end_time, start_time, end_time), as_dict=True)
    
    if conflicting_allocations:
        exam = conflicting_allocations[0]
        return {
            "available": False,
            "message": f"Student is already allocated to Room {exam.room} from {exam.start_time} to {exam.end_time} (Exam: {exam.exam_timetable})",
            "conflicting_exam": exam
        }
    
    return {"available": True, "message": "Student is available for this time slot"}
# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class ExaminationMarksEntry(Document):
    def validate(self):
        if self.exam_type == 'Regular Assessment':
            self.fetch_exam_registration()
        self.check_duplicate_ass_component()
        # self.check_duplicate_marks_entry()
        self.calculate_weightageAchieved()

    def on_submit(self):
        self.check_earlier_assesment()
        self.create_assessment_ledger()

    def on_cancel(self):
        self.ignore_linked_doctypes = (
            "Assessment Ledger",
        )
        self.cancel_assessment_entry()

    def cancel_assessment_entry(self):
        for i in self.items:
            assessment_ledger = frappe.db.get_value(
                "Assessment Ledger",
                {
                    "reference_name": self.name,
                    
                },
                "name"
            )

            if assessment_ledger:
                frappe.db.sql(
                    '''
                    UPDATE `tabAssessment Ledger`
                    SET is_cancelled = 1
                    WHERE name = %s
                    ''',
                    (assessment_ledger,)
                )

        frappe.db.commit()

    def fetch_exam_registration(self):
        if self.exam_type == 'Regular Assessment':
            return
            
        if self.exam_type in ('Exam Re-Assessment','Exam Recheck','Exam Re-Evaluation'):
            exam_registration = frappe.db.sql("""
                SELECT name 
                FROM `tabExamination Review Application`
                WHERE module = %s
                AND semester = %s
                AND academic_term = %s
                AND college = %s
                AND assessment_component = %s
                AND tutor = %s
                order by posting_date DESC limit 1
            """, 
            (self.module, self.semester, self.academic_term, self.college, self.assessment_component, self.tutor),
            as_dict=True)

            if exam_registration:
                self.examination_registration = exam_registration[0].get('name')
            else:
                frappe.throw("Examination Review Application not found for {}".format(self.assessment_component))
                
    def check_duplicate_marks_entry(self):
        if self.exam_type == 'Regular Assessment':
            duplicate = frappe.db.exists("Examination Marks Entry",{
                "exam_type": self.exam_type,
                "docstatus": 1
            })
        else:
            duplicate = frappe.db.exists("Examination Marks Entry",{
                "exam_type": self.exam_type,
                "docstatus": 1
            })
    
        if duplicate:
            frappe.throw("The Marks entry done already for this combination")
            
    def check_duplicate_ass_component(self):
        pass

    def check_earlier_assesment(self):
        for i in self.items:
            assessment_ledger = frappe.db.get_value(
                "Assessment Ledger",
                {
                    "student": i.student,
                    "assessment_component": self.assessment_component,
                    "module": self.module,
                    "has_reassessment":0
                },
                "name"
            )

            if assessment_ledger:
                frappe.db.sql(
                    '''
                    UPDATE `tabAssessment Ledger`
                    SET has_reassessment = 1
                    WHERE name = %s
                    ''',
                    (assessment_ledger,)
                )

        frappe.db.commit()
    
    def calculate_weightageAchieved(self):
        for i in self.items:
            if not (i.marks_obtained and self.total_marks):
                continue

            condition = f" AND mac.tutor = '{self.tutor}'"

            query = f"""
                SELECT mai.weightage
                FROM `tabModule Assessment Item` mai
                INNER JOIN `tabModule Assessment Criteria` mac 
                    ON mai.parent = mac.name
                WHERE mac.college = '{self.college}'
                AND mac.academic_term = '{self.academic_term}'
                AND mac.programme = '{self.programme}'
                AND mai.assessment_name = '{self.assessment_component}'
                {condition}
            """

            result = frappe.db.sql(query)

            if not result:
                frappe.throw("Weightage not defined for this configuration")

            weightage = result[0][0] or 0

            i.weightage = weightage
            i.weightage_achieved = (
                (i.marks_obtained / self.total_marks) * weightage
            )

    def create_assessment_ledger(self):
        for i in self.items:
            programme = frappe.get_value("Student", {"name": i.student}, "programme")
            
            # Prepare ledger data
            ledger_data = {
                "doctype": "Assessment Ledger",
                "student": i.student,
                "posting_date": self.posting_date,
                "student_name": i.student_name,
                "academic_year": self.academic_year,
                "academic_term": self.academic_term,
                "marks_obtained": i.marks_obtained,
                "semester": self.semester,
                "passing_marks": self.passing_marks,
                "total_marks": self.total_marks,
                "reference_type": self.doctype,
                "reference_name": self.name,
                "has_reassessment": 0,
                "college": self.college,
                "programme": programme,
                "module": self.module,
                "assessment_component": self.assessment_component,
                "assessment_weightage": self.weightage,
                "weightage_achieved": i.weightage_achieved,
                "tutor": self.tutor,
                "tutor_name": self.tutor_name
            }
            
            doc = frappe.get_doc(ledger_data)

            doc.insert(ignore_permissions=True)

            doc.submit()

        frappe.msgprint(f"Assessment Ledger created and submitted for {self.module} - {self.assessment_component}")
        
@frappe.whitelist()
def get_students(examination_registration=None, doc=None):
    doc = json.loads(doc)
    
    if doc['exam_type'] == 'Regular Assessment':
        if not doc.get('module'):
            frappe.throw("Please select Module")
        if not doc.get('tutor'):
            frappe.throw("Please select Tutor")
        if not doc.get('academic_term'):
            frappe.throw("Please select Academic Term")
        if not doc.get('college'):
            frappe.throw("Please select College")
        if not doc.get('semester'):
            frappe.throw("Please select Semester")
            
        data = frappe.db.sql(
            """
           SELECT DISTINCT 
            me.student,
            me.student_name
            FROM `tabModule Enrolment` me
            INNER JOIN `tabModule Enrolment Tutor` met 
            ON met.parent = me.name
            WHERE me.course = %s
            AND met.tutor = %s
            AND me.academic_term = %s
            AND me.college = %s
            AND me.semester = %s
            AND me.docstatus = 1
            """,
            (doc["module"], doc["tutor"], doc["academic_term"], doc["college"], doc["semester"]),
            as_dict=True
        )
        
    elif doc['exam_type'] in ('Exam Recheck', 'Exam Re-Evaluation', 'Exam Re-Assessment'):
        if not doc.get('module'):
            frappe.throw("Please select Module")
        if not doc.get('tutor'):
            frappe.throw("Please select Tutor")
        if not doc.get('academic_term'):
            frappe.throw("Please select Academic Term")
        if not doc.get('college'):
            frappe.throw("Please select College")
        if not doc.get('semester'):
            frappe.throw("Please select Semester")
        if not doc.get('assessment_component'):
            frappe.throw("Please select Assessment Component")
        
        data = frappe.db.sql(
            """
            SELECT DISTINCT 
                era.student,
                era.student_name,
                era.programme
            FROM 
                `tabExamination Review Application` era
            INNER JOIN `tabModule Enrolment` me 
                ON me.student = era.student
                AND me.course = era.module
                AND me.academic_term = era.academic_term
                AND me.college = era.college
                AND me.semester = era.semester
                AND me.docstatus = 1
            INNER JOIN `tabModule Enrolment Tutor` met 
                ON met.parent = me.name
                AND met.tutor = %(tutor)s
            WHERE era.academic_term = %(academic_term)s
                AND era.module = %(module)s
                AND era.college = %(college)s
                AND era.semester = %(semester)s
                AND era.assessment_component = %(assessment_component)s
                AND era.exam_review_type = %(exam_type)s
                AND era.docstatus = 1
            """,
            {
                "academic_term": doc["academic_term"],
                "module": doc["module"],
                "college": doc["college"],
                "semester": doc["semester"],
                "tutor": doc["tutor"],
                "assessment_component": doc["assessment_component"],
                "exam_type": doc["exam_type"]
            },
            as_dict=True
        )
    
    if not data:
        frappe.msgprint("No students found for the selected criteria")
        return []
    
  
    ineligible_students_query = """
        SELECT DISTINCT 
            ies.student,
            ies.consider_attendance,
            ins.module,
            ins.assessment_component
        FROM `tabIneligible Student` ins
        INNER JOIN `tabNon Eligible Exam Students` ies 
            ON ies.parent = ins.name
        WHERE ins.docstatus = 1
    """
    
    where_conditions = []
    params = []
    
    if doc.get('college'):
        where_conditions.append("ins.company = %s")
        params.append(doc.get('college'))
    if doc.get('academic_year'):
        where_conditions.append("ins.academic_year = %s")
        params.append(doc.get('academic_year'))
    if doc.get('academic_term'):
        where_conditions.append("ins.academic_term = %s")
        params.append(doc.get('academic_term'))
    if doc.get('semester'):
        where_conditions.append("ins.semester = %s")
        params.append(doc.get('semester'))
    
   
    
    module_condition = ""
    assessment_condition = ""
    
    if doc.get('module'):
        module_condition = """ AND (ins.module = %s OR ins.module IS NULL) """
        params.append(doc.get('module'))
    
    if doc.get('assessment_component'):
        assessment_condition = """ AND (ins.assessment_component = %s OR ins.assessment_component IS NULL) """
        params.append(doc.get('assessment_component'))
    
    if where_conditions:
        ineligible_students_query += " AND " + " AND ".join(where_conditions)
    
    if module_condition:
        ineligible_students_query += module_condition
    
    if assessment_condition:
        ineligible_students_query += assessment_condition
    
    ineligible_records = frappe.db.sql(ineligible_students_query, tuple(params), as_dict=True)
    
   
    completely_ineligible_set = set()
    ineligible_details = []
    
    for record in ineligible_records:
        student_id = record.get('student')
        if student_id:
            applies = True
            
            if doc.get('module') and record.get('module') is not None:
                if record.get('module') != doc.get('module'):
                    applies = False
            
            if applies and doc.get('assessment_component') and record.get('assessment_component') is not None:
                if record.get('assessment_component') != doc.get('assessment_component'):
                    applies = False
            
            if applies and record.get('consider_attendance') == 0:
                completely_ineligible_set.add(student_id)
                ineligible_details.append({
                    "student": student_id,
                    "reason": record.get('reason', 'Marked as ineligible'),
                    "module": record.get('module'),
                    "assessment_component": record.get('assessment_component')
                })
    
    eligible_data = []
    ineligible_filtered_out = []
    
    for student in data:
        student_id = student.get('student')
        
        if student_id in completely_ineligible_set:
            ineligible_filtered_out.append({
                "student": student_id,
                "student_name": student.get('student_name', ''),
                "programme": student.get('programme'),
                "reason": next((d['reason'] for d in ineligible_details if d['student'] == student_id), 'Marked as ineligible')
            })
        else:
            eligible_data.append(student)
    
    for i in eligible_data:
        if not i.get('programme'):
            programme = frappe.get_value('Student', {"name": i.student}, 'programme')
            if not programme:
                frappe.throw("Set programme for student {} in Student".format(i.student))
            i["programme"] = programme
        else:
            i["programme"] = i.get('programme')
    
    if ineligible_filtered_out:
        frappe.local.ineligible_students = ineligible_filtered_out
        
        ineligible_names = ", ".join([f"{s['student']} - {s['student_name']}" for s in ineligible_filtered_out[:5]])
        if len(ineligible_filtered_out) > 5:
            ineligible_names += f" and {len(ineligible_filtered_out) - 5} more"
        
        frappe.msgprint(
            title="Ineligible Students Filtered Out",
            msg=f"Student {ineligible_names} is being Excluded from the Exam Mark Entry.",
            indicator="orange"
        )
    
    return eligible_data
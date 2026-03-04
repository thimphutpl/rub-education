# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class ExaminationMarksEntry(Document):
    def validate(self):
        # self.fetch_weightage()
        self.check_assesment_component()
        self.fetch_exam_registration()
        self.check_duplicate_ass_component()
        self.check_duplicate_marks_entry()
        self.calculate_weightageAchieved()

    def on_submit(self):
        self.check_earlier_assesment()
        self.create_assessment_ledger()

    def on_cancel(self):
        self.ignore_linked_doctypes = (
            "Assessment Ledger",
        )

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
        # Get assessment component to check role
        assessment_component_settings = frappe.db.get_value(
            "Assessment Component",
            self.assessment_component,
            "assessment_role",
            as_dict=True
        )
        
        assessment_role = assessment_component_settings.get("assessment_role", "Tutor") if assessment_component_settings else "Tutor"
        
        if self.exam_type in ('Regular Assessment','Exam Re-Assessment','Exam Recheck','Exam Re-Evaluation'):
            if self.exam_type=='Regular Assessment':
                if assessment_role == "Exam Cell":
                    exam_registration = frappe.db.sql("""
                        SELECT name 
                        FROM `tabExamination Registration`
                        WHERE module = %s
                        AND semester = %s
                        AND academic_term = %s
                        AND company = %s
                        AND docstatus = 1  
                        AND assessment_component = %s
                        AND reassesment=0
                    """, 
                    (self.module, self.semester, self.academic_term, self.college, self.assessment_component),
                    as_dict=True)
                else:
                    exam_registration = frappe.db.sql("""
                        SELECT name 
                        FROM `tabExamination Registration`
                        WHERE module = %s
                        AND semester = %s
                        AND academic_term = %s
                        AND company = %s
                        AND docstatus = 1  
                        AND assessment_component = %s
                        AND tutor = %s
                        AND reassesment=0
                    """, 
                    (self.module, self.semester, self.academic_term, self.college, self.assessment_component, self.tutor),
                    as_dict=True)
                    
            elif self.exam_type=='Exam Re-Assessment':
                if assessment_role == "Exam Cell":
                    exam_registration = frappe.db.sql("""
                        SELECT name 
                        FROM `tabExamination Registration`
                        WHERE module = %s
                        AND semester = %s
                        AND academic_term = %s
                        AND company = %s
                        AND docstatus = 1  
                        AND assessment_component = %s
                        AND reassesment=1 
                        order by posting_date DESC limit 1
                    """, 
                    (self.module, self.semester, self.academic_term, self.college, self.assessment_component),
                    as_dict=True)
                else:
                    exam_registration = frappe.db.sql("""
                        SELECT name 
                        FROM `tabExamination Registration`
                        WHERE module = %s
                        AND semester = %s
                        AND academic_term = %s
                        AND docstatus = 1  
                        AND company = %s
                        AND assessment_component = %s
                        AND tutor = %s
                        AND reassesment=1 
                        order by posting_date DESC limit 1
                    """, 
                    (self.module, self.semester, self.academic_term, self.college, self.assessment_component, self.tutor),
                    as_dict=True)
            else:
                if assessment_role == "Exam Cell":
                    exam_registration = frappe.db.sql("""
                        SELECT name 
                        FROM `tabExamination Registration`
                        WHERE module = %s
                        AND semester = %s
                        AND docstatus = 1  
                        AND academic_term = %s
                        AND company = %s
                        AND assessment_component = %s
                        order by posting_date DESC limit 1
                    """, 
                    (self.module, self.semester, self.academic_term, self.college, self.assessment_component),
                    as_dict=True)
                else:
                    exam_registration = frappe.db.sql("""
                        SELECT name 
                        FROM `tabExamination Registration`
                        WHERE module = %s
                        AND semester = %s
                        AND docstatus = 1  
                        AND academic_term = %s
                        AND company = %s
                        AND assessment_component = %s
                        AND tutor = %s
                        order by posting_date DESC limit 1
                    """, 
                    (self.module, self.semester, self.academic_term, self.college, self.assessment_component, self.tutor),
                    as_dict=True)

            if exam_registration:
                self.examination_registration = exam_registration[0].get('name')
            else:
                frappe.throw("Examination Registration not found for {}".format(self.assessment_component))
                
    def check_duplicate_marks_entry(self):
        # Get assessment component to check role
        assessment_component_settings = frappe.db.get_value(
            "Assessment Component",
            self.assessment_component,
            "assessment_role",
            as_dict=True
        )
        
        assessment_role = assessment_component_settings.get("assessment_role", "Tutor") if assessment_component_settings else "Tutor"
        
        if assessment_role == "Exam Cell":
            duplicate = frappe.db.exists("Examination Marks Entry",{
                "exam_type":self.exam_type,
                "examination_registration":self.examination_registration,
                "academic_term":self.academic_term,
                "docstatus":1
            })
        else:
            duplicate = frappe.db.exists("Examination Marks Entry",{
                "exam_type":self.exam_type,
                "examination_registration":self.examination_registration,
                "academic_term":self.academic_term,
                "tutor":self.tutor,
                "docstatus":1
            })
    
        if duplicate:
            frappe.throw("The Marks entry done already for examination {}".format(self.examination_registration))
            
    def check_assesment_component(self):
        ass_com = frappe.db.exists("Module Assessment Item",{"parent":self.module,"assessment_name":self.assessment_component})
    
        if not ass_com:
            frappe.throw("The component {} dont exist for module {}".format(self.assessment_component,self.module))
            
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
            if not (i.marks_verified and self.total_marks):
                continue

            condition = ""
            if self.tutor:
                condition = f" AND mac.tutor = '{self.tutor}'"

            query = f"""
                SELECT mai.weightage
                FROM `tabModule Assessment Item` mai
                INNER JOIN `tabModule Assessment Criteria` mac 
                    ON mai.parent = mac.name
                WHERE mac.college = '{self.college}'
                AND mac.academic_term = '{self.academic_term}'
                AND mac.programme = '{i.programme}'
                AND mac.module = '{self.module}'
                AND mai.assessment_name = '{self.assessment_component}'
                {condition}
            """

            # frappe.throw(str(query))

            result = frappe.db.sql(query)

            if not result:
                frappe.throw("Weightage not defined for this configuration")

            weightage = result[0][0] or 0

            i.weightage = weightage
            i.weightage_achieved = (
                (i.marks_verified / self.total_marks) * weightage
            )

    # def calculate_weightageAchieved(self):
    #     for i in self.items:
    #         if i.marks_verified and self.total_marks:
    #             # i.weightage= frappe.get_value("Module Assessment Item",{"assessment_name":self.assessment_component,"college":self.college,""},"weightage")
    #             condition = ''
    #             if self.tutor:
    #                 condition = ' and tutor= {}'.format(self.tutor)
    #             i.weightage = frappe.db.sql('''
    #                 select mac.module,mai.weightage from 
    #                 `tabModule Assessment Item` mai inner join 
    #                 `tabModule Assessment Criteria` mac on mai.parent=mac.name 
    #                 and mac.college='{}' 
    #                 and mac.academic_term='{}' 
    #                 and mac.programme='{}' 
    #                 and module='{}'  
    #                 and mai.assessment_name='Semester Exam'

    #                 {}

    #             '''.format(self.college,self.academic_term,self.programme,self.module,condition))
    #             i.weightage_achieved = float(float(i.marks_verified/self.total_marks)*i.weightage)

    def fetch_weightage(self):
        if self.assessment_component:
            weightage= frappe.get_value("Module Assessment Item",{"assessment_name":self.assessment_component,"parent":self.module},"weightage")
    
        self.weightage = weightage
        
    def create_assessment_ledger(self):
        # Get assessment component to check role
        assessment_component_settings = frappe.db.get_value(
            "Assessment Component",
            self.assessment_component,
            "assessment_role",
            as_dict=True
        )
        
        assessment_role = assessment_component_settings.get("assessment_role", "Tutor") if assessment_component_settings else "Tutor"
        
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
                "marks_obtained": i.marks_verified,
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
            }
            
            # Set tutor fields based on assessment role
            if assessment_role == "Exam Cell":
                # Set tutor fields as empty/None for Exam Cell
                ledger_data["tutor"] = None
                ledger_data["tutor_name"] = None
            else:
                # Set tutor fields from the document for regular tutors
                ledger_data["tutor"] = self.tutor
                ledger_data["tutor_name"] = self.tutor_name
            
            # Create the document
            doc = frappe.get_doc(ledger_data)

            # Insert into database
            doc.insert(ignore_permissions=True)

            # Optionally submit if needed
            doc.submit()

        frappe.msgprint(f"Assessment Ledger created and submitted for {self.examination_registration}")

@frappe.whitelist()
def get_students(examination_registration=None, doc=None):
    # Step 1: Get students enrolled in the given term & module
    doc = json.loads(doc)
    
    if not examination_registration:
        frappe.throw("Please Add Examination Registration")

    # Get assessment component to check role
    assessment_component_settings = frappe.db.get_value(
        "Assessment Component",
        doc['assessment_component'],
        "assessment_role",
        as_dict=True
    )
    
    assessment_role = assessment_component_settings.get("assessment_role", "Tutor") if assessment_component_settings else "Tutor"

    if doc['exam_type']=='Exam Recheck' or doc['exam_type']=='Exam Re-Evaluation':
        if assessment_role == "Exam Cell":
            data = frappe.db.sql(
                """
                select student, student_name, programme
                from 
                `tabExamination Review Application`
                WHERE academic_term=%s
                AND module=%s
                AND college=%s
                AND assessment_component = %s
                AND exam_review_type=%s
                AND docstatus=1
                """,
                (doc["academic_term"], doc["module"], doc["college"], doc["assessment_component"], doc["exam_type"]),
                as_dict=True
            )
        else:
            data = frappe.db.sql(
                """
                select student, student_name, programme
                from 
                `tabExamination Review Application`
                WHERE academic_term=%s
                AND module=%s
                AND college=%s
                AND tutor=%s
                AND assessment_component = %s
                AND exam_review_type=%s
                AND docstatus=1
                """,
                (doc["academic_term"], doc["module"], doc["college"], doc["tutor"], doc["assessment_component"], doc["exam_type"]),
                as_dict=True
            )
    else:
        data = frappe.db.sql(
            """
            select student, student_name
            from `tabExam Students` where parent=%s

            union

            select student, student_name from `tabNon Eligible Exam Students` 
            where consider_attendance=1 and parent=%s;
            """,
            (examination_registration, examination_registration),
            as_dict=True
        )
    
    for i in data:
        programme = frappe.get_value('Student',{"name":i.student},'programme')
        if not programme:
            frappe.throw("Set programme for student {} in Student".format(i.student))
        i["programme"] = programme

    return data
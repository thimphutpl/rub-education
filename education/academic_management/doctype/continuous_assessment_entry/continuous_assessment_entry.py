# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ContinuousAssessmentEntry(Document):
    def validate(self):
        self.fetch_weightage()
        self.check_assesment_component()
        self.check_duplicate_marks_entry()
        self.calculate_weightage_achieved()
        self.validate_marks_obtained()

    def on_submit(self):
        self.create_assessment_ledger()

    def on_cancel(self):
        self.ignore_linked_doctypes = ("Assessment Ledger",)
        self.cancel_assessment_entry()

    def validate_marks_obtained(self):
        for item in self.items:
            if (item.marks_obtained or 0) > (self.total_marks or 0):
                frappe.throw(
                    f"Row {item.idx}: Marks Obtained cannot be greater than "
                    f"Total Marks ({self.total_marks})."
                )

    def cancel_assessment_entry(self):
        assessment_ledgers = frappe.get_all(
            "Assessment Ledger",
            filters={"reference_name": self.name},
            pluck="name",
        )
        for ledger in assessment_ledgers:
            frappe.db.sql(
                """
                UPDATE `tabAssessment Ledger`
                SET is_cancelled = 1
                WHERE name = %s
                """,
                (ledger,),
            )

    def fetch_exam_registration(self):
        if self.exam_type not in ("Semester End Examination", "Exam Re-Assessment"):
            return

        params = (
            self.module,
            self.semester,
            self.academic_term,
            self.college,
            self.assessment_component,
            self.tutor,
        )

        if self.exam_type == "Semester End Examination":
            query = """
                SELECT name
                FROM `tabExamination Registration`
                WHERE module = %s
                  AND semester = %s
                  AND academic_term = %s
                  AND company = %s
                  AND assessment_component = %s
                  AND tutor = %s
                  AND reassesment = 0
            """
        else:  # Exam Re-Assessment
            query = """
                SELECT name
                FROM `tabExamination Registration`
                WHERE module = %s
                  AND semester = %s
                  AND academic_term = %s
                  AND company = %s
                  AND assessment_component = %s
                  AND tutor = %s
                  AND reassesment = 1
                ORDER BY posting_date DESC
                LIMIT 1
            """

        exam_registration = frappe.db.sql(query, params, as_dict=True)

        if exam_registration:
            self.examination_registration = exam_registration[0].get("name")
        else:
            frappe.throw(
                f"Examination Registration not found for {self.assessment_component}"
            )

    def check_duplicate_marks_entry(self):
        if not self.module_enrolment_key:
            return

        exclude = [self.name]
        if self.amended_from:
            exclude.append(self.amended_from)

        duplicate = frappe.db.get_value(
            "Continuous Assessment Entry",
            {
                "module_enrolment_key": self.module_enrolment_key,
                "assessment_component": self.assessment_component,
                "tutor": self.tutor,
                "exam_type": self.exam_type,
                "docstatus": ["!=", 2],
                "name": ["not in", exclude],
            },
            "name",
        )

        if duplicate:
            frappe.throw(
                f"CA Entry <b>{duplicate}</b> already exists for "
                f"{self.assessment_component} ({self.exam_type}) "
                f"under this Module Enrolment Key."
            )

    def check_assesment_component(self):
        ass_com = frappe.db.sql(
            """
            SELECT 1
            FROM `tabModule Assessment Item` mai
            INNER JOIN `tabModule Assessment Criteria` mac
                ON mai.parent = mac.name
            WHERE mac.module = %s
              AND mai.assessment_name = %s
              AND mac.academic_term = %s
              AND mac.college = %s
            """,
            (
                self.module,
                self.assessment_component,
                self.academic_term,
                self.college,
            ),
        )

        if not ass_com:
            frappe.throw(
                f"The component {self.assessment_component} "
                f"does not exist for module {self.module}"
            )

    def calculate_weightage_achieved(self):
        for item in self.items:
            if not (item.marks_obtained and self.total_marks):
                continue

            result = frappe.db.sql(
                """
                SELECT mai.weightage
                FROM `tabModule Assessment Item` mai
                INNER JOIN `tabModule Assessment Criteria` mac
                    ON mai.parent = mac.name
                WHERE mac.college = %s
                  AND mac.academic_term = %s
                  AND mac.programme = %s
                  AND mac.module = %s
                  AND mai.assessment_name = %s
                """,
                (
                    self.college,
                    self.academic_term,
                    self.programme,
                    self.module,
                    self.assessment_component,
                ),
            )

            if not result:
                frappe.throw("Weightage not defined for this configuration")

            weightage = result[0][0] or 0
            item.weightage = weightage
            item.weightage_achieved = (
                (item.marks_obtained / self.total_marks) * weightage
            )

    def fetch_weightage(self):
        weightage = frappe.db.sql(
            """
            SELECT mai.weightage
            FROM `tabModule Assessment Item` mai
            INNER JOIN `tabModule Assessment Criteria` mac
                ON mai.parent = mac.name
            WHERE mac.college = %s
              AND mac.academic_term = %s
              AND mac.programme = %s
              AND mac.module = %s
              AND mai.assessment_name = %s
            """,
            (
                self.college,
                self.academic_term,
                self.programme,
                self.module,
                self.assessment_component,
            ),
            as_dict=1,
        )

        if len(weightage) > 0:
            self.weightage = weightage[0].weightage

    def create_assessment_ledger(self):
        for item in self.items:
            doc = frappe.get_doc(
                {
                    "doctype": "Assessment Ledger",
                    "student": item.student,
                    "posting_date": self.posting_date,
                    "student_name": item.student_name,
                    "academic_year": self.academic_year,
                    "academic_term": self.academic_term,
                    "marks_obtained": item.marks_obtained,
                    "semester": self.semester,
                    "passing_marks": self.passing_marks,
                    "total_marks": self.total_marks,
                    "reference_type": self.doctype,
                    "reference_name": self.name,
                    "has_reassessment": 0,
                    "college": self.college,
                    "programme": self.programme,
                    "module": self.module,
                    "assessment_component": self.assessment_component,
                    "tutor": self.tutor,
                    "tutor_name": self.tutor_name,
                    "assessment_weightage": self.weightage,
                    "weightage_achieved": item.weightage_achieved,
                }
            )
            doc.insert(ignore_permissions=True)
            doc.submit()

        frappe.msgprint(
            f"Assessment Ledger created and submitted for {self.assessment_component}"
        )


@frappe.whitelist()
def get_students(doc, module_enrolment_key):
    if not module_enrolment_key:
        frappe.throw("Please select Module Enrolment Key")

    data = frappe.db.sql(
        """
        SELECT DISTINCT student, student_name
        FROM `tabModule Enrolment`
        WHERE module_enrollment_key = %s
          AND docstatus = 1
        ORDER BY student_name ASC
        """,
        (module_enrolment_key,),
        as_dict=True,
    )

    return data
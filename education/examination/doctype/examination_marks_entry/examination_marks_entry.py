# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ExaminationMarksEntry(Document):
    def validate(self):
        self.set_from_module_enrolment_key()
        self.fetch_weightage()
        self.calculate_weightage_achieved()
        self.validate_marks()

    # ------------------------------------------------------------------
    # Backfill fields from Module Enrolment Key
    # NOTE: 'semester' is NOT on Module Enrolment Key → excluded here.
    # ------------------------------------------------------------------
    def set_from_module_enrolment_key(self):
        if not self.module_enrolment_key:
            return

        candidate_fields = [
            "college",
            "tutor",
            "programme",
            "academic_year",
            "academic_term",
            "module",
            # "semester" — intentionally omitted (not on MEK)
        ]

        mek_meta = frappe.get_meta("Module Enrolment Key")
        existing_fields = [
            f for f in candidate_fields if mek_meta.has_field(f)
        ]

        if not existing_fields:
            return

        mek = frappe.db.get_value(
            "Module Enrolment Key",
            self.module_enrolment_key,
            existing_fields,
            as_dict=True,
        )

        if not mek:
            frappe.throw(
                f"Module Enrolment Key <b>{self.module_enrolment_key}</b> not found."
            )

        for field in existing_fields:
            if not self.get(field) and mek.get(field):
                self.set(field, mek.get(field))

        if self.tutor and not self.tutor_name:
            self.tutor_name = frappe.db.get_value(
                "Employee", self.tutor, "employee_name"
            )

    # ------------------------------------------------------------------
    # Weightage lookup — identical to CA Entry.fetch_weightage
    # ------------------------------------------------------------------
    def fetch_weightage(self):
        if not (
            self.college
            and self.academic_term
            and self.programme
            and self.module
            and self.assessment_component
        ):
            return

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

    # ------------------------------------------------------------------
    # Per-row weightage_achieved — identical to CA Entry
    # ------------------------------------------------------------------
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
                frappe.throw(
                    "Weightage not defined for this configuration"
                )

            weightage = result[0][0] or 0
            item.weightage = weightage
            item.weightage_achieved = (
                (item.marks_obtained / self.total_marks) * weightage
            )

    # ------------------------------------------------------------------
    # Marks validation
    # ------------------------------------------------------------------
    def validate_marks(self):
        for item in self.items:
            if (item.marks_obtained or 0) > (self.total_marks or 0):
                frappe.throw(
                    f"Row {item.idx}: Marks Obtained cannot be greater than "
                    f"Total Marks ({self.total_marks})."
                )


# ----------------------------------------------------------------------
# Whitelisted: fetch students alphabetically
# ----------------------------------------------------------------------
@frappe.whitelist()
def get_students(doc, examination_registration=None):
    """Fetch students alphabetically for the given criteria."""
    if isinstance(doc, str):
        doc = json.loads(doc)

    exam_type = doc.get("exam_type")

    # Re-Assessment / Recheck / Re-Evaluation → use examination_registration
    if exam_type and exam_type != "Semester End Examination":
        if not examination_registration:
            frappe.throw(
                f"Examination Registration is required for {exam_type}."
            )

        data = frappe.db.sql(
            """
            SELECT DISTINCT
                er.student,
                er.student_name,
                er.programme,
                er.name AS review_name
            FROM `tabExamination Registration` er
            WHERE er.name = %s
              AND er.docstatus = 1
            ORDER BY er.student_name ASC
            """,
            (examination_registration,),
            as_dict=True,
        )
        return data

    # Semester End Examination → use Module Enrolment Key
    module_enrolment_key = doc.get("module_enrolment_key")
    if not module_enrolment_key:
        frappe.throw("Please select Module Enrolment Key.")

    data = frappe.db.sql(
        """
        SELECT DISTINCT
            me.student,
            me.student_name
        FROM `tabModule Enrolment` me
        WHERE me.module_enrollment_key = %s
          AND me.docstatus = 1
        ORDER BY me.student_name ASC
        """,
        (module_enrolment_key,),
        as_dict=True,
    )

    for row in data:
        row["programme"] = doc.get("programme")

    return data


# ----------------------------------------------------------------------
# Whitelisted: fetch weightage for live UI refresh
# ----------------------------------------------------------------------
@frappe.whitelist()
def get_weightage(college, academic_term, programme, module, assessment_component):
    """Return weightage for the given assessment configuration, or None."""
    rows = frappe.db.sql(
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
        (college, academic_term, programme, module, assessment_component),
        as_dict=True,
    )
    if rows and rows[0].get("weightage") is not None:
        return rows[0]["weightage"]
    return None
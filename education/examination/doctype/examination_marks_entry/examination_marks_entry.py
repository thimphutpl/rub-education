# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ExaminationMarksEntry(Document):
    def validate(self):
        self.check_duplicate_marks_entry()
        self.calculate_weightage_achieved()

    def on_submit(self):
        self.check_earlier_assessment()
        self.create_assessment_ledger()

    def on_cancel(self):
        self.ignore_linked_doctypes = ("Assessment Ledger",)
        self.cancel_assessment_entry()

    # ------------------------------------------------------------------ #
    #  Validation helpers
    # ------------------------------------------------------------------ #
    def check_duplicate_marks_entry(self):
        if frappe.db.exists(
            "Examination Marks Entry",
            {
                "exam_type": self.exam_type,
                "academic_term": self.academic_term,
                "programme": self.programme,
                "module": self.module,
                "assessment_component": self.assessment_component,
                "docstatus": 1,
                "name": ("!=", self.name),
            },
        ):
            frappe.throw(
                f"The marks entry for <b>{self.assessment_component}</b> "
                "has already been completed."
            )

    def calculate_weightage_achieved(self):
        if not self.items:
            return

        # Fetch weightage once (same for every row) instead of per-row
        weightage = frappe.db.sql(
            """
            SELECT mai.weightage
            FROM `tabModule Assessment Item` mai
            INNER JOIN `tabModule Assessment Criteria` mac
                ON mai.parent = mac.name
            WHERE mac.college = %s
              AND mac.academic_term = %s
              AND mac.programme = %s
              AND mai.assessment_name = %s
            LIMIT 1
            """,
            (self.college, self.academic_term, self.programme,
             self.assessment_component),
            as_dict=False,
        )

        if not weightage:
            frappe.throw("Weightage not defined for this configuration")

        weightage = weightage[0][0] or 0

        for row in self.items:
            row.weightage = weightage
            if row.marks_obtained and self.total_marks:
                row.weightage_achieved = (
                    (row.marks_obtained / self.total_marks) * weightage
                )
            else:
                row.weightage_achieved = 0

    # ------------------------------------------------------------------ #
    #  Submit / Cancel
    # ------------------------------------------------------------------ #
    def check_earlier_assessment(self):
        """Flag prior non-reassessment ledger rows as having a reassessment."""
        for row in self.items:
            ledger = frappe.db.get_value(
                "Assessment Ledger",
                {
                    "student": row.student,
                    "assessment_component": self.assessment_component,
                    "module": self.module,
                    "has_reassessment": 0,
                },
                "name",
            )
            if ledger:
                frappe.db.set_value(
                    "Assessment Ledger", ledger, "has_reassessment", 1,
                    update_modified=False,
                )

    def create_assessment_ledger(self):
        if not self.items:
            return

        # Pre-fetch all programmes in one query
        student_ids = [row.student for row in self.items if row.student]
        programme_map = {}
        if student_ids:
            for rec in frappe.get_all(
                "Student",
                filters={"name": ("in", student_ids)},
                fields=["name", "programme"],
            ):
                programme_map[rec.name] = rec.programme

        for row in self.items:
            ledger_data = {
                "doctype": "Assessment Ledger",
                "student": row.student,
                "posting_date": self.posting_date,
                "student_name": row.student_name,
                "academic_year": self.academic_year,
                "academic_term": self.academic_term,
                "marks_obtained": row.marks_obtained,
                "semester": self.semester,
                "passing_marks": self.passing_marks,
                "total_marks": self.total_marks,
                "reference_type": self.doctype,
                "reference_name": self.name,
                "has_reassessment": 0,
                "college": self.college,
                "programme": programme_map.get(row.student),
                "module": self.module,
                "assessment_component": self.assessment_component,
                "assessment_weightage": row.weightage,
                "weightage_achieved": row.weightage_achieved,
                "tutor": self.tutor,
                "tutor_name": self.tutor_name,
            }
            doc = frappe.get_doc(ledger_data)
            doc.insert(ignore_permissions=True)
            doc.submit()

            if row.get("examination_review_link"):
                frappe.db.set_value(
                    "Examination Review Application",
                    row.examination_review_link,
                    "marks_awarded",
                    1,
                )

        frappe.msgprint(
            f"Assessment Ledger created and submitted for "
            f"{self.module} - {self.assessment_component}"
        )

    def cancel_assessment_entry(self):
        ledger_names = frappe.get_all(
            "Assessment Ledger",
            filters={"reference_name": self.name},
            pluck="name",
        )
        if not ledger_names:
            return

        frappe.db.set_value(
            "Assessment Ledger",
            {"name": ("in", ledger_names)},
            "is_cancelled",
            1,
            update_modified=False,
        )


# ---------------------------------------------------------------------- #
#  Whitelisted API
# ---------------------------------------------------------------------- #
REQUIRED_FIELDS = {
    "Semester End Examination": (
        "module", "tutor", "academic_term", "college", "semester",
        "module_enrolment_key",
    ),
    "Exam Recheck": (
        "module", "tutor", "academic_term", "college", "semester",
        "assessment_component",
    ),
    "Exam Re-Evaluation": (
        "module", "tutor", "academic_term", "college", "semester",
        "assessment_component",
    ),
    "Exam Re-Assessment": (
        "module", "tutor", "academic_term", "college", "semester",
        "assessment_component",
    ),
}


@frappe.whitelist()
def get_students(examination_registration=None, doc=None):
    doc = json.loads(doc) if isinstance(doc, str) else (doc or {})
    exam_type = doc.get("exam_type")

    if exam_type not in REQUIRED_FIELDS:
        frappe.throw(
            f"Unsupported exam type: {exam_type!r}. "
            "Please select a valid Exam Type before fetching students."
        )

    for field in REQUIRED_FIELDS[exam_type]:
        if not doc.get(field):
            frappe.throw(f"Please select {field.replace('_', ' ').title()}")

    if exam_type == "Semester End Examination":
        data = _fetch_semester_end_students(doc)
    else:
        data = _fetch_review_students(doc)

    if not data:
        frappe.msgprint("No students found for the selected criteria")
        return []

    eligible_data = _filter_ineligible_students(doc, data)

    # ✅ Alphabetical sort by student name (case-insensitive)
    eligible_data.sort(key=lambda x: (x.get("student_name") or "").lower())

    # Ensure programme is populated
    for i in eligible_data:
        if not i.get("programme"):
            programme = frappe.get_value(
                "Student", {"name": i["student"]}, "programme"
            )
            if not programme:
                frappe.throw(
                    f"Set programme for student {i['student']} in Student"
                )
            i["programme"] = programme

    return eligible_data


# ---------------------------------------------------------------------- #
#  Internal helpers
# ---------------------------------------------------------------------- #
def _fetch_semester_end_students(doc):
    return frappe.db.sql(
        """
        SELECT DISTINCT me.student, me.student_name
        FROM `tabModule Enrolment` me
        INNER JOIN `tabModule Enrolment Tutor` met ON met.parent = me.name
        WHERE me.course = %s
          AND met.tutor = %s
          AND me.academic_term = %s
          AND me.college = %s
          AND me.semester = %s
          AND me.module_enrollment_key = %s
          AND me.docstatus = 1
        """,
        (
            doc["module"], doc["tutor"], doc["academic_term"],
            doc["college"], doc["semester"], doc["module_enrolment_key"],
        ),
        as_dict=True,
    )


def _fetch_review_students(doc):
    return frappe.db.sql(
        """
        SELECT DISTINCT
            era.student,
            era.student_name,
            era.programme,
            era.name AS review_name
        FROM `tabExamination Review Application` era
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
            "exam_type": doc["exam_type"],
        },
        as_dict=True,
    )


def _filter_ineligible_students(doc, data):
    """Remove students that are marked as ineligible for the given context."""
    query = """
        SELECT DISTINCT
            ies.student,
            ies.consider_attendance,
            ins.module,
            ins.assessment_component
        FROM `tabIneligible Student` ins
        INNER JOIN `tabNon Eligible Exam Students` ies ON ies.parent = ins.name
        WHERE ins.docstatus = 1
    """
    conditions, params = [], []

    for field, column in (
        ("college", "ins.company"),
        ("academic_year", "ins.academic_year"),
        ("academic_term", "ins.academic_term"),
        ("semester", "ins.semester"),
    ):
        if doc.get(field):
            conditions.append(f"{column} = %s")
            params.append(doc[field])

    if doc.get("module"):
        conditions.append("(ins.module = %s OR ins.module IS NULL)")
        params.append(doc["module"])

    if doc.get("assessment_component"):
        conditions.append(
            "(ins.assessment_component = %s OR ins.assessment_component IS NULL)"
        )
        params.append(doc["assessment_component"])

    if conditions:
        query += " AND " + " AND ".join(conditions)

    ineligible_records = frappe.db.sql(query, tuple(params), as_dict=True)

    ineligible_set = set()
    for rec in ineligible_records:
        if not rec.get("student"):
            continue
        if doc.get("module") and rec.get("module") and rec["module"] != doc["module"]:
            continue
        if (
            doc.get("assessment_component")
            and rec.get("assessment_component")
            and rec["assessment_component"] != doc["assessment_component"]
        ):
            continue
        if rec.get("consider_attendance") == 0:
            ineligible_set.add(rec["student"])

    eligible = []
    excluded = []
    for student in data:
        if student["student"] in ineligible_set:
            excluded.append(student)
        else:
            eligible.append(student)

    if excluded:
        frappe.local.ineligible_students = excluded
        names = ", ".join(
            f"{s['student']} - {s.get('student_name', '')}" for s in excluded[:5]
        )
        if len(excluded) > 5:
            names += f" and {len(excluded) - 5} more"
        frappe.msgprint(
            title="Ineligible Students Filtered Out",
            msg=f"Student {names} is being Excluded from the Exam Mark Entry.",
            indicator="orange",
        )

    return eligible
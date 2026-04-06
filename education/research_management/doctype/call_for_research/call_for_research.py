# Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class CallforResearch(Document):
    def on_submit(self):
        self.send_research_email()

    def send_research_email(self):
        emails = []

        # STUDENT EMAILS
        if self.research_call_for == "Student":
            students = frappe.get_all(
                "Student",
                filters={"student_email_id": ["!=", ""]},
                fields=["student_email_id"]
            )
            emails = [s.student_email_id for s in students if s.student_email_id]

        # EMPLOYEE (FACULTY) EMAILS
        elif self.research_call_for == "Faculty":
            employees = frappe.get_all(
                "Employee",
                filters={"company_email": ["!=", ""]},
                fields=["company_email"]
            )
            emails = [e.company_email for e in employees if e.company_email]

        # No recipients
        if not emails:
            frappe.msgprint("No email recipients found.")
            return

        # Remove duplicates
        emails = list(set(emails))

        # Email Subject
        subject = f"New Research Call: {self.topic_of_the_research_call}"

        # Email Message (HTML)
        message = f"""
        <p>Dear {'Student' if self.research_call_for == 'Student' else 'Faculty'},</p>

        <p>A new research opportunity is available:</p>

        <b>Topic:</b> {self.topic_of_the_research_call} <br>
        <b>Grant Type:</b> {self.grant_type} <br>
        <b>Research Type:</b> {self.research_type} <br>
        <b>Grant Amount:</b> {self.grant_amount} <br>
        <b>Deadline:</b> {self.deadline_for_submission} <br>
        <b>Organization:</b> {self.organization} <br>

        <p>Please apply before the deadline.</p>

        <p>Regards,<br>Research Center</p>
        """

        # BULK EMAIL SEND (FAST)
        frappe.sendmail(
            recipients=emails,
            subject=subject,
            message=message
        )


@frappe.whitelist()
def make_research_proposal(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.call_for_research = source.name

    return get_mapped_doc(
        "Call for Research",
        source_name,
        {
            "Call for Research": {  
                "doctype": "Research Proposal",
                "field_map": {
                    "grant_amount": "grant_amount",
                    "topic_of_the_research_call": "topic_of_the_research_call",
                    "grant_type": "grant_type",
                    "research_type":"research_type"
                },
            }
        },
        target_doc,
        set_missing_values,
    )

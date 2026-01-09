# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class ResearchProject(Document):

    def before_save(self):
        self.validate_research_milestone_progress()
        
    def before_submit(self):
        """
        Ensure total approved milestone percentage is exactly 100%
        and all approved milestones have a linked reference_payment_entry.
        """
        approved_milestones = [c for c in self.table_bzbl if c.status == "Approved"]
        total_percentage = sum([c.milestone_percentage for c in approved_milestones])
        if total_percentage != 100:
            frappe.throw(
                f"Cannot submit. Total approved milestone percentage must be exactly 100%, "
                f"but found {total_percentage}%"
            )
        not_linked = [c.name for c in approved_milestones if not c.reference_payment_entry]
        if not_linked:
            frappe.throw(
                f"Cannot submit. The following approved milestones are missing a reference Payment Entry: "
                f"{', '.join(not_linked)}"
            )

    def validate_research_milestone_progress(self):
        """
        Calculate and validate total approved milestone progress and budget consumed
        for draft milestones that are not yet linked to any Payment Entry.
        """

        total_percentage = sum([c.milestone_percentage for c in self.table_bzbl if c.status == "Approved"])
        total_amount = sum([c.budget_amount for c in self.table_bzbl if c.status == "Approved"])

        if total_percentage > 100:
            frappe.throw("Total approved milestone percentage cannot exceed 100%")

        self.research_milestone_progress = total_percentage
        self.total_budget_consumed = total_amount
    

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
    def set_missing_values(source, target):
        
        target.payment_type = "Pay"
        if source.researcher_details and len(source.researcher_details) > 0:
            researcher = source.researcher_details[0]
            if researcher.is_student:
                target.party_type = "Student"
                target.party = researcher.student
                target.party_name = researcher.first_name
            else:
                target.party_type = "Employee"
                target.party = researcher.employee
                target.party_name = researcher.employee_name

            target.company = researcher.college
            target.call_for_research = source.name
        company_doc = frappe.get_doc("Company", target.company)

        if company_doc.receivable_accounts:
            target.paid_to = company_doc.receivable_accounts
            target.paid_to_account_currency = frappe.db.get_value(
                "Account",
                company_doc.receivable_accounts,
                "account_currency"
            )

        if company_doc.income_accounts:
            target.paid_from = company_doc.income_accounts
            target.paid_from_account_currency = frappe.db.get_value(
                "Account",
                company_doc.income_accounts,
                "account_currency"
            )

        target.research_reference = source.name
        milestone_items = frappe.get_all(
            "Research Milestone Item",
            filters={
                "parent": source.name,
                "status": "Approved",
                "reference_payment_entry": ["is", "not set"]
            },
            fields=["name", "budget_amount"]
        )

        total_budget = sum([d.budget_amount for d in milestone_items]) if milestone_items else 0
        if total_budget > 0:
            target.paid_amount = total_budget
            target.received_amount = total_budget
            target.base_paid_amount = total_budget

    return get_mapped_doc(
        "Research Project",
        source_name,
        {
            "Research Project": {
                "doctype": "Payment Entry",
                "field_map": {
                    "posting_date": "posting_date"
                },
            }
        },
        target_doc,
        set_missing_values,
    )



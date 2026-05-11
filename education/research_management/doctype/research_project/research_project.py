# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class ResearchProject(Document):

    def before_save(self):
        self.validate_research_milestone_progress()
        self.update_project_status_based_on_payments()
        
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

    def update_project_status_based_on_payments(self):
        """
        Update project status based on milestone payments.
        Status format: "milestone_percentage% Paid" (e.g., "10% Paid", "25% Paid")
        Only update if the latest payment has a reference_payment_entry.
        """
        # Get approved milestones that have reference_payment_entry
        paid_milestones = [c for c in self.table_bzbl if c.status == "Approved" and c.reference_payment_entry]
        
        # if not paid_milestones:
        #     # No payments made yet, keep default status as "Draft" or existing status
        #     if not self.status or self.status == "Draft":
        #         self.status = "Draft"
        #     return
        
        # Find the milestone with the latest reference_payment_entry (most recent payment)
        latest_milestone = None
        latest_payment_date = None
        
        for milestone in paid_milestones:
            if milestone.reference_payment_entry:
                # Get the payment entry document to check its posting date
                payment = frappe.get_doc("Payment Entry", milestone.reference_payment_entry)
                payment_date = payment.posting_date if payment else None
                
                if payment_date and (not latest_payment_date or payment_date > latest_payment_date):
                    latest_payment_date = payment_date
                    latest_milestone = milestone
        
        if latest_milestone:
            # Calculate total paid percentage including this milestone
            total_paid_percentage = sum([c.milestone_percentage for c in paid_milestones])
            
            # Set the status with the total paid percentage
            # Only use the latest milestone's percentage if we want individual milestone status
            # Or use total sum for cumulative status
            new_status = f"{int(total_paid_percentage)}% Paid"
            self.status = new_status
        # else:
        #     if not self.status or self.status == "Draft":
        #         self.status = "Draft"        

@frappe.whitelist()
def update_milestone_payment_reference(self, milestone_name, payment_entry_name):
    """Update the reference_payment_entry for a specific milestone"""
    for milestone in self.table_bzbl:
        if milestone.name == milestone_name:
            milestone.reference_payment_entry = payment_entry_name
            self.save()
            self.update_project_status_based_on_payments()
            return True
    return False    

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
    def set_missing_values(source, target):
        
        target.payment_type = "Pay"
        if source.researcher_details and len(source.researcher_details) > 0:
            researcher = source.researcher_details[0]
            if researcher.type =="Student":
                target.party_type = "Student"
                target.party = researcher.student
                target.party_name = researcher.first_name
            elif researcher.type =="Employee":
                target.party_type = "Employee"
                target.party = researcher.employee
                target.party_name = researcher.employee_name
            else:
                target.party_type = "Other"
                target.party = researcher.external_name

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

@frappe.whitelist()
def get_researcher_details(type, researcher_id):
    """Get researcher details including name, email, and gender"""
    if not type or not researcher_id:
        frappe.throw(_("Researcher Type and Researcher ID are required"))
    
    details = {
        "researcher_id": researcher_id,
        "researcher_name": "",
        "email": "",
        "gender": "",
        "college": "",
    }
    
    if type == "Employee":
        employee = frappe.db.get_value(
            "Employee", 
            researcher_id, 
            ["employee_name", "company_email", "personal_email", "gender", "cell_number", "company"], 
            as_dict=True
        )
        if employee:
            # Prefer company email, fallback to personal email
            email = employee.get("company_email") or employee.get("personal_email")
            details.update({
                "researcher_name": employee.get("employee_name", ""),
                "email": email or "",
                "gender": employee.get("gender", ""),
                "phone": employee.get("cell_number", ""),
                "college": employee.get("company", "")
            })
        else:
            frappe.throw(_("Employee {0} not found").format(researcher_id))
    
    elif type == "Student":
        student = frappe.db.get_value(
            "Student", 
            researcher_id, 
            ["student_name", "student_email_id", "gender", "student_mobile_number", "company"], 
            as_dict=True
        )
        if student:
            details.update({
                "researcher_name": student.get("student_name", ""),
                "email": student.get("student_email_id", ""),
                "gender": student.get("gender", ""),
                "phone": student.get("student_mobile_number", ""),
                "college": student.get("company", "")
            })
        else:
            frappe.throw(_("Student {0} not found").format(researcher_id))
    
    return details

@frappe.whitelist()
def update_payment_reference(project_name, milestone_name, payment_entry_name):
    """Update the milestone with payment entry reference"""
    project = frappe.get_doc("Research Project", project_name)
    project.update_milestone_payment_reference(milestone_name, payment_entry_name)
    return True
# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class ResearchProposal(Document):

    def validate(self):
        self.validate_milestone_percentage()
        self.validate_budget_amount()

    def validate_milestone_percentage(self):
        total_percentage = 0

        milestones = self.get("research_proposal_milestone_details") or []
        for d in milestones:
            if d.milestone_percentage:
                total_percentage += d.milestone_percentage

        if total_percentage > 100:
            frappe.throw(
                f"Total of Milestone Percentages cannot exceed 100%. Currently: {total_percentage}%"
            )
        if total_percentage < 100:
            frappe.throw(
                f"Total of Milestone Percentages must be exactly 100%. Currently: {total_percentage}%"
            )
            
    def validate_budget_amount(self):
        total_budget = 0
        milestones = self.get("research_proposal_milestone_details") or []

        for d in milestones:
            if d.budget_amount:
                total_budget += d.budget_amount

        self.total_expenses = total_budget

@frappe.whitelist()
def make_research_project(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.call_for_research = source.name
        target.grant_type = source.grant_type
        target.posting_date = source.posting_date
        for row in source.research_proposal_milestone_details:
            child = target.append("table_bzbl", {})
            child.date_for_milestone = row.get("date_for_milestone")
            child.milestone_percentage = row.get('milestone_percentage')
            child.budget_amount = row.get("budget_amount")
            child.milestone_descripton = row.get("milestone_descripton")
            
    return get_mapped_doc(
        "Research Proposal",
        source_name,
        {
            "Research Proposal": {
                "doctype": "Research Project",
                "field_map": {
                    "posting_date": "posting_date",
                    "grant_type": "grant_type",
                },
            }
        },
        target_doc,
        set_missing_values
    )

    
@frappe.whitelist()
def make_research_registration(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.call_for_research = source.name
    return get_mapped_doc(
        "Research Proposal",
        source_name,
        {
            "Research Proposal": {
                "doctype": "Research Registration",
                "field_map": {
                    "posting_date": "posting_date",
                    "grant_type": "grant_type",
                },
            }
        },
        target_doc,
        set_missing_values,
    )
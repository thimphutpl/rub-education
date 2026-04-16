# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import re
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate, today


class ResearchProposal(Document):

    def validate(self):
        self.validate_submission_deadline()
        self.validate_resubmission_deadline()

        # self.validate_milestone_percentage()
        self.validate_budget_amount()
        self.validate_word_count("abstract", "Abstract")
        self.validate_word_count("bg_and_prb_statement", "Background and Problem Statement")
        self.validate_word_count_hypothesis_impact("res_q_or_hypo", "Research Questions and Hypothesis")
        self.validate_word_count_hypothesis_impact("Research Impact", "Research Impact")
        # self.validate_research_question_word_count()
        self.validate_literature_review_word_count() 

        # #(max 1000 only)
        # self.validate_max_words("research_design", "Research Design")
        # self.validate_max_words("sampling_design", "Sampling Design")
        # self.validate_max_words("data_collection_tools_and_procedures", "Data Collection Tools and Procedures")
        # self.validate_max_words("data_analysis_tools_and_procedures", "Data Analysis Tools and Procedures")
        # self.validate_max_words("data_presentation", "Data Presentation")

        # total validation
        self.validate_total_research_words() 

    def get_context(context):
        context.breadcrumbs = [
            {"label": "Research Management", "route": "/app/research-management"}
        ]

    def on_submit(self):  
        self.validate_milestone_percentage()

    def validate_submission_deadline(self):
        if self.resubmission_deadline:
            pass

        """Prevent editing other fields if research_submission_date has passed"""
        if self.research_submission_deadline and not self.is_new() and not self.resubmission_deadline:
            submission_date = getdate(self.research_submission_deadline)
            current_date = getdate(today())
            
            if current_date > submission_date:
                # Check if this is an existing document being edited
                if self.get_doc_before_save():
                    frappe.throw(
                        f"Research submission deadline ({self.research_submission_deadline}) has passed. "
                        "You cannot edit any fields in this Research Proposal."
                    ) 

    def validate_resubmission_deadline(self):
        """Prevent editing other fields if resubmission_date has passed"""
        if self.resubmission_deadline and not self.is_new():
            submission_date = getdate(self.resubmission_deadline)
            current_date = getdate(today())
            
            if current_date > submission_date:
                # Check if this is an existing document being edited
                if self.get_doc_before_save():
                    frappe.throw(
                        f"Research resubmission deadline ({self.resubmission_deadline}) has passed. "
                        "You cannot edit any fields in this Research Proposal."
                    )                            

    def validate_total_research_words(self):
        fields = [
            "research_design",
            "sampling_design",
            "data_collection_tools_and_procedures",
            "data_analysis_tools_and_procedures",
            "data_presentation"
        ]

        total_words = 0

        for field in fields:
            value = self.get(field)
            if value:
                clean_text = re.sub('<[^<]+?>', '', value)
                words = clean_text.split()
                total_words += len(words)

        if total_words > 1000:
            frappe.throw(
                f"Total words for Research Sections cannot exceed 1000. Current: {total_words}"
            )        

    # def validate_max_words(self, fieldname, label):
    #     value = self.get(fieldname)

    #     if value:
    #         clean_text = re.sub('<[^<]+?>', '', value)
    #         words = clean_text.split()
    #         word_count = len(words)

    #         if word_count > 1000:
    #             frappe.throw(
    #                 f"{label} cannot exceed 1000 words. Current: {word_count}"
    #             )              

    def validate_research_question_word_count(self):
        if self.res_q_or_hypo:
            # remove HTML tags (Text Editor stores HTML)
            clean_text = re.sub('<[^<]+?>', '', self.res_q_or_hypo)

            words = clean_text.split()
            word_count = len(words)

            if word_count < 50 or word_count > 100:
                frappe.throw(
                    f"Research Questions and Hypothesis must be between 50 and 100 words. Current: {word_count}"
                )  

    def validate_literature_review_word_count(self):
        if self.literature_review:
            # remove HTML tags (Text Editor stores HTML)
            clean_text = re.sub('<[^<]+?>', '', self.literature_review)

            words = clean_text.split()
            word_count = len(words)

            if word_count < 500 or word_count > 600:
                frappe.throw(
                    f"Literature Review must be between 500 and 600 words. Current: {word_count}"
                )                 

    def validate_word_count(self, fieldname, label):
        value = self.get(fieldname)

        if value:
            clean_text = re.sub('<[^<]+?>', '', value)
            words = clean_text.split()
            word_count = len(words)

            # if word_count < 250 or word_count > 300:
            #     frappe.throw(
            #         f"{label} must be between 250 and 300 words. Current: {word_count}"
            #     )  

    def validate_word_count_hypothesis_impact(self, fieldname, label):
        value = self.get(fieldname)

        if value:
            clean_text = re.sub('<[^<]+?>', '', value)
            words = clean_text.split()
            word_count = len(words)

            if word_count < 50 or word_count > 100:
                frappe.throw(
                    f"{label} must be between 50 and 100 words. Current: {word_count}"
                )                                

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
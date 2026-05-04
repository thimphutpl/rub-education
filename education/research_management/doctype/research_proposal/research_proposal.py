# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import re
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate, today


class ResearchProposal(Document):

    def after_insert(self):
        """Automatically create Research Registration after proposal is inserted"""
        self.create_research_registration()
    
    def create_research_registration(self):
        """Create a Research Registration document from this proposal"""
        
        # Generate the name based on grant_type/YYYY/MM/serial_no
        registration_number = self.generate_registration_name()
        
        # Create Research Registration document
        registration = frappe.get_doc({
            "doctype": "Research Registration",
            "research_proposal": self.name,
            "research_title": self.research_title,
            "grant_type": self.grant_type,
            "registration_number": registration_number,
            "registration_date": frappe.utils.today(),
            "title_of_the_project": self.topic_of_the_research_call,
            "project_start_date": self.posting_date,
            "project_end_date": self.research_submission_deadline,
            "funding_agency": self.grant_type,
            "funding_amount": self.grant_amount,
            "status": "Registered"
        })
        
        registration.insert(ignore_permissions=True)
        # Submit the document
        registration.submit()
        frappe.db.commit()  # Commit the transaction
        frappe.msgprint(
            msg=f"Research Registration <b>{registration_number}</b> created and submitted successfully",
            title="Registration Created",
            indicator="green"
        )
        # Return the registration details for reference
        return registration
        # frappe.msgprint(f"Research Registration {registration.name} created successfully")
    
    def generate_registration_name(self):
        """
        Generate registration name in format: grant_type/YYYY/MM/serial_no
        Example: STUDENT/2025/05/001
        """
        from frappe.utils import getdate
        
        grant_type = self.grant_type or "GEN"
        # Remove spaces and special characters, convert to uppercase
        grant_type = grant_type.upper().replace(" ", "_")
        
        current_date = getdate()
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        
        # Get the last serial number for this research type, year, and month
        last_registration = frappe.db.sql("""
            SELECT registration_number 
            FROM `tabResearch Registration` 
            WHERE registration_number LIKE %s 
            ORDER BY creation DESC 
            LIMIT 1
        """, (f"{grant_type}/{year}/{month}/%",), as_dict=True)
        
        if last_registration:
            # Extract serial number from last registration name
            last_serial = int(last_registration[0].registration_number.split('/')[-1])
            new_serial = last_serial + 1
        else:
            new_serial = 1
        
        # Format serial number as 3-digit (001, 002, etc.)
        serial_no = str(new_serial).zfill(3)
        
        return f"{grant_type}/{year}/{month}/{serial_no}"

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
        self.validate_researcher_details()

    def validate_grant_amount(self):
        if self.total_expenses > self.grant_amount:
            difference = self.total_expenses - self.grant_amount
            frappe.throw(
                title="Invalid Amount",
                msg=f"Total Expenses ({self.total_expenses}) cannot exceed Grant Amount ({self.grant_amount}). The difference amount is {difference} . "
            )      

    def get_context(context):
        context.breadcrumbs = [
            {"label": "Research Management", "route": "/app/research-management"}
        ]

    def on_submit(self):  
        self.validate_milestone_percentage()
        self.validate_grant_amount()
    
    def validate_researcher_details(self):
        """Validate researcher details and fetch names if missing"""
        if not self.researcher_details:
            return
        
        for row in self.researcher_details:
            # if row.researcher_id and not row.researcher_name:
            #     row.researcher_name = self.get_researcher_name(
            #         row.type, 
            #         row.researcher_id
            #     )
            if row.researcher_id:
                if not row.researcher_name or not row.email or not row.gender:
                    details = self.get_researcher_details(
                        row.researcher_type, 
                        row.researcher_id
                    )
                    if details:
                        row.researcher_name = details.get("researcher_name", "")
                        row.email = details.get("email", "")
                        row.gender = details.get("gender", "")
                        row.phone = details.get("phone", "")
    
    # @staticmethod
    # def get_researcher_name(type, researcher_id):
    #     """Get name based on researcher type"""
    #     if not type or not researcher_id:
    #         return ""
        
    #     if type == "Employee":
    #         return frappe.db.get_value("Employee", researcher_id, "employee_name")
    #     elif type == "Student":
    #         return frappe.db.get_value("Student", researcher_id, "student_name")
    #     else:
    #         return ""

    @staticmethod
    def get_researcher_details(researcher_type, researcher_id):
        """Get complete researcher details based on type and ID"""
        if not researcher_type or not researcher_id:
            return {}
        
        details = {
            "researcher_name": "",
            "email": "",
            "gender": "",
            "phone": ""
        }
        
        if researcher_type == "Employee":
            employee = frappe.db.get_value(
                "Employee", 
                researcher_id, 
                ["employee_name", "company_email", "gender", "cell_number"], 
                as_dict=True
            )
            if employee:
                details.update({
                    "researcher_name": employee.get("employee_name", ""),
                    "email": employee.get("company_email", ""),
                    "gender": employee.get("gender", ""),
                    "phone": employee.get("cell_number", "")
                })
        
        elif researcher_type == "Student":
            student = frappe.db.get_value(
                "Student", 
                researcher_id, 
                ["student_name", "user", "gender", "student_mobile_number"], 
                as_dict=True
            )
            if student:
                details.update({
                    "researcher_name": student.get("student_name", ""),
                    "email": student.get("user", ""),
                    "gender": student.get("gender", ""),
                    "phone": student.get("student_mobile_number", "")
                })
        
        return details

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
                    "topic_of_the_research_call":"title_of_the_project",
                    "grant_amount":"funding_amount",
                    "posting_date":"project_start_date",
                    "research_submission_deadline":"project_end_date"
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

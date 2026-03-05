# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe

# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "College", "fieldname": "college", "fieldtype": "Link", "options": "Company", "width": 200},
        {"label": "Research Center", "fieldname": "research_center_name", "fieldtype": "Link", "options": "Research Center", "width": 220},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},

        {"label": "Introduction", "fieldname": "introduction", "fieldtype": "Data", "width": 350},

        {"label": "Research Projects", "fieldname": "long_text_hdcp", "fieldtype": "Data", "width": 350},

        {"label": "Research Funding", "fieldname": "research_funding", "fieldtype": "Data", "width": 350},

        {"label": "Researcher Productivity & Impact", "fieldname": "researcher_productivity_and_impact", "fieldtype": "Data", "width": 350},

        {"label": "Knowledge Transfer & Outreach", "fieldname": "knowledge_transfer_and_outreach", "fieldtype": "Data", "width": 350},

        {"label": "Research Infrastructure", "fieldname": "research_infrastructure_and_facilities", "fieldtype": "Data", "width": 350},

        {"label": "Collaborations & Partnerships", "fieldname": "collaborations_and_partnerships", "fieldtype": "Data", "width": 350},

        {"label": "Impact & Relevance", "fieldname": "impact_and_relevance", "fieldtype": "Data", "width": 350},

        {"label": "Financial Overview", "fieldname": "financial_overview", "fieldtype": "Data", "width": 300},

        {"label": "Key Challenges & Mitigation", "fieldname": "key_challenges_and_mitifation_strategies", "fieldtype": "Data", "width": 350},

        {"label": "Future Plans", "fieldname": "future_plans_and_objectives", "fieldtype": "Data", "width": 350},

        {"label": "Conclusion", "fieldname": "conclusion", "fieldtype": "Data", "width": 300},

        {"label": "Contact Information", "fieldname": "contact_information", "fieldtype": "Data", "width": 250},
    ]


def get_data(filters):
    conditions = ""

    if filters.get("research_center_name"):
        conditions += " AND research_center_name = %(research_center_name)s"

    if filters.get("college"):
        conditions += " AND college = %(college)s"

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND posting_date BETWEEN %(from_date)s AND %(to_date)s"

    data = frappe.db.sql(f"""
        SELECT
            college,
            research_center_name,
            posting_date,
            introduction,
            long_text_hdcp,
            research_funding,
            researcher_productivity_and_impact,
            knowledge_transfer_and_outreach,
            research_infrastructure_and_facilities,
            collaborations_and_partnerships,
            impact_and_relevance,
            financial_overview,
            key_challenges_and_mitifation_strategies,
            future_plans_and_objectives,
            conclusion,
            contact_information
        FROM `tabResearch Center Progress Reporting`
        WHERE docstatus = 1
        {conditions}
        ORDER BY posting_date DESC
    """, filters, as_dict=True)

    return data

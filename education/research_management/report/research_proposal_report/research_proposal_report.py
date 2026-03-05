# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):

    columns = [
        {"label": "Proposal ID", "fieldname": "name", "fieldtype": "Link", "options": "Research Proposal", "width": 160},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": "Academic Year", "fieldname": "academic_year", "width": 120},
        {"label": "Research Title", "fieldname": "research_title", "width": 250},
        {"label": "Project Title", "fieldname": "topic_of_the_research_call", "width": 200},
        {"label": "Research Type", "fieldname": "research_type", "width": 140},
        {"label": "Grant Type", "fieldname": "grant_type", "width": 140},
        {"label": "Grant Amount", "fieldname": "grant_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Total Budget Proposed", "fieldname": "total_expenses", "fieldtype": "Currency", "width": 150},
        {"label": "Project Period", "fieldname": "project_period", "width": 130},
        {"label": "Marks", "fieldname": "marks", "width": 80},
        {"label": "Researchers", "fieldname": "researcher_count", "width": 100},
    ]

    conditions = " WHERE rp.docstatus = 1 "

    if filters.get("academic_year"):
        conditions += " AND rp.academic_year = %(academic_year)s"

    if filters.get("research_type"):
        conditions += " AND rp.research_type = %(research_type)s"

    if filters.get("grant_type"):
        conditions += " AND rp.grant_type = %(grant_type)s"

    data = frappe.db.sql(f"""
        SELECT
            rp.name,
            rp.posting_date,
            rp.academic_year,
            rp.research_title,
            rp.topic_of_the_research_call,
            rp.research_type,
            rp.grant_type,
            rp.grant_amount,
            rp.total_expenses,
            rp.project_period,
            rp.marks,
            COUNT(rd.name) as researcher_count
        FROM `tabResearch Proposal` rp
        LEFT JOIN `tabResearcher Details` rd
            ON rd.parent = rp.name
        {conditions}
        GROUP BY rp.name
        ORDER BY rp.posting_date DESC
    """, filters, as_dict=1)

    return columns, data
# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):

    columns = [
        {"label": "Project ID", "fieldname": "name", "fieldtype": "Link", "options": "Research Project", "width": 160},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Research Title", "fieldname": "research_title", "width": 260},
        {"label": "Grant Type", "fieldname": "grant_type", "width": 150},
        {"label": "Grant Amount", "fieldname": "grant_amount", "fieldtype": "Currency", "width": 140},
        {"label": "Milestone Progress (%)", "fieldname": "research_milestone_progress", "width": 150},
        {"label": "Total Budget Consumed", "fieldname": "total_budget_consumed", "fieldtype": "Currency", "width": 170},
        {"label": "Researchers", "fieldname": "researcher_count", "width": 110},
        {"label": "Total Milestones", "fieldname": "milestone_count", "width": 120},
        {"label": "Approved Milestones", "fieldname": "approved_milestones", "width": 150},
    ]

    conditions = " WHERE rp.docstatus = 1 "

    if filters.get("from_date"):
        conditions += " AND rp.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND rp.posting_date <= %(to_date)s"

    if filters.get("grant_type"):
        conditions += " AND rp.grant_type = %(grant_type)s"

    data = frappe.db.sql(f"""
        SELECT
            rp.name,
            rp.posting_date,
            rp.research_title,
            rp.grant_type,
            rp.grant_amount,
            rp.research_milestone_progress,
            rp.total_budget_consumed,
            COUNT(DISTINCT rd.name) as researcher_count,
            COUNT(DISTINCT rm.name) as milestone_count,
            SUM(
                CASE 
                    WHEN rm.status = 'Approved' THEN 1
                    ELSE 0
                END
            ) as approved_milestones
        FROM `tabResearch Project` rp

        LEFT JOIN `tabResearcher Details` rd
            ON rd.parent = rp.name

        LEFT JOIN `tabResearch Milestone Item` rm
            ON rm.parent = rp.name

        {conditions}

        GROUP BY rp.name
        ORDER BY rp.posting_date DESC
    """, filters, as_dict=1)

    return columns, data

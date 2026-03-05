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
        {"label": "College", "fieldname": "college", "fieldtype": "Link", "options": "Company", "width": 180},
        {"label": "Research Center", "fieldname": "research_center_name", "fieldtype": "Link", "options": "Research Center", "width": 220},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Policy Briefs", "fieldname": "policy_briefs", "fieldtype": "Int", "width": 130},
        {"label": "Journals", "fieldname": "journals", "fieldtype": "Int", "width": 120},
        {"label": "Research Articles", "fieldname": "research_articles", "fieldtype": "Int", "width": 140},
        {"label": "Conference Papers", "fieldname": "conference_papers", "fieldtype": "Int", "width": 150},
        {"label": "Book Chapters", "fieldname": "book_chapters", "fieldtype": "Int", "width": 130},
        {"label": "Trainings/Workshops", "fieldname": "training_workshops", "fieldtype": "Int", "width": 160},
        {"label": "Research Events", "fieldname": "research_events", "fieldtype": "Int", "width": 150},
        {"label": "Research Projects", "fieldname": "research_projects", "fieldtype": "Int", "width": 160},
    ]


def get_data(filters):

    conditions = ""

    if filters.get("college"):
        conditions += " AND r.car.college = %(college)s"

    if filters.get("research_center_name"):
        conditions += " AND r.car.research_center_name = %(research_center_name)s"

    if filters.get("from_date"):
        conditions += " AND r.car.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND r.car.posting_date <= %(to_date)s"

    data = frappe.db.sql("""
        SELECT
            car.college,
            car.research_center_name,
            car.posting_date,

            SUM(CASE WHEN r.reporting_type = 'Policy Briefs' THEN 1 ELSE 0 END) policy_briefs,
            SUM(CASE WHEN r.reporting_type = 'Journals' THEN 1 ELSE 0 END) journals,
            SUM(CASE WHEN r.reporting_type = 'Research Articles' THEN 1 ELSE 0 END) research_articles,
            SUM(CASE WHEN r.reporting_type = 'Conference Seminar Paper' THEN 1 ELSE 0 END) conference_papers,
            SUM(CASE WHEN r.reporting_type = 'Book Chapters' THEN 1 ELSE 0 END) book_chapters,
            SUM(CASE WHEN r.reporting_type = 'Knowledge Transfer and Community Service' THEN 1 ELSE 0 END) training_workshops,
            SUM(CASE WHEN r.reporting_type = 'Research Event Organized' THEN 1 ELSE 0 END) research_events,
            SUM(CASE WHEN r.reporting_type = 'Research Projects and Funding' THEN 1 ELSE 0 END) research_projects

        FROM
            `tabResearch Center Annual Reporting` car

        LEFT JOIN
            `tabResearch Center Reporting Items` r
        ON
            car.research_center_name = r.research_center_name
            AND car.posting_date = r.posting_date
            AND r.docstatus = 1

        WHERE
            car.docstatus = 1
            {conditions}

        GROUP BY
            car.name
        ORDER BY
            car.posting_date DESC

    """.format(conditions=conditions), filters, as_dict=1)

    return data
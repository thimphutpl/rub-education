# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe

import frappe

def execute(filters=None):

    columns = [
        {"label": "College", "fieldname": "college", "fieldtype": "Link", "options": "Company", "width": 180},
        {"label": "Research Center", "fieldname": "research_center_name", "fieldtype": "Link", "options": "Research Center", "width": 200},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": "Year", "fieldname": "year", "width": 100},
        {"label": "Reporting Type", "fieldname": "reporting_type", "width": 200},
        {"label": "Title", "fieldname": "title", "width": 300},
        {"label": "Source / Publisher / Event", "fieldname": "source", "width": 250},
        {"label": "Remarks", "fieldname": "remarks", "width": 250},
    ]

    data = frappe.db.sql("""
        SELECT
            college,
            research_center_name,
            posting_date,
            year,
            reporting_type,

            CASE
                WHEN reporting_type='Policy Briefs' THEN policy_briefs_title
                WHEN reporting_type='Journals' THEN name_of_the_journal
                WHEN reporting_type='Research Articles' THEN research_articles_title
                WHEN reporting_type='Conference Seminar Paper' THEN conference_seminar_paper_title
                WHEN reporting_type='Book Chapters' THEN book_chapter_title
                WHEN reporting_type='Knowledge Transfer and Community Service' THEN trainings_organized_title
                WHEN reporting_type='Research Event Organized' THEN research_event_organized_title
                WHEN reporting_type='Research Projects and Funding' THEN project_title
            END as title,

            CASE
                WHEN reporting_type='Policy Briefs' THEN publisher_policy_brief
                WHEN reporting_type='Journals' THEN website_links_journal
                WHEN reporting_type='Research Articles' THEN publisher
                WHEN reporting_type='Conference Seminar Paper' THEN conferenceseminar_title
                WHEN reporting_type='Book Chapters' THEN book_title
                WHEN reporting_type='Knowledge Transfer and Community Service' THEN venue
                WHEN reporting_type='Research Event Organized' THEN venues
                WHEN reporting_type='Research Projects and Funding' THEN funding_agency_nameinstitution
            END as source,

            CASE
                WHEN reporting_type='Policy Briefs' THEN remarks_policy_briefs
                WHEN reporting_type='Knowledge Transfer and Community Service' THEN remarks
                WHEN reporting_type='Research Event Organized' THEN remarkss
            END as remarks

        FROM `tabResearch Center Reporting Items`
        WHERE docstatus = 1
    """, as_dict=1)

    return columns, data

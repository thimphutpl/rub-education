// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Research Center Reporting Items Report"] = {
	filters: [

        {
            fieldname: "college",
            label: "College",
            fieldtype: "Link",
            options: "Company"
        },

        {
            fieldname: "research_center_name",
            label: "Research Center",
            fieldtype: "Link",
            options: "Research Center"
        },

        {
            fieldname: "reporting_type",
            label: "Reporting Type",
            fieldtype: "Select",
            options: "\nPolicy Briefs\nJournals\nResearch Articles\nConference Seminar Paper\nBook Chapters\nKnowledge Transfer and Community Service\nResearch Event Organized\nResearch Projects and Funding"
        },

        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Link",
            options: "Fiscal Year"
        }

    ]
};

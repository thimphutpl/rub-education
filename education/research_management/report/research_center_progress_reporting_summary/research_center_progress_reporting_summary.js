// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Research Center Progress Reporting Summary"] = {
	"filters": [

        {
            "fieldname": "college",
            "label": "College",
            "fieldtype": "Link",
            "options": "Company"
        },

        {
            "fieldname": "research_center_name",
            "label": "Research Center",
            "fieldtype": "Link",
            "options": "Research Center"
        },

        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date"
        },

        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date"
        }
    ]
};

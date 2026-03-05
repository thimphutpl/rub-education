// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Research Proposal Report"] = {

    filters: [

        {
            fieldname: "academic_year",
            label: "Academic Year",
            fieldtype: "Link",
            options: "Fiscal Year"
        },

        {
            fieldname: "research_type",
            label: "Research Type",
            fieldtype: "Link",
            options: "Research Type"
        },

        {
            fieldname: "grant_type",
            label: "Grant Type",
            fieldtype: "Link",
            options: "Grant Type"
        },

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        }

    ]
};
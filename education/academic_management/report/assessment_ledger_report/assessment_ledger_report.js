// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Assessment Ledger Report"] = {
	"filters": [
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "academic_year",
            "label": "Academic Year",
            "fieldtype": "Link",
            "options": "Academic Year"
        },
        {
            "fieldname": "academic_term",
            "label": "Academic Term",
            "fieldtype": "Link",
            "options": "Academic Term"
        },
        {
            "fieldname": "module",
            "label": "Module",
            "fieldtype": "Link",
            "options": "Module"
        },
        {
            "fieldname": "tutor",
            "label": "Tutor",
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "assessment_component",
            "label": "Assessment Component",
            "fieldtype": "Link",
            "options": "Assessment Component"
        },
        {
            "fieldname": "assessment_type",
            "label": "Assessment Type",
            "fieldtype": "Select",
            "options": "\nRegular Assessment\nRe-assessment\nRe-evaluation\nRe-check"
        },
        {
            "fieldname": "student",
            "label": "Student",
            "fieldtype": "Link",
            "options": "Student"
        },
        {
            "fieldname": "show_previous_attempts",
            "label": "Show Previous Attempts",
            "fieldtype": "Check",
            "default": 0
        },
        {
            "fieldname": "show_cancelled_entries",
            "label": "Show Cancelled Entries",
            "fieldtype": "Check",
            "default": 0
        }
    ],
    "formatter": function (value, row, column, data, default_formatter) {
        // Use default formatter first
        value = default_formatter(value, row, column, data);
    
        // Check that data is valid before styling
        if (data && column.fieldname === "marks_obtained" && data.marks_obtained < data.passing_marks) {
            // Apply style safely
            value = `<span style="color:red; font-weight:bold;">${value}</span>`;
        }
        else if (data && column.fieldname === "marks_obtained" ){
            value = `<span style="color:green; font-weight:bold;">${value}</span>`;
        }
    
        return value;
    }
};

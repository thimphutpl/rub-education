// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Semester Result Declaration"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1
		},
		{
			fieldname: "academic_term",
			label: __("Academic Term"),
			fieldtype: "Link",
			options: "Academic Term",
			reqd: 1
		},
		{
			fieldname: "programme",
			label: __("Programme"),
			fieldtype: "Link",
			options: "Programme Master",
			reqd: 1
		},
		{
			fieldname: "student_section",
			label: __("Student Section"),
			fieldtype: "Link",
			options: "Student Section",
			reqd: 1
		},
	]
};

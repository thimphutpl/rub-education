// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Individual Exam Timetable Report"] = {
	"filters": [
		{
			"fieldname": "academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year"
		},
		{
			"fieldname": "academic_term",
			"label": __("Academic Term"),
			"fieldtype": "Link",
			"options": "Academic Term"
		},
		{
			"fieldname": "exam_date",
			"label": __("Exam Date"),
			"fieldtype": "Date"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Optional: Add color coding for different days
		if (column.fieldname == "day") {
			if (value == "Saturday" || value == "Sunday") {
				value = `<span style="color: orange;">${value}</span>`;
			}
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Optional: Add custom initialization code
		console.log("Report loaded");
	}
};
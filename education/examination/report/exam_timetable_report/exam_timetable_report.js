// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Exam Timetable Report"] = {
	"filters": [
		{
			fieldname: "exam_date",
			label: __("Exam Date"),
			fieldtype: "Date",
			reqd: 0
		},
		{
			fieldname: "room",
			label: __("Exam Room"),
			fieldtype: "Link",
			options: "Room",
			reqd: 0
		}
	]
};

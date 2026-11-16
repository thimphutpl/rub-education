// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Student Batch-Wise Attendance"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
		},
		{
			fieldname: "college",
			label: __("College"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,

			get_query: function () {
				return {
					query: "education.education.report.student_batch_wise_attendance.student_batch_wise_attendance.get_college_query",
				};
			},

			on_change: function () {
				frappe.query_report.set_filter_value({
					academic_term: "",
					module: "",
					student_group: "",
					student: "",
				});
			},
		},
		{
			fieldname: "academic_term",
			label: __("Academic Term"),
			fieldtype: "Link",
			options: "Academic Term",
			reqd: 1,

			get_query: function () {
				return {
					query: "education.education.report.student_batch_wise_attendance.student_batch_wise_attendance.get_academic_term_query",
					filters: {
						college: frappe.query_report.get_filter_value("college"),
					},
				};
			},

			on_change: function () {
				frappe.query_report.set_filter_value({
					module: "",
					student_group: "",
					student: "",
				});
			},
		},
		{
			fieldname: "module",
			label: __("Module"),
			fieldtype: "Link",
			options: "Module",
			reqd: 1,

			get_query: function () {
				return {
					query: "education.education.report.student_batch_wise_attendance.student_batch_wise_attendance.get_module_query",
					filters: {
						college: frappe.query_report.get_filter_value("college"),
						academic_term:
							frappe.query_report.get_filter_value("academic_term"),
					},
				};
			},

			on_change: function () {
				frappe.query_report.set_filter_value({
					student_group: "",
					student: "",
				});
			},
		},
		{
			fieldname: "student",
			label: __("Student"),
			fieldtype: "Link",
			options: "Student",
		
			get_query: function () {
				return {
					query: "education.education.report.student_batch_wise_attendance.student_batch_wise_attendance.get_student_query",
					filters: {
						college: frappe.query_report.get_filter_value("college"),
						academic_term:
							frappe.query_report.get_filter_value("academic_term"),
						module: frappe.query_report.get_filter_value("module"),
						student_group:
							frappe.query_report.get_filter_value("student_group"),
					},
				};
			},
		},
		{
			fieldname: "student_group",
			label: __("Student Section"),
			fieldtype: "Link",
			options: "Student Section",
			
			on_change: function () {
				frappe.query_report.set_filter_value("student", "");
			},
			
			get_query: function () {
				return {
					query: "education.education.report.student_batch_wise_attendance.student_batch_wise_attendance.get_student_section_query",
					filters: {
						college: frappe.query_report.get_filter_value("college"),
						academic_term:
							frappe.query_report.get_filter_value("academic_term"),
						module: frappe.query_report.get_filter_value("module"),
					},
				};
			},
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (data && data.student_name === "TOTAL") {
			return `<span style="font-weight: 700 !important;">${value}</span>`;
		}

		return value;
	},
};
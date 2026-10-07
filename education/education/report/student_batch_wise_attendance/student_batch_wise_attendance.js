// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports['Student Batch-Wise Attendance'] = {
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
		},
    {
			fieldname: "academic_term",
			label: __("Academic Term"),
			fieldtype: "Link",
			options: "Academic Term",
			reqd: 1,
		},
    // {
	// 		fieldname: "link_nvfk",
	// 		label: __("Programme"),
	// 		fieldtype: "Link",
	// 		options: "Programme",
	// 		reqd: 1,

	// 		get_query: function () {
	// 			return {
	// 				query: "education.education.report.student_batch_wise_attendance.student_batch_wise_attendance.get_programme_query",
	// 				filters: {
	// 					college: frappe.query_report.get_filter_value("college"),
	// 					academic_term: frappe.query_report.get_filter_value("academic_term"),
	// 				},
	// 			};
	// 		},
		
	// 		on_change: function () {
	// 			frappe.query_report.set_filter_value("module", "");
	// 			frappe.query_report.set_filter_value("student_group", "");
	// 			frappe.query_report.set_filter_value("student", "");
	// 		},
	// 	},
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
						academic_term: frappe.query_report.get_filter_value("academic_term"),
						// link_nvfk: frappe.query_report.get_filter_value("link_nvfk"),
					},
				};
			},
		
			on_change: function () {
				frappe.query_report.set_filter_value("student_group", "");
				frappe.query_report.set_filter_value("student", "");
			},
		},
		{
			fieldname: "student",
			label: __("Student"),
			fieldtype: "Link",
			options: "Student",
		},
    {
			fieldname: "student_group",
			label: __("Student Section"),
			fieldtype: "Link",
			options: "Student Section",

			get_query: function () {
				return {
					query: "education.education.report.student_batch_wise_attendance.student_batch_wise_attendance.get_student_section_query",
					filters: {
						college: frappe.query_report.get_filter_value("college"),
						academic_term: frappe.query_report.get_filter_value("academic_term"),
						link_nvfk: frappe.query_report.get_filter_value("link_nvfk"),
						module: frappe.query_report.get_filter_value("module"),
					},
				};
			},
			
		},
    // {
    //   fieldname: 'date',
    //   label: __('Date'),
    //   fieldtype: 'Date',
    // //   default: frappe.datetime.get_today(),
    // //   reqd: 1,
    // },
		
  ],
  formatter: function (value, row, column, data, default_formatter) {
	value = default_formatter(value, row, column, data);

	if (data && data.student_name === "TOTAL") {
		return `<span style="font-weight: 700 !important;">${value}</span>`;
	}

	return value;
},
}

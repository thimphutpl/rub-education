// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports['Student Batch-Wise Attendance'] = {
  filters: [
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
    {
			fieldname: "link_nvfk",
			label: __("Programme"),
			fieldtype: "Link",
			options: "Programme",
			reqd: 1,
		},
    {
			fieldname: "module",
			label: __("Module"),
			fieldtype: "Link",
			options: "Module",
		},
    {
			fieldname: "tutor",
			label: __("Tutor"),
			fieldtype: "Link",
			options: "Employee",
		},
    {
			fieldname: "student_group",
			label: __("Student Section"),
			fieldtype: "Link",
			options: "Student Section",
			
		},
    {
      fieldname: 'date',
      label: __('Date'),
      fieldtype: 'Date',
    //   default: frappe.datetime.get_today(),
    //   reqd: 1,
    },
		
  ],
  formatter: function (value, row, column, data, default_formatter) {
	value = default_formatter(value, row, column, data);

	if (data && data.student_name === "TOTAL") {
		return `<span style="font-weight: 700 !important;">${value}</span>`;
	}

	return value;
},
}

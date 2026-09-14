// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports['Student Monthly Attendance Sheet'] = {
  filters: [
    {
      fieldname: 'month',
      label: __('Month'),
      fieldtype: 'Select',
      options: 'Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec',
      default: [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
      ][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()], reqd: 1,
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
		{
			fieldname: "link_nvfk",
			label: __("Programme"),
			fieldtype: "Link",
			options: "Programme",
			reqd: 1,
		},
    
    {
      fieldname: 'student_section',
      label: __('Student Section'),
      fieldtype: 'Link',
      options: 'Student Section',
     
    },
  ],

}

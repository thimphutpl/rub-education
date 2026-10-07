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
    // {
	// 		fieldname: "from_date",
	// 		label: __("From Date"),
	// 		fieldtype: "Date",
	// 		reqd: 1,
	// 	},
	// 	{
	// 		fieldname: "to_date",
	// 		label: __("To Date"),
	// 		fieldtype: "Date",
	// 		reqd: 1,
	// 	},
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
		// 	fieldname: "link_nvfk",
		// 	label: __("Programme"),
		// 	fieldtype: "Link",
		// 	options: "Programme",
		// 	reqd: 1,
		// },
        {
			fieldname: "module",
			label: __("Module"),
			fieldtype: "Link",
			options: "Module",
            reqd: 1,
		},
    
    {
      fieldname: 'student_section',
      label: __('Student Section'),
      fieldtype: 'Link',
      options: 'Student Section',
     
    },
     {
      fieldname: 'student',
      label: __('Student'),
      fieldtype: 'Link',
      options: 'Student',
     
    },
  ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // Present
        if (value === "P") {
            return `
                <span style="
                    background:#DCFCE7;
                    color:#15803D;
                    font-weight:700;
                    padding:3px 9px;
                    border-radius:5px;
                    display:inline-block;
                    min-width:25px;
                    text-align:center;
                ">P</span>
            `;
        }

        // Absent
        if (value === "A") {
            return `
                <span style="
                    background:#FEE2E2;
                    color:#DC2626;
                    font-weight:700;
                    padding:3px 9px;
                    border-radius:5px;
                    display:inline-block;
                    min-width:25px;
                    text-align:center;
                ">A</span>
            `;
        }

        // Holiday
        if (value === "H") {
            return `
                <span style="
                    background:#FEF3C7;
                    color:#D97706;
                    font-weight:700;
                    padding:3px 9px;
                    border-radius:5px;
                    display:inline-block;
                    min-width:25px;
                    text-align:center;
                ">H</span>
            `;
        }

        // Leave
        if (value === "L") {
            return `
                <span style="
                    background:#DBEAFE;
                    color:#2563EB;
                    font-weight:700;
                    padding:3px 9px;
                    border-radius:5px;
                    display:inline-block;
                    min-width:25px;
                    text-align:center;
                ">L</span>
            `;
        }

        // Inactive
        if (value === "-") {
            return `
                <span style="
                    color:#9CA3AF;
                    font-weight:600;
                ">-</span>
            `;
        }

        return value;
    },

}

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
    
        get_query: function () {
            return {
                query: "education.education.report.student_batch_wise_attendance.student_batch_wise_attendance.get_college_query",
            };
        },
    
        on_change: function () {
            frappe.query_report.set_filter_value({
                academic_term: "",
                module: "",
                student_section: "",
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
                    college:
                        frappe.query_report.get_filter_value("college"),
                },
            };
        },
    
        on_change: function () {
            frappe.query_report.set_filter_value({
                module: "",
                student_section: "",
                student: "",
            });
        },
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
        
            get_query: function () {
                return {
                    query: "education.education.report.student_batch_wise_attendance.student_batch_wise_attendance.get_module_query",
                    filters: {
                        college:
                            frappe.query_report.get_filter_value("college"),
                        academic_term:
                            frappe.query_report.get_filter_value("academic_term"),
                    },
                };
            },
        
            on_change: function () {
                frappe.query_report.set_filter_value({
                    student_section: "",
                    student: "",
                });
            },
        },
    
        {
            fieldname: "student_section",
            label: __("Student Section"),
            fieldtype: "Link",
            options: "Student Section",
        
            get_query: function () {
                return {
                    query: "education.education.report.student_batch_wise_attendance.student_batch_wise_attendance.get_student_section_query",
                    filters: {
                        college:
                            frappe.query_report.get_filter_value("college"),
                        academic_term:
                            frappe.query_report.get_filter_value("academic_term"),
                        module:
                            frappe.query_report.get_filter_value("module"),
                    },
                };
            },
        
            on_change: function () {
                frappe.query_report.set_filter_value("student", "");
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
                        college:
                            frappe.query_report.get_filter_value("college"),
                        academic_term:
                            frappe.query_report.get_filter_value("academic_term"),
                        module:
                            frappe.query_report.get_filter_value("module"),
                        student_group:
                            frappe.query_report.get_filter_value("student_section"),
                    },
                };
            },
        },
  ],

    // formatter: function (value, row, column, data, default_formatter) {
    //     value = default_formatter(value, row, column, data);

    //     // Present
    //     if (value === "P") {
    //         return `
    //             <span style="
    //                 background:#DCFCE7;
    //                 color:#15803D;
    //                 font-weight:700;
    //                 padding:3px 9px;
    //                 border-radius:5px;
    //                 display:inline-block;
    //                 min-width:25px;
    //                 text-align:center;
    //             ">P</span>
    //         `;
    //     }

    //     // Absent
    //     if (value === "A") {
    //         return `
    //             <span style="
    //                 background:#FEE2E2;
    //                 color:#DC2626;
    //                 font-weight:700;
    //                 padding:3px 9px;
    //                 border-radius:5px;
    //                 display:inline-block;
    //                 min-width:25px;
    //                 text-align:center;
    //             ">A</span>
    //         `;
    //     }

    //     // Holiday
    //     if (value === "H") {
    //         return `
    //             <span style="
    //                 background:#FEF3C7;
    //                 color:#D97706;
    //                 font-weight:700;
    //                 padding:3px 9px;
    //                 border-radius:5px;
    //                 display:inline-block;
    //                 min-width:25px;
    //                 text-align:center;
    //             ">H</span>
    //         `;
    //     }

    //     // Leave
    //     if (value === "L") {
    //         return `
    //             <span style="
    //                 background:#DBEAFE;
    //                 color:#2563EB;
    //                 font-weight:700;
    //                 padding:3px 9px;
    //                 border-radius:5px;
    //                 display:inline-block;
    //                 min-width:25px;
    //                 text-align:center;
    //             ">L</span>
    //         `;
    //     }

    //     // Inactive
    //     if (value === "-") {
    //         return `
    //             <span style="
    //                 color:#9CA3AF;
    //                 font-weight:600;
    //             ">-</span>
    //         `;
    //     }

    //     return value;
    // },
    formatter: function (value, row, column, data, default_formatter) {

        // Keep Student and Student Name columns unchanged
        if (!/^\d{1,2}$/.test(String(column.fieldname || ""))) {
            return default_formatter(value, row, column, data);
        }
    
        if (value === null || value === undefined || value === "") {
            return "";
        }
    
        const colors = {
            P: ["#DCFCE7", "#15803D"],
            A: ["#FEE2E2", "#DC2626"],
            H: ["#FEF3C7", "#D97706"],
            L: ["#DBEAFE", "#2563EB"]
        };
    
        // Separate block periods
        const periods = String(value).split("|");
    
        const badges = periods.map((period) => {
    
            period = period.trim();
    
            if (period === "-") {
                return `<span style="color:#9CA3AF;">-</span>`;
            }
    
            // Extract P, A, H or L and ignore the timings
            const match = period.match(/^([PAHL])(?:\s|$)/);
    
            if (!match) {
                return "";
            }
    
            const status = match[1];
            const [background, color] = colors[status];
    
            return `
                <span style="
                    background:${background};
                    color:${color};
                    padding:3px 7px;
                    border-radius:5px;
                    font-weight:700;
                    display:inline-block;
                    min-width:24px;
                    text-align:center;
                ">${status}</span>
            `;
    
        }).join("");
    
        return `
            <div style="
                display:flex;
                align-items:center;
                gap:4px;
                white-space:nowrap;
            ">
                ${badges}
            </div>
        `;
    },
};

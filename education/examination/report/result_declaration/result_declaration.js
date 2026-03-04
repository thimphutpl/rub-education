frappe.query_reports["Result Declaration"] = {
    "filters": [
        {
            fieldname: "student",
            label: __("Student"),
            fieldtype: "Link",
            options: "Student",
            on_change: function() {
                let student = frappe.query_report.get_filter_value('student');
                if (student) {
                    // Fetch the Student document
                    frappe.db.get_doc('Student', student).then(doc => {
                        // Auto-populate college and programme
                        frappe.query_report.set_filter_value('college', doc.company);
                        frappe.query_report.set_filter_value('programme', doc.programme);
                    });
                } else {
                    // Clear values if no student is selected
                    frappe.query_report.set_filter_value('college', '');
                    frappe.query_report.set_filter_value('programme', '');
                }
            }
        },
        {
            fieldname: "college",
            label: __("College"),
            fieldtype: "Link",
            options: "Company"
        },
        {
            fieldname: "programme",
            label: __("Programme"),
            fieldtype: "Link",
            options: "Programme"
        },
       
        {
            fieldname: "semester",
            label: __("Semester"),
            fieldtype: "Link",
            options: "Semester"
        }
    ]
};
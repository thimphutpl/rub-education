// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Attendance", {
    programme: function (frm) { fetch_students(frm); },
    year: function (frm) { fetch_students(frm); },
    semester: function (frm) { fetch_students(frm); },
    refresh(frm) {
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Mark Attendance'), function () {

                // Show popup
                frappe.prompt([
                    {
                        label: 'Student',
                        fieldname: 'student',
                        fieldtype: 'Link',
                        options: 'Student',
                        reqd: 1
                    },
                    {
                        label: 'Status',
                        fieldname: 'status',
                        fieldtype: 'Select',
                        options: 'Present\nAbsent\nOn Leave',
                        reqd: 1
                    }
                ],
                    function (values) {
                        let row = frm.doc.attendance_list.find(d => d.student === values.student);
                        if (row) {
                            row.status = values.status;
                            frm.refresh_field("attendance_list");
                            frappe.msgprint(__('Attendance updated for {0}: {1}', [row.student_name, values.status]));
                        } else {
                            frappe.msgprint(__('Student not found in Attendance List'));
                        }
                    },
                    __('Mark Attendance'),
                    __('Submit')
                );
            });
        }
    }
});


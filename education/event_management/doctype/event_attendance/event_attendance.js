// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Attendance", {
    programme: function (frm) { fetch_students(frm); },
    year: function (frm) { fetch_students(frm); },
    semester: function (frm) { fetch_students(frm); },
    refresh(frm) {
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Mark Attendance'), function () {
                let existing_students = frm.doc.attendance_list.map(d => d.student);

                frappe.prompt([
                    {
                        label: 'Student',
                        fieldname: 'student',
                        fieldtype: 'Link',
                        options: 'Student',
                        reqd: 1,
                        get_query: function () {
                            return {
                                filters: {
                                    name: ['in', existing_students],
                                    company: frm.doc.college
                                }
                            };
                        }
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
                        let row = frm.doc.attendance_list.find(d => String(d.student).trim() === String(values.student).trim());
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


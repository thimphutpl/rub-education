frappe.ui.form.on("Faculty Attendance", {
    refresh(frm) {
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Mark Attendance'), function () {

                let existing_faculty = frm.doc.faculty_attendance_list.map(d => d.faculty);

                frappe.prompt([
                    {
                        label: 'Employee',
                        fieldname: 'employee',
                        fieldtype: 'Link',
                        options: 'Employee',
                        reqd: 1,
                        get_query: function () {
                            return {
                                filters: {
                                    name: ['in', existing_faculty],
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
                        // ✅ Use values.employee, not values.faculty
                        let row = frm.doc.faculty_attendance_list.find(d => String(d.faculty).trim() === String(values.employee).trim());

                        if (row) {
                            row.status = values.status;
                            frm.refresh_field("faculty_attendance_list");
                            frappe.msgprint(__('Attendance updated for {0}: {1}', [row.faculty_name, values.status]));
                        } else {
                            frappe.msgprint(__('Faculty not found in Attendance List'));
                        }
                    },
                    __('Mark Attendance'),
                    __('Submit'));
            });
        }
    }
});
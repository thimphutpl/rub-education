frappe.ui.form.on("Events", {
    refresh(frm) {


        frm.call("has_attendance").then((r) => {
            if (!r.message.has_attendance) {
                if (frm.doc.docstatus === 1) {
                    frm.add_custom_button(
                        __("Create Attendance"),
                        function () {
                            frm.events.create_attendace(frm);
                        },
                    );

                }
            } else {
                if (frm.doc.name) {
                    frm.add_custom_button(__('View Attendance'), function () {
                        frappe.set_route('List', 'Event Attendance', {
                            concept_note: frm.doc.name
                        });
                    });
                }
            }

        });

    },

    create_attendace: function (frm) {
        let method = "education.event_management.doctype.event_attendance.event_attendance.create_attendance";
        return frappe.call({
            method: method,
            args: {
                dt: frm.doc.doctype,
                dn: frm.doc.name,
            },
            callback: function (r) {
                if (r.message && r.message.attendance_name) {
                    frappe.msgprint("Attendance created.");
                    frappe.set_route("List", "Event Attendance", r.message.attendance_name);
                } else {
                    frappe.msgprint("No attendance records created.");
                }
            },
        });
    },


    get_all_faculty(frm) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "User",
                limit_page_length: 1000,
                fields: ["name", "email", "full_name"]
            },
            callback: function (r) {
                if (r.message && r.message.length) {
                    frm.doc._all_faculty = r.message;
                    reload_faculty_rows(frm);
                }
            }
        });
    },


});

function reload_faculty_rows(frm) {
    frm.clear_table("event_register");

    let faculty_to_show = frm.doc._all_faculty.slice(0);
    faculty_to_show.forEach(emp => {
        let row = frm.add_child("event_register");
        row.faculty_name = emp.name;
        row.faculty_email = emp.email;
        row.faculty = emp.full_name;
    });

    frm.refresh_field("event_register");
}



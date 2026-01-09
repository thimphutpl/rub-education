frappe.ui.form.on("Events", {
    onload_post_render: function (frm) {
        if (frm.is_new() && !frm.doc.college) {
            frappe.call({
                method: "education.event_management.doctype.events.events.get_student_college",
                callback: function (r) {
                    if (r.message) {
                        frm.set_value("college", r.message);
                        frm.refresh_field("college");
                        frm.set_df_property("college", "read_only", 1);
                    }
                }
            });
        }
    },
    onload: function (frm) {
        frm.set_df_property("external_participant", "hidden", 1);
        frm.set_df_property("external_participant", "reqd", 0);
        frm.set_df_property("full_paper", "hidden", 1);
        frm.set_df_property("full_paper", "reqd", 0);

    },
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
                            student: frm.doc.name
                        });
                    });
                }
            }

        });
        toggle_culture_agenda(frm);



    },
    event_type: function (frm) {
        toggle_culture_agenda(frm);
        toggle_full_paper(frm)
    },


    create_attendace: function (frm) {
        let method = "education.event_management.doctype.event_attendance.event_attendance.create_attendance";
        frappe.dom.freeze("Please wait. Creating Attendance...", true);
        return frappe.call({
            method: method,
            args: {
                dt: frm.doc.doctype,
                dn: frm.doc.name,
            },
            callback: function (r) {
                if (r.message && r.message.attendance_name) {
                    frappe.msgprint("Successfully Attendance created.");
                    frappe.set_route("List", "Event Attendance", r.message.attendance_name);
                } else {
                    frappe.msgprint("No attendance records created.");
                }
            },
            always: function () {
                setTimeout(() => {
                    frappe.dom.unfreeze();
                }, 500);
            }
        });
    },

    guest__external_participant: function (frm) {
        if (frm.doc.guest__external_participant) {
            frm.set_df_property("external_participant", "hidden", 0);
            frm.set_df_property("external_participant", "reqd", 1);
        } else {
            frm.set_df_property("external_participant", "hidden", 1);
            frm.set_df_property("external_participant", "reqd", 0);
            frm.clear_table("external_participant");
        }
        frm.refresh_field("external_participant");
    },

    get_all_faculty(frm) {
        frappe.dom.freeze("Please wait. Fetching Faculty...", true);
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "User",
                fields: ["name", "email", "full_name"],
            },
            callback: function (r) {
                if (r.message && r.message.length) {
                    frm.doc._all_faculty = r.message;
                    reload_faculty_rows(frm);
                }
            },
            always: function () {
                setTimeout(() => {
                    frappe.dom.unfreeze();
                }, 500);
            },
        });
    },

    get_all_student(frm) {
        frappe.dom.freeze("Please wait. Fetching Students...", true);

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Student",
                fields: ["name", "student_email_id", "first"],
            },
            callback: function (r) {
                if (r.message && r.message.length) {
                    frm.doc._all_student = r.message;
                    reload_student_rows(frm);
                }
            },
            always: function () {
                setTimeout(() => {
                    frappe.dom.unfreeze();
                }, 500);
            }
        });
    },
    get_student: function (frm) {
        frappe.dom.freeze("Please wait. Fetching Students...", true);

        if (!frm.doc.student_filter || frm.doc.student_filter.length === 0) {
            frappe.msgprint("Please Select Class");
            frappe.dom.unfreeze();
            return;
        }

        // Clear previous _all_student array and student_register
        frm.doc._all_student = [];
        frm.clear_table("student_register");

        // Count how many rows to process
        let rows_to_process = frm.doc.student_filter.length;
        let processed_rows = 0;

        frm.doc.student_filter.forEach(function (row) {
            if (row.programme && row.year && row.semester) {
                let programme_list = Array.isArray(row.programme) ? row.programme : row.programme.split(",");

                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Student",
                        filters: [
                            ["programme", "in", programme_list],
                            ["year", "=", row.year],
                            ["semester", "=", row.semester],
                            ["status", "=", "Active"]
                        ],
                        fields: ["name", "student_email_id", "first_name", "last_name"]
                    },
                    callback: function (r) {
                        if (r.message && r.message.length) {
                            frm.doc._all_student = frm.doc._all_student.concat(r.message);
                        }

                        // After processing all rows, reload student_register
                        processed_rows++;
                        if (processed_rows === rows_to_process) {
                            reload_student_rows(frm);
                        }
                    },
                    always: function () {
                        setTimeout(() => {
                            frappe.dom.unfreeze();
                        }, 500);
                    },
                });
            } else {
                frappe.msgprint("Please select Programme(s), Year, and Semester in all filter rows.");
                frappe.dom.unfreeze();
                processed_rows++;
            }
        });
    }

});



function reload_faculty_rows(frm) {
    frm.clear_table("faculty_register");
    let faculty_to_show = frm.doc._all_faculty.slice(0);
    faculty_to_show.forEach(emp => {
        let row = frm.add_child("faculty_register");
        row.faculty = emp.name;
        row.faculty_email = emp.email;
        row.faculty_name = emp.full_name;
    });

    frm.refresh_field("faculty_register");
}


function reload_student_rows(frm) {
    frm.clear_table("student_register");
    let student_to_show = frm.doc._all_student.slice(0);
    student_to_show.forEach(std => {
        let row = frm.add_child("student_register");
        row.student = std.name;
        row.student_email = std.student_email_id;
        row.student_name = std.first_name + " " + std.last_name;

    });
    frm.refresh_field("student_register");
}

function toggle_culture_agenda(frm) {
    if (frm.doc.event_type === "Cultural") {
        frm.toggle_display('culture_agenda', true);
        frm.toggle_display('event_agenda', false)
    } else {
        frm.toggle_display('event_agenda', true)
        frm.toggle_display('culture_agenda', false);
    }
}
function toggle_full_paper(frm) {
    if (frm.doc.event_type === "Conference") {
        frm.set_df_property("agenda_section", "hidden", 1);
        frm.set_df_property("culture_agenda", "hidden", 1);
        frm.set_df_property("registration_type", "hidden", 1);
        frm.set_df_property("full_paper", "hidden", 0)
        frm.set_df_property("full_paper", "reqd", 1)
    } else if (frm.doc.event_type === "Cultural") {
        frm.set_df_property("event_agenda", "hidden", 1);
        frm.set_df_property("culture_agenda", "hidden", 0);
        frm.set_df_property("registration_type", "hidden", 0);
        frm.set_df_property("full_paper", "hidden", 1);
        frm.set_df_property("full_paper", "reqd", 0);
    } else {
        frm.set_df_property("event_agenda", "hidden", 0);
        frm.set_df_property("culture_agenda", "hidden", 1);
        frm.set_df_property("registration_type", "hidden", 0);
        frm.set_df_property("full_paper", "hidden", 1);
        frm.set_df_property("full_paper", "reqd", 0);
    }
}






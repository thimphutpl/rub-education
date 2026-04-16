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
        frm.trigger("event_type");
        frm.trigger("type");
        forward_to_filter(frm);
        room_filter(frm);
        // student_filter(frm);
        // employee_filter(frm);
        faculty_register_filter(frm);
        student_register_filter(frm);
        setup_equipment_filter(frm);
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

        frm.call("has_faculty_attendance").then((r) => {
            // if (frappe.user.has_role("Student")) {
            //     return;
            // }

            if (!r.message.has_faculty_attendance) {
                if (frm.doc.docstatus === 1) {
                    frm.add_custom_button(
                        __("Create Faculty Attendance"),
                        function () {
                            frm.events.create_faculty_attendace(frm);
                        },
                    );

                }
            } else {
                if (frm.doc.name) {
                    frm.add_custom_button(__('View Faculty Attendance'), function () {
                        frappe.set_route('List', 'Faculty Attendance', {
                            student: frm.doc.name
                        });
                    });
                }
            }

        });
        // toggle_agenda(frm);
        // toggle_full_paper(frm);

        if (frm.fields_dict["student_filter"]) {
            frm.fields_dict["student_filter"].grid.get_field("programme").get_query =
                function (doc, cdt, cdn) {
                    if (!frm.doc.college) {
                        return { filters: { name: ["=", ""] } };
                    }
                    return {
                        query: "education.event_management.doctype.events.events.get_programmes_by_college",
                        filters: { college: frm.doc.college }
                    };
                };
        }

        if (frappe.user.has_role("Employee")) {

            if (!frm.doc.college) { // only set if empty
                frappe.db.get_value('Employee', { user_id: frappe.session.user }, ['company'])
                    .then(r => {
                        if (r.message && r.message.company) {
                            frm.set_value('college', r.message.company);
                            frm.set_df_property('college', 'read_only', 1);
                        }
                    });
            }

        } else if (frappe.user.has_role("Student")) {

            frappe.db.get_value('Student', { user: frappe.session.user }, ['company'])
                .then(r => {
                    if (r.message && r.message.company) {
                        frm.set_value('college', r.message.company);
                    }
                });

        }

    },
    setup:function(frm){
        const filterByCollege=()=>{
            if(!frm.doc.college){
                alert("College is required")
            }
            return{
                filters:{
                    "company":frm.doc.college
                }
            }
        };
        frm.set_query("student",filterByCollege);
        frm.set_query("employee",filterByCollege);
    },
    college(frm) {
        if (!frm.doc.college) {
            frm.set_value("room", null);
            frm.set_value("forward_to", null);
            frm.set_value("event_equipment", null);
            frm.set_value("employee", null);
            frm.set_value("student", null);
            frm.clear_table("faculty_register", null);
            frm.clear_table("student_register", null);

        }

        setup_equipment_filter(frm);
        forward_to_filter(frm);
        room_filter(frm);
        faculty_register_filter(frm);
        student_register_filter(frm);

        if (frm.fields_dict.event_equipment) {
            frm.fields_dict.event_equipment.grid.refresh();
        }
        if (frm.fields_dict.faculty_register) {
            frm.fields_dict.faculty_register.grid.refresh();
        }
        if (frm.fields_dict.student_register) {
            frm.fields_dict.student_register.grid.refresh();
        }
    },
    type: function (frm) {
        frm.set_df_property("student", "hidden", 1);
        frm.set_df_property("employee", "hidden", 1);
        frm.set_df_property("student", "reqd", 0);
        frm.set_df_property("employee", "reqd", 0);
        if (frm.doc.type === "Student") {
            frm.set_df_property("employee", "hidden", 1);
            frm.set_df_property("student", "hidden", 0);
            frm.set_df_property("student", "reqd", 1);
            frm.set_df_property("forward_to", "reqd", 1);
        } else if (frm.doc.type === "Staff") {
            frm.set_df_property("student", "hidden", 1);
            frm.set_df_property("employee", "hidden", 0);
            frm.set_df_property("employee", "reqd", 1);
            frm.set_df_property("forward_to", "reqd", 1);
        }
    },
    event_type: function (frm) {
        if (frm.doc.event_type === "Conference") {
            frm.set_df_property("event_agenda", "hidden", 1);
            frm.set_df_property("registration_type", "hidden", 1);

            frm.set_df_property("conference_theme", "hidden", 0);
            frm.set_df_property("conference_theme", "reqd", 1);

        } else {
            // For any other Event Type
            frm.set_df_property("event_agenda", "hidden", 0);
            frm.set_df_property("registration_type", "hidden", 0);

            frm.set_df_property("conference_theme", "hidden", 1);
            frm.set_df_property("conference_theme", "reqd", 0);
        }
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

    create_faculty_attendace: function (frm) {
        let method = "education.event_management.doctype.faculty_attendance.faculty_attendance.create_attendance";
        frappe.dom.freeze("Please wait. Creating Faculty Attendance...", true);
        return frappe.call({
            method: method,
            args: {
                dt: frm.doc.doctype,
                dn: frm.doc.name,
            },
            callback: function (r) {
                if (r.message && r.message.attendance_name) {
                    frappe.msgprint("Successfully Attendance created.");
                    frappe.set_route("List", "Faculty Attendance", r.message.attendance_name);
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
        if (!frm.doc.college) {
            frappe.msgprint("Please select College first.");
            return;
        }

        frappe.dom.freeze("Please wait. Fetching Faculty...", true);

        frappe.call({
            method: "education.event_management.doctype.events.events.get_faculty_by_college",
            args: { college: frm.doc.college },
            callback: function (r) {
                if (r.message && r.message.length) {
                    frm.doc._all_faculty = r.message;
                    reload_faculty_rows(frm);
                } else {
                    frappe.msgprint("No faculty found for the selected college.");
                }
            },
            always: function () {
                setTimeout(() => frappe.dom.unfreeze(), 500);
            }
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

        frm.doc._all_student = [];
        frm.clear_table("student_register");

        frappe.call({
            method: "education.event_management.doctype.events.events.get_students_by_filters",
            args: {
                filters: frm.doc.student_filter,
            },
            callback: function (r) {
                if (r.message && r.message.length) {
                    frm.doc._all_student = r.message;
                    reload_student_rows(frm);
                } else {
                    frappe.msgprint("No students found with the selected filters.");
                }
            },
            always: function () {
                setTimeout(() => {
                    frappe.dom.unfreeze();
                }, 500);
            }
        });
    }

});

function setup_equipment_filter(frm) {
    if (!frm.doc.college) return;

    frm.set_query("equipment", "event_equipment", function (doc, cdt, cdn) {
        return {
            filters: {
                company: frm.doc.college
            }
        };
    });
}
function faculty_register_filter(frm) {
    if (!frm.doc.college) return;

    frm.set_query("faculty_email", "faculty_register", function (doc, cdt, cdn) {
        return {
            filters: {
                company: frm.doc.college
            }
        };
    });
}
function student_filter(frm) {
    if (!frm.doc.college) return;

    frm.set_query("student", "student_register", function (doc, cdt, cdn) {
        return {
            filters: {
                company: frm.doc.college
            }
        };
    });
}
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


function forward_to_filter(frm) {
    if (!frm.doc.college) return;
    frm.set_query("forward_to", function () {
        return {
            filters: {
                company: frm.doc.college,
                // role: "Event Approval"
            }
        };
    });
}

function room_filter(frm) {
    if (!frm.doc.college) return;
    frm.set_query("room", function () {
        return {
            filters: {
                company: frm.doc.college
            }
        };
    });
}
// function student_filter(frm) {
//     if (!frm.doc.college) return;
//     frm.set_query("student", function () {
//         return {
//             filters: {
//                 company: frm.doc.college
//             }
//         };
//     });
// }
// function employee_filter(frm) {
//     if (!frm.doc.college) return;
//     frm.set_query("employee", function () {
//         return {
//             filters: {
//                 company: frm.doc.college
//             }
//         };
//     });
// }
function student_register_filter(frm) {
    if (!frm.doc.college) return;
    frm.set_query("student", "student_register", function (doc, cdt, cdn) {
        return {
            filters: {
                company: frm.doc.college
            }
        };
    });
}

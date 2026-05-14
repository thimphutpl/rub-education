frappe.ui.form.on("Exam Timetable", {
    refresh(frm) {
        // Add custom buttons
        frm.add_custom_button(__("Upload File"), () => frm.events.upload_file(frm))
            .addClass("btn-dark");
        
        frm.add_custom_button(__("View Report"), () => frm.events.view_report(frm))
            .addClass("btn-dark");
    },

    // Get Student button click handler
    get_student(frm) {
        if (frm.is_new()) {
            frappe.msgprint(__("Please save the document before fetching students."));
            return;
        }

        // Get values directly from form fields
        const college = frm.doc.college;
        const academic_year = frm.doc.academic_year;
        const academic_term = frm.doc.academic_term;

        // Collect all modules from child table exam_module
        const modules = (frm.doc.exam_module || [])
            .map(row => row.module)
            .filter(m => m);

        // Validate required fields
        if (!college || !academic_year || !academic_term) {
            frappe.msgprint(__("Please ensure College, Academic Year, and Academic Term are filled in before fetching students."));
            return;
        }

        if (modules.length === 0) {
            frappe.msgprint(__("No modules found in Exam Module table."));
            return;
        }

        // Fetch students for each module
        const fetchNext = (index = 0) => {
            if (index >= modules.length) {
                frappe.msgprint(__("Students added successfully for all modules."));
                frm.refresh_field("exam_timetable_student");
                frm.trigger("validate_capacity");
                return;
            }

            const module = modules[index];

            frappe.call({
                method: "education.examination.doctype.exam_timetable.exam_timetable.get_students",
                args: {
                    college: college,
                    academic_year: academic_year,
                    academic_term: academic_term,
                    module: module,
                    docname: frm.doc.name
                },
                freeze: true,
                freeze_message: __("Fetching Students for Module: {0}...", [module]),
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        frappe.msgprint(__("{0} students added for Module: {1}", [r.message.length, module]));
                        frm.reload_doc();
                    } else {
                        frappe.msgprint(__("No students found in Module Enrolment for Module: {0}", [module]));
                    }
                    fetchNext(index + 1);
                },
                error: function(err) {
                    frappe.msgprint(__("Error fetching students for Module: {0}.", [module]));
                    console.error(err);
                }
            });
        };
        
        fetchNext();
    },

    upload_file(frm) {
        if (frm.is_new()) {
            frappe.msgprint(__("Please save the document before uploading the Excel file."));
            return;
        }

        frappe.prompt([
            {
                fieldname: "excel_file",
                fieldtype: "Attach",
                label: "Select Excel File",
                reqd: 1,
            }
        ], (data) => {
            frappe.call({
                method: "education.examination.doctype.exam_timetable.exam_timetable.upload_excel",
                args: {
                    file_url: data.excel_file,
                    docname: frm.doc.name,
                },
                freeze: true,
                freeze_message: __("Uploading and Processing Excel..."),
                callback: function(r) {
                    if (r.message && !r.exc) {
                        frappe.msgprint(r.message.message || __("Excel data has been imported successfully!"));
                        frm.reload_doc();
                    }
                },
            });
        }, __("Upload Excel File"), __("Upload"));
    },

    view_report(frm) {
        if (frm.is_new()) {
            frappe.msgprint(__("Please save the document before viewing the report."));
            return;
        }
        frappe.set_route("examtimetable-report", {"docname": frm.doc.name});
    },

    // Real-time validations
    start_time: function(frm) {
        if (frm.doc.start_time && frm.doc.end_time && frm.doc.room && frm.doc.exam_date) {
            frm.trigger("check_hall_availability");
        }
        if (frm.doc.start_time && frm.doc.end_time && frm.doc.exam_date) {
            frm.trigger("validate_student_allocation");
        }
    },

    end_time: function(frm) {
        if (frm.doc.start_time && frm.doc.end_time && frm.doc.room && frm.doc.exam_date) {
            frm.trigger("check_hall_availability");
        }
        if (frm.doc.start_time && frm.doc.end_time && frm.doc.exam_date) {
            frm.trigger("validate_student_allocation");
        }
    },

    room: function(frm) {
        if (frm.doc.room && frm.doc.start_time && frm.doc.end_time && frm.doc.exam_date) {
            frm.trigger("check_hall_availability");
        }
    },

    exam_date: function(frm) {
        if (frm.doc.room && frm.doc.start_time && frm.doc.end_time && frm.doc.exam_date) {
            frm.trigger("check_hall_availability");
        }
        if (frm.doc.start_time && frm.doc.end_time && frm.doc.exam_date) {
            frm.trigger("validate_student_allocation");
        }
    },

    check_hall_availability: function(frm) {
        if (!frm.doc.room || !frm.doc.exam_date || !frm.doc.start_time || !frm.doc.end_time) {
            return;
        }

        frappe.call({
            method: "education.examination.doctype.exam_timetable.exam_timetable.check_hall_availability",
            args: {
                room: frm.doc.room,
                exam_date: frm.doc.exam_date,
                start_time: frm.doc.start_time,
                end_time: frm.doc.end_time,
                current_docname: frm.doc.name
            },
            callback: function(r) {
                if (r.message && !r.message.available) {
                    frappe.msgprint({
                        title: __("Hall Not Available"),
                        message: r.message.message,
                        indicator: "red"
                    });
                }
            }
        });
    },

    validate_student_allocation: function(frm) {
        const students = frm.doc.exam_timetable_student || [];
        if (students.length === 0 || !frm.doc.exam_date || !frm.doc.start_time || !frm.doc.end_time) {
            return;
        }

        const studentToCheck = students[0]?.student;
        if (!studentToCheck) return;

        frappe.call({
            method: "education.examination.doctype.exam_timetable.exam_timetable.check_student_availability",
            args: {
                student: studentToCheck,
                exam_date: frm.doc.exam_date,
                start_time: frm.doc.start_time,
                end_time: frm.doc.end_time,
                current_docname: frm.doc.name
            },
            callback: function(r) {
                if (r.message && !r.message.available) {
                    frappe.msgprint({
                        title: __("Student Conflict Warning"),
                        message: r.message.message,
                        indicator: "orange"
                    });
                }
            }
        });
    },

    validate_capacity: function(frm) {
        if (frm.doc.capacity && frm.doc.exam_timetable_student) {
            const total_students = frm.doc.exam_timetable_student.length;
            const capacity = parseInt(frm.doc.capacity);
            
            if (total_students > capacity) {
                frappe.msgprint({
                    title: __("Capacity Exceeded"),
                    message: __("Number of students ({0}) exceeds the capacity ({1}).", [total_students, capacity]),
                    indicator: "red"
                });
            }
        }
    },

    exam_timetable_student_add: function(frm) {
        frm.trigger("validate_capacity");
    },

    exam_timetable_student_remove: function(frm) {
        frm.trigger("validate_capacity");
    },

    capacity: function(frm) {
        frm.trigger("validate_capacity");
    }
});
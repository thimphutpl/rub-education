// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Continuous Assessment Entry", {
    setup(frm) {
        frm.set_query("module_enrollment_key", function () {
            return {
                filters: {
                    academic_term: frm.doc.academic_term,
                    module: frm.doc.enrollment_date,
                    docstatus: 1,
                },
            };
        });

        frm.set_query("college", function () {
            return {
                filters: {
                    is_group: 0,
                    name: ["!=", "Office of Vice Chancellor"],
                },
            };
        });

        frm.set_query("programme", function () {
            return {
                query: "education.education.doctype.module_enrolment_tool.module_enrolment_tool.get_programme",
                filters: {
                    college: frm.doc.college,
                    date: frm.doc.posting_date,
                    validate: 1,
                },
            };
        });

        frm.set_query("tutor", function () {
            return {
                query: "erpnext.controllers.queries.filter_module_tutors",
                filters: {
                    college: frm.doc.college,
                    programme: frm.doc.programme,
                    module: frm.doc.module,
                },
            };
        });

        frm.set_query("assessment_component", function () {
            return {
                query: "erpnext.controllers.queries.filter_assessment_component",
                filters: {
                    college: frm.doc.college,
                    programme: frm.doc.programme,
                    module: frm.doc.module,
                    tutor: frm.doc.tutor,
                    academic_term: frm.doc.academic_term,
                    examination_assesment: 0,
                },
            };
        });
    },

    refresh(frm) {
        frm.set_df_property("items", "cannot_add_rows", true);

        frm.set_query("course", function () {
            return {
                query: "education.education.doctype.program_enrollment.program_enrollment.get_program_courses",
                filters: {
                    program: frm.doc.programme,
                    college: frm.doc.college,
                    semester: frm.doc.semester,
                    validate: 1,
                },
            };
        });

        frm.set_query("module", function () {
            return {
                query: "education.education.doctype.program_enrollment.program_enrollment.get_program_courses",
                filters: {
                    program: frm.doc.programme,
                    college: frm.doc.college,
                    semester: frm.doc.semester,
                    validate: 1,
                },
            };
        });
    },

    college(frm) {
        frm.set_query("programme", function () {
            return {
                query: "education.education.doctype.module_enrolment_tool.module_enrolment_tool.get_programme",
                filters: {
                    college: frm.doc.college,
                    date: frm.doc.posting_date,
                    validate: 1,
                },
            };
        });

        frm.set_query("course", function () {
            return {
                query: "education.education.doctype.program_enrollment.program_enrollment.get_program_courses",
                filters: {
                    program: frm.doc.programme,
                    college: frm.doc.college,
                    semester: frm.doc.semester,
                    validate: 1,
                },
            };
        });
    },

    academic_term(frm) {
        // Hook retained for future use
    },

    exam_type(frm) {
        exam_registration_filter(frm);
    },

    get_students(frm) {
        frappe.call({
            method: "education.academic_management.doctype.continuous_assessment_entry.continuous_assessment_entry.get_students",
            args: {
                doc: frm.doc,
                module_enrolment_key: frm.doc.module_enrolment_key,
            },
            callback: function (r) {
                if (!r.message) return;

                frm.clear_table("items");

                r.message.forEach((student) => {
                    const row = frm.add_child("items");
                    row.student = student.student;
                    row.student_name = student.student_name;
                });

                frm.refresh_field("items");
            },
        });
    },
});


function exam_registration_filter(frm) {
    frm.set_query("examination_registration", function () {
        if (frm.doc.exam_type === "Exam Re-Assessment") {
            return { filters: { reassesment: 1 } };
        } else if (frm.doc.exam_type === "Semester End Examination") {
            return { filters: { reassesment: 0 } };
        } else {
            return { filters: { reassesment: ["!=", 2] } };
        }
    });
}
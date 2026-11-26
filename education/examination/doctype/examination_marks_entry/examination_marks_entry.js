// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Marks Entry", {
    onload(frm) {
        if (!frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.now_date());
        }
        if (!frm.doc.college || !frm.doc.tutor) {
            set_company_from_user(frm);
        }
    },

    setup(frm) {
        frm.set_query("module_enrolment_key", () => ({
            filters: {
                college: frm.doc.college,
                docstatus: 1,
            },
        }));

        frm.set_query("college", () => ({
            filters: {
                is_group: 0,
                name: ["!=", "Office of Vice Chancellor"],
            },
        }));

        frm.set_query("programme", () => ({
            query:
                "education.education.doctype.module_enrolment_tool.module_enrolment_tool.get_programme",
            filters: {
                college: frm.doc.college,
                date: frm.doc.posting_date,
                validate: 1,
            },
        }));

        frm.set_query("assessment_component", () => ({
            query: "erpnext.controllers.queries.filter_assessment_component",
            filters: {
                college: frm.doc.college,
                programme: frm.doc.programme,
                module: frm.doc.module,
                academic_term: frm.doc.academic_term,
                examination_assesment: 1,
            },
        }));
    },

    refresh(frm) {
        frm.set_df_property("items", "cannot_add_rows", true);
        set_module_field_visibility(frm);
    },

    // NOTE: semester is intentionally NOT set here — it's not on MEK.
    module_enrolment_key(frm) {
        if (!frm.doc.module_enrolment_key) return;

        frappe.db
            .get_doc("Module Enrolment Key", frm.doc.module_enrolment_key)
            .then((mek) => {
                const fields = [
                    "college",
                    "tutor",
                    "programme",
                    "academic_year",
                    "academic_term",
                    "module",
                ];
                fields.forEach((f) => {
                    if (mek[f]) frm.set_value(f, mek[f]);
                });

                if (mek.tutor) {
                    frappe.db
                        .get_value("Employee", mek.tutor, "employee_name")
                        .then((r) => {
                            if (r.message && r.message.employee_name) {
                                frm.set_value(
                                    "tutor_name",
                                    r.message.employee_name
                                );
                            }
                        });
                }

                fetch_weightage(frm);
            });
    },

    academic_term(frm) {
        // semester is user-driven; do NOT auto-clear unless you want to
        fetch_weightage(frm);
    },

    programme(frm) {
        fetch_weightage(frm);
    },

    module(frm) {
        fetch_weightage(frm);
    },

    assessment_component(frm) {
        fetch_weightage(frm);
    },

    exam_type(frm) {
        set_module_field_visibility(frm);
        if (frm.doc.exam_type === "Semester End Examination") {
            frm.set_value("examination_registration", null);
        }
        fetch_weightage(frm);
    },

    get_students(frm) {
        const required = [
            "assessment_component",
            "academic_year",
            "academic_term",
            "college",
            "tutor",
        ];
        if (frm.doc.exam_type === "Semester End Examination") {
            required.push("module", "module_enrolment_key", "semester");
        } else if (frm.doc.exam_type) {
            required.push("examination_registration");
        }

        for (const field of required) {
            if (!frm.doc[field]) {
                frappe.msgprint(
                    __("Please select {0}", [
                        __(frappe.model.unscrub(field)),
                    ])
                );
                return;
            }
        }

        frappe.call({
            method:
                "education.examination.doctype.examination_marks_entry.examination_marks_entry.get_students",
            args: {
                doc: frm.doc,
                examination_registration:
                    frm.doc.examination_registration || null,
            },
            freeze: true,
            freeze_message: __("Fetching students..."),
            callback(r) {
                if (!r.message) return;

                const students = r.message;
                if (!students.length) {
                    frappe.msgprint(
                        __("No students found for the selected criteria")
                    );
                    return;
                }

                students.sort((a, b) =>
                    (a.student_name || "").localeCompare(
                        b.student_name || "",
                        undefined,
                        { sensitivity: "base" }
                    )
                );

                frm.clear_table("items");
                students.forEach((s) => {
                    const row = frm.add_child("items");
                    row.student = s.student;
                    row.student_name = s.student_name;
                    row.programme = s.programme || frm.doc.programme;
                    row.examination_review_link =
                        s.review_name || null;
                });
                frm.refresh_field("items");

                frappe.show_alert(
                    {
                        message: __("Fetched {0} students", [students.length]),
                        indicator: "green",
                    },
                    5
                );
            },
        });
    },
});


// ----------------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------------
function set_module_field_visibility(frm) {
    if (!frm.doc.exam_type) return;

    const isSEE = frm.doc.exam_type === "Semester End Examination";
    frm.set_df_property("module", "reqd", isSEE ? 1 : 0);
    frm.set_df_property("module", "hidden", 0);
    frm.set_df_property("examination_registration", "hidden", isSEE ? 1 : 0);
    frm.set_df_property("examination_registration", "reqd", 0);
}

function set_company_from_user(frm) {
    frappe.db
        .get_value(
            "Employee",
            { user_id: frappe.session.user },
            ["company", "name"]
        )
        .then((r) => {
            if (r.message) {
                if (!frm.doc.college) {
                    frm.set_value("college", r.message.company);
                }
                if (!frm.doc.tutor) {
                    frm.set_value("tutor", r.message.name);
                }
            }
        });
}

function fetch_weightage(frm) {
    const required = [
        "college",
        "academic_term",
        "programme",
        "module",
        "assessment_component",
    ];
    for (const f of required) {
        if (!frm.doc[f]) return;
    }

    frappe.call({
        method:
            "education.examination.doctype.examination_marks_entry.examination_marks_entry.get_weightage",
        args: {
            college: frm.doc.college,
            academic_term: frm.doc.academic_term,
            programme: frm.doc.programme,
            module: frm.doc.module,
            assessment_component: frm.doc.assessment_component,
        },
        callback(r) {
            if (r && r.message !== undefined && r.message !== null) {
                frm.set_value("weightage", r.message);
            }
        },
    });
}
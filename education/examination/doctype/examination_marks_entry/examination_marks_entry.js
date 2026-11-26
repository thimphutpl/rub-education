// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Marks Entry", {
    onload(frm) {
        if (!frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.now_date());
        }
        if (!frm.doc.company) {
            set_company_from_user(frm);
        }
    },

    setup(frm) {
        frm.set_query("module_enrolment_key", () => ({
            filters: { college: frm.doc.college },
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

    academic_term(frm) {
        frm.set_value("semester", "");
    },

    exam_type(frm) {
        set_module_field_visibility(frm);
        if (frm.doc.exam_type === "Semester End Examination") {
            frm.set_value("examination_registration", null);
        }
    },

    get_students(frm) {
        const required = [
            "assessment_component", "academic_year", "academic_term",
            "college", "semester", "tutor",
        ];
        if (frm.doc.exam_type === "Semester End Examination") {
            required.push("module");
        }

        for (const field of required) {
            if (!frm.doc[field]) {
                frappe.msgprint(
                    __("Please select {0}", [__(frappe.model.unscrub(field))])
                );
                return;
            }
        }

        frappe.call({
            method:
                "education.examination.doctype.examination_marks_entry.examination_marks_entry.get_students",
            args: {
                examination_registration:
                    frm.doc.examination_registration || null,
                doc: frm.doc,
            },
            callback(r) {
                if (!r.message) return;

                const students = r.message;
                if (!students.length) {
                    frappe.msgprint(
                        __("No students found for the selected criteria")
                    );
                    return;
                }

                // ✅ Defensive sort (backend already sorts, but keeps UI stable)
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
                    row.programme = s.programme;
                    row.examination_review_link = s.review_name;
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

function set_module_field_visibility(frm) {
    if (!frm.doc.exam_type) return;

    const isSEE = frm.doc.exam_type === "Semester End Examination";
    frm.set_df_property("module", "reqd", isSEE ? 1 : 0);
    frm.set_df_property("module", "hidden", 0);
    frm.set_df_property("examination_registration", "hidden", isSEE ? 1 : 0);
    frm.set_df_property(
        "examination_registration",
        "reqd",
        isSEE ? 0 : 0
    );
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
                frm.set_value("college", r.message.company);
                frm.set_value("tutor", r.message.name);
            }
        });
}
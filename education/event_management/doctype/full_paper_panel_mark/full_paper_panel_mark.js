// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Full Paper Panel Mark", {
    onload_post_render: function (frm) {
        if (frm.doc.theme && (!frm.doc.full_paper_evaluation_criteria_full_paper || frm.doc.full_paper_evaluation_criteria_full_paper.length === 0)) {
            load_rubric_based_on_theme(frm);
        }
    },
    theme: function (frm) {
        load_rubric_based_on_theme(frm);
    },
    validate: function (frm) {
        frm.doc.full_paper_evaluation_criteria_full_paper.forEach(function (row, idx) {
            // Ensure weight_marks is a number
            let weight = parseFloat(row.weight_marks);

            if (isNaN(weight)) {
                frappe.throw(`Weight (Marks) in row ${idx + 1} must be a number.`);
            }

            // Example: validate max limit (e.g., score value)
            let max_score = parseFloat(row.score);
            if (weight > max_score) {
                frappe.throw(`Weight (Marks) in row "${row.criteria}" cannot exceed ${max_score}. You entered ${weight}`);
            }

            // Example: validate min limit
            if (weight < 0) {
                frappe.throw(`Weight (Marks) in row "${row.criteria}" cannot be negative.`);
            }
        });
    },
});

function load_rubric_based_on_theme(frm) {
    if (!frm.doc.theme) return;
    frm.clear_table("full_paper_evaluation_criteria_full_paper");
    frappe.call({
        method: "education.event_management.doctype.rubric_template_for_full_paper.rubric_template_for_full_paper.get_full_paper_rubric",
        args: {
            theme_name: frm.doc.theme
        },
        callback: function (r) {
            if (r.message && r.message.length) {

                r.message.forEach(row => {

                    let child = frm.add_child("full_paper_evaluation_criteria_full_paper");
                    child.criteria = row.criteria;
                    child.weight_marks = row.weight_marks;
                    child.remark = row.remark;

                });

                frm.refresh_field("full_paper_evaluation_criteria_full_paper");

            } else {
                frappe.msgprint("No active full paper rubric found for this theme.");
            }
        }
    });
}

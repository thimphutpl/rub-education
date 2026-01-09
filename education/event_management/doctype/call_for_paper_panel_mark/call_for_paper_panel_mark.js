// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Call For Paper Panel Mark", {
    onload_post_render: function (frm) {
        if (frm.doc.theme && (!frm.doc.panel_evaluation_criteria_call_for_paper || frm.doc.panel_evaluation_criteria_call_for_paper.length === 0)) {
            load_rubric_based_on_theme(frm);
        }
    },
    theme: function (frm) {
        load_rubric_based_on_theme(frm);
    },
    validate: function (frm) {
        frm.doc.panel_evaluation_criteria_call_for_paper.forEach(function (row, idx) {
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
    frm.clear_table("panel_evaluation_criteria_call_for_paper");
    frappe.call({
        method: "education.event_management.doctype.rubric_template_for_call_for_paper.rubric_template_for_call_for_paper.get_abstract_rubric",
        args: {
            theme_name: frm.doc.theme
        },
        callback: function (r) {
            if (r.message && r.message.length) {
                r.message.forEach(row => {
                    let child = frm.add_child("panel_evaluation_criteria_call_for_paper");
                    child.criteria = row.criteria;
                    child.score = row.score;
                });

                frm.refresh_field("panel_evaluation_criteria_call_for_paper");

            } else {
                frappe.msgprint("No active abstract rubric found for this theme.");
            }
        }
    });
}
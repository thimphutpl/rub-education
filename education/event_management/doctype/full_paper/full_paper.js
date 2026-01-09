// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Full Paper", {

    refresh: function (frm) {
        // Check if the user has already given marks
        frm.call("has_given_mark").then((r) => {
            if (!r.message.has_given_mark) {
                frm.toggle_display('give_marks', true);
                frm.toggle_display('view_marks', false);
            } else {
                frm.toggle_display('give_marks', false);
                frm.toggle_display('view_marks', true);
            }
        });

        // Update panel summary safely (use frm.doc + refresh_field)
        frm.call("update_panel_summary").then((r) => {
            if (!r.message) return;
            frm.doc.total_panel_member = r.message.total_panel_member;
            frm.doc.total_mark_submitted = r.message.total_mark_submitted;
            frm.doc.waiting_for_review = r.message.waiting_for_review;

            frm.refresh_field("total_panel_member");
            frm.refresh_field("total_mark_submitted");
            frm.refresh_field("waiting_for_review");
        });

        // Update total mark safely
        frm.call("calculate_total_mark").then((r) => {
            if (r.message !== undefined) {
                frm.doc.total_mark = r.message;
                frm.refresh_field("total_mark");
            }
        });

        // Fetch master evaluation criteria only if not already loaded
        if (!frm.doc.master_evaluation_criteria_full_paper || frm.doc.master_evaluation_criteria_full_paper.length === 0) {
            fetch_master_avg_marks(frm);
        }

        // Only allow certain roles to see summary fields and child table
        const allowed_roles = ["Administrator", "System Manager", "Super Admin"];
        const can_view = frappe.user_roles.some(role => allowed_roles.includes(role));
    

        frm.toggle_display("master_evaluation_criteria_full_paper", can_view);
        frm.toggle_display("total_panel_member", can_view);
        frm.toggle_display("total_mark_submitted", can_view);
        frm.toggle_display("waiting_for_review", can_view);
        frm.toggle_display("total_mark", can_view);
    },
    give_marks: function (frm) {
        frm.events.has_mark(frm);
    },

    has_mark: function (frm) {
        frappe.call({
            method: "education.event_management.doctype.full_paper_panel_mark.full_paper_panel_mark.get_conference_info",
            args: {
                source_doctype: frm.doc.doctype,
                source_name: frm.doc.name
            },
            callback: function (r) {
                if (r.message) {
                    frappe.set_route(
                        "Form",
                        r.message.doctype,
                        r.message.name
                    );
                }
            }
        });
    },
    view_marks: function (frm) {
        frm.call("has_given_mark").then(r => {
            if (r.message.has_given_mark) {
                frappe.set_route('Form', 'Full Paper Panel Mark', r.message);
            } else {
                frappe.msgprint("No Project Formulation Grant found for this record.");
            }
        });
    },
});

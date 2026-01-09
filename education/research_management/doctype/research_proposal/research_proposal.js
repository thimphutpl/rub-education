// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Research Proposal", {
    refresh(frm) {
        frm.fields_dict['researcher_details'].grid.get_field('student').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            return {
                filters: {
                    company: row.college 
                }
            };
        };
        frm.fields_dict['researcher_details'].grid.get_field('employee').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            return {
                filters: {
                    company: row.college 
                }
            };
        };
        if (!frm.doc.__islocal) {
            if (frm.doc.docstatus === 0) {
                frm.add_custom_button(__('Make Research Registration'), function() {
                    frappe.model.open_mapped_doc({
                        method: "education.research_management.doctype.research_proposal.research_proposal.make_research_registration",
                        frm: frm
                    });
                }, __('Create'));
            } 
            else if (frm.doc.docstatus === 1) {
                frm.add_custom_button(__('Make Research Project'), function() {
                    frappe.model.open_mapped_doc({
                        method: "education.research_management.doctype.research_proposal.research_proposal.make_research_project",
                        frm: frm
                    });
                }, __('Create'));
            }
        }
    },
});

frappe.ui.form.on("Research Proposal Milestone Details", {
    milestone_percentage: function(frm, cdt, cdn) {
        let total = 0;

        frm.doc.research_proposal_milestone_details.forEach(row => {
            total += row.milestone_percentage || 0;
        });

        if (total > 100) {
            frappe.msgprint(__("Total milestone percentage cannot exceed 100%. Currently: {0}%".replace("{0}", total)));
            frappe.validated = false;
        }
    }
});


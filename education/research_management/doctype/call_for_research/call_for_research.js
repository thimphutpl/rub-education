// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Call for Research", {
	refresh(frm) {
        if (!frm.doc.__islocal) { 
            frm.add_custom_button(__('Make Research Proposal'), function() {
                frappe.model.open_mapped_doc({
                    method: "education.research_management.doctype.call_for_research.call_for_research.make_research_proposal",
                    frm: frm
                });
            }, __('Create'));
        }

	},
});

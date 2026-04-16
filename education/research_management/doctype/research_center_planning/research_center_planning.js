// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Research Center Planning", {
	refresh(frm) {
        frm.set_query("research_center", function(doc) {
            return {
                filters: {
                    college: doc.company 
                }
            };
        });
        // Child table filter (CORRECT WAY)
        frm.set_query("research_kpi", "research_publications_details", function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];

            return {
                filters: {
                    parent_task: row.reporting_type   // or row.reporting_type if inside child
                }
            };
        });

        // if (!frm.doc.__islocal) { 
        //     frm.add_custom_button(__('Make Publications'), function() {
        //         frappe.model.open_mapped_doc({
        //             method: "education.research_management.doctype.research_center_planning.research_center_planning.make_research_publications",
        //             frm: frm
        //         });
        //     }, __('Create Research Item'));
        // }
	},
});


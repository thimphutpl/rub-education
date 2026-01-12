// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Update Programme", {
	refresh(frm) {

	},
    setup: function(frm){
        frm.set_query("programme_leader", "colleges", function (frm, cdt, cdn) {
            var row = locals[cdt][cdn];
            return {
                filters: { company: row.company, status: "Active" },
            };
        });
    },
    old_programme: function(frm){
        frappe.call({
            method: "get_old_programme_details",
            doc: frm.doc,
            callback: function(r){
                frm.refresh_fields();
            }
        })
    }
    
});

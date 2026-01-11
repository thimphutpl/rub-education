// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Programme Master", {
	// refresh(frm) {

	// },
    setup(frm){
        frappe.call({
            method: "sync_programme_history",
            doc: frm.doc,
            args: {update: true},
            callback: function(r){
            }
        });

		frm.set_query("programme_leader", "colleges", function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
			return {
				filters: { company: row.company, status: "Active" },
			};
		});
    }
});


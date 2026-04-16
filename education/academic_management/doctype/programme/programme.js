// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Programme", {
	refresh(frm) {
		frm.set_query("programme_leader", "colleges", function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
			return {
				filters: { company: row.company, status: "Active" },
			};
		});
	},
});

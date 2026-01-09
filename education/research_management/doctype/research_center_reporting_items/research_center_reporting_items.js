// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Research Center Reporting Items", {
	refresh(frm) {
        frm.set_query("research_center_name", function(doc) {
            return {
                filters: {
                    college: doc.college 
                }
            };
        });
	},
});

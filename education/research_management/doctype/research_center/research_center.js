// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Research Center", {
	refresh(frm) {
        frm.set_query("company", function(){
			return {
				filters: {
					"is_group": 0,
				}
			}
		})

	},
});

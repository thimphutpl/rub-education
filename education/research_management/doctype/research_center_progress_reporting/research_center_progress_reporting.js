// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Research Center Progress Reporting", {
	refresh(frm) {

	},
    onload(frm){
        if (!frm.doc.posting_date) {
			frm.set_value('posting_date', frappe.datetime.now_date());
			// frm.set_value("posting_date", get_today());
		}
    }
});

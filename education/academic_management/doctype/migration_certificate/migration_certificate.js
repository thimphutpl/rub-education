// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Migration Certificate", {
    setup(frm){
        frm.set_query('programme', function () {
            return {
              query: 'erpnext.controllers.queries.filter_college_programmes',
              filters: {
                college: frm.doc.college,
              },
            }
          })
        frm.set_query('student', function () {
            return {
                filters: {
                company: frm.doc.college,
                status: "Graduated",
                },
            }
        })
    },
	refresh(frm) {

	},
});

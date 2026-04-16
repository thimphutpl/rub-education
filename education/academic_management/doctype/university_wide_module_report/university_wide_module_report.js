// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("University Wide Module Report", {
	refresh(frm) {
        frm.set_query('module', function () {
            return {
              query: 'erpnext.controllers.queries.filter_college_modules',
              filters: {
                college: frm.doc.college              },
            }
        });
        frm.set_query("college", function () {
          return {
            filters: {
              is_group: 0,
              name: ["!=", "Office of Vice Chancellor"]
            },
          };
        });
	},
});

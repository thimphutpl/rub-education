// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Module", {
	refresh(frm) {
        frm.set_query('tutor', 'tutors', function () {
            return {
              filters: {
                status: "Active",
                is_teaching_staff: 1
              },
            }
          })
	},
});

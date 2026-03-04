// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Time Table Schedule", {
    setup(frm){
        frm.set_query('programme', function () {
            return {
              query: 'erpnext.controllers.queries.filter_college_programmes',
              filters: {
                college: frm.doc.college,
              },
            }
        })
        frm.set_query('constraint', function () {
			if (!frm.doc.college) {
				return {
					filters: {
						college: ["=", "Please Select College"]
					}
				};
			}
			if (!frm.doc.academic_term) {
				return {
					filters: {
						college: ["=", "Please Select Academic Term"]
					}
				};
			}
			return {
				filters: {
                    college: frm.doc.college,
                    academic_term: frm.doc.academic_term
				}
			};
        })
		frm.set_query('from_employee', function(doc, cdt, cdn) {

		});
    },
	refresh(frm) {

	},
    generate(frm) {
        if (!frm.doc.constraint) {
            frappe.msgprint("Please select Timetable Constraint first");
            return;
        }
        frappe.call({
            method: "generate_timetable",
            doc: frm.doc,
            freeze: true,
            callback: function(r) {
                frm.refresh_field("items")
            }
        });
    }
});

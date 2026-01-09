// // Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Research Project", {
// 	refresh(frm) {
//         if (frm.doc.docstatus === 0 && !frm.doc.__islocal) { 
//             frm.add_custom_button(__('Make Payment Entry'), function() {
//                 frappe.model.open_mapped_doc({
//                     method: "education.research_management.doctype.research_project.research_project.make_payment_entry",
//                     frm: frm
//                 });
//             }, __('Create'));
//         }
// 	},
// });


frappe.ui.form.on("Research Project", {
    refresh(frm) {
        if (frm.doc.docstatus === 0 && !frm.doc.__islocal) {

            // Check if any approved milestone has budget_amount > 0 and no reference_payment_entry
            let eligible = frm.doc.table_bzbl?.some(row => {
                return row.status === "Approved" &&
                       !row.reference_payment_entry &&
                       row.budget_amount > 0;
            });

            if (eligible) {
                frm.add_custom_button(__('Make Payment Entry'), function() {
                    frappe.model.open_mapped_doc({
                        method: "education.research_management.doctype.research_project.research_project.make_payment_entry",
                        frm: frm
                    });
                }, __('Create'));
            }
        }
    },
});


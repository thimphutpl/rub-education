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
    onload(frm){
        if (!frm.doc.posting_date) {
			frm.set_value('posting_date', frappe.datetime.now_date());
			// frm.set_value("posting_date", get_today());
		}
    }
});

// Child table events for Researcher Details
frappe.ui.form.on("Researcher Details", {
    type: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        // Clear researcher_id and name when type changes
        if (row.type) {
            frappe.model.set_value(cdt, cdn, "researcher_id", "");
            frappe.model.set_value(cdt, cdn, "researcher_name", "");
            frappe.model.set_value(cdt, cdn, "email", "");
            frappe.model.set_value(cdt, cdn, "gender", "");
            frappe.model.set_value(cdt, cdn, "phone", "");
            frappe.model.set_value(cdt, cdn, "college", "");
        }
    },
    
    researcher_id: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (!row.researcher_id) {
            frappe.model.set_value(cdt, cdn, "researcher_name", "");
            frappe.model.set_value(cdt, cdn, "email", "");
            frappe.model.set_value(cdt, cdn, "gender", "");
            frappe.model.set_value(cdt, cdn, "phone", "");
            frappe.model.set_value(cdt, cdn, "college", "");
            return;
        }
        
        if (!row.type) {
            frappe.msgprint(__("Please select Researcher Type first"));
            frappe.model.set_value(cdt, cdn, "researcher_id", "");
            return;
        }
        
        // Fetch name based on researcher type
        // fetch_researcher_name(frm, cdt, cdn, row.type, row.researcher_id);
        fetch_researcher_details(frm, cdt, cdn, row.type, row.researcher_id);
    }
});

function fetch_researcher_details(frm, cdt, cdn, type, researcher_id) {
    frappe.call({
        method: "education.research_management.doctype.research_proposal.research_proposal.get_researcher_details",
        args: {
            type: type,
            researcher_id: researcher_id
        },
        callback: function(response) {
            if (response.message && !response.message.error) {
                let data = response.message;
                
                // Set all fetched values
                frappe.model.set_value(cdt, cdn, "researcher_name", data.researcher_name || "");
                frappe.model.set_value(cdt, cdn, "email", data.email || "");
                frappe.model.set_value(cdt, cdn, "gender", data.gender || "");
                frappe.model.set_value(cdt, cdn, "phone", data.phone || "");
                frappe.model.set_value(cdt, cdn, "college", data.college || "");
                
                // Optional: Show success message
                frappe.show_alert({
                    message: __("Researcher details loaded for {0}", [data.researcher_name]),
                    indicator: "green"
                }, 2);
            } else {
                // Clear fields if invalid
                frappe.model.set_value(cdt, cdn, "researcher_id", "");
                frappe.model.set_value(cdt, cdn, "researcher_name", "");
                frappe.model.set_value(cdt, cdn, "email", "");
                frappe.model.set_value(cdt, cdn, "gender", "");
                frappe.model.set_value(cdt, cdn, "phone", "");
                frappe.model.set_value(cdt, cdn, "college", "");
                
                frappe.msgprint({
                    title: __("Invalid Selection"),
                    message: __("Invalid {0}: {1}. Please select a valid {0}.", 
                        [type, researcher_id]),
                    indicator: "red"
                });
            }
        },
        error: function(error) {
            frappe.msgprint({
                title: __("Error"),
                message: __("Failed to fetch researcher details. Please try again."),
                indicator: "red"
            });
        }
    });
}


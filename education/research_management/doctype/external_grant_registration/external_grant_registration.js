// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("External Grant Registration", {
	refresh(frm) {

	},
    investigator_type: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        // Clear investigator_type and name when type changes
        if (row.investigator_type) {
            frappe.model.set_value(cdt, cdn, "principal_investigator", "");
            frappe.model.set_value(cdt, cdn, "pi_name", "");
        }
    },
    
    principal_investigator: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (!row.principal_investigator) {
            frappe.model.set_value(cdt, cdn, "pi_name", "");
            return;
        }
        
        if (!row.investigator_type) {
            frappe.msgprint(__("Please select Researcher Type first"));
            frappe.model.set_value(cdt, cdn, "principal_investigator", "");
            return;
        }
        
        // Fetch name based on researcher type
        // fetch_researcher_name(frm, cdt, cdn, row.type, row.principal_investigator);
        fetch_researcher_details(frm, cdt, cdn, row.investigator_type, row.principal_investigator);
    }
});

function fetch_researcher_details(frm, cdt, cdn, investigator_type, principal_investigator) {
    frappe.call({
        method: "education.research_management.doctype.external_grant_registration.external_grant_registration.get_researcher_details",
        args: {
            investigator_type: investigator_type,
            principal_investigator: principal_investigator
        },
        callback: function(response) {
            if (response.message && !response.message.error) {
                let data = response.message;
                
                // Set all fetched values
                frappe.model.set_value(cdt, cdn, "pi_name", data.pi_name || "");
                
                // Optional: Show success message
                frappe.show_alert({
                    message: __("Researcher details loaded for {0}", [data.pi_name]),
                    indicator: "green"
                }, 2);
            } else {
                // Clear fields if invalid
                frappe.model.set_value(cdt, cdn, "principal_investigator", "");
                frappe.model.set_value(cdt, cdn, "pi_name", "");
                
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

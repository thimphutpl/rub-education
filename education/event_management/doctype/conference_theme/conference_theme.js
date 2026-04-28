// // Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Conference Theme", {
//     company:function(frm){
//         frm.set_value("panel_member", "");
        

//     },
// 	refresh(frm) {
//          frm.fields_dict['panel_member'].grid.get_field('employee').get_query = function(doc) {
//             if (!frm.doc.company){
//                 alert("Please select college first")
//             }
//             return {
//                 filters: {
//                     // Filter items based on the parent form's 'item_group' field
//                     "company": frm.doc.company,


//                 },
//                 query: "education.event_management.doctype.conference_theme.conference_theme.panel_member_query"
//             };
//         };
// 	},
// });


// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Conference Theme", {
    company: function(frm) {
        // Clear panel members when company changes - use [] not ""
        frm.set_value("panel_member", []);
        frm.refresh_field("panel_member");
    },

    refresh: function(frm) {
        frm.fields_dict['panel_member'].grid.get_field('employee').get_query = function(doc) {
            if (!frm.doc.company) {
                // Use Frappe message instead of alert
                frappe.msgprint("Please select college first");
                // Return empty filter when no company
                return {
                    filters: [["Employee", "name", "is", "not set"]]
                };
            }
            
            return {
                filters: {
                    "company": frm.doc.company,
                    "status": "Active",
                    "Role":"Panel Member"
                },
                query: "education.event_management.doctype.conference_theme.conference_theme.panel_member_query"
            };
        };
    }
});
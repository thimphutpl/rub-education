// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Result Modification", {
	refresh(frm) {

	},
    get_data: function(frm){
        // Validate required fields based on exam type
        // if (!frm.doc.assessment_component) {
        //     frappe.msgprint(__("Please select Assessment Component first"));
        //     return;
        // }
        // education/examination/doctype/result_modification/result_modification.py

        frappe.call({
            method: "education.examination.doctype.result_modification.result_modification.get_students",
            args: {
                doc: frm.doc
            },
            callback: function(r) {
                if (r.message) {
                    const datas = r.message;
        
                    if (datas.length === 0) {
                        frappe.msgprint(__("No data found for the selected criteria"));
                        return;
                    }
        
                    // Clear table
                    frm.clear_table('items');
        
                    datas.forEach(data => {
                        let row = frm.add_child('items');
        
                        // ✅ Mapping all fields
                        row.assessment_ledger = data.name;
                        row.module = data.module;
                        row.programme = data.programme;
                        row.assessment_component_type = data.assessment_component_type;
                        row.total_marks = data.total_marks;
                        row.passing_marks = data.passing_marks;
                        row.marks_obtained = data.marks_obtained;
                        row.assessment_weightage = data.assessment_weightage;
                        row.weightage_achieved = data.weightage_achieved;
                        row.assessment_component = data.assessment_component;
        
                        // Optional (if you include in backend)
                        row.student = data.student;
                        row.student_name = data.student_name;
                    });
        
                    // Refresh table
                    frm.refresh_field('items');
        
                    frappe.show_alert({
                        message: __("Fetched {0} records", [datas.length]),
                        indicator: 'green'
                    }, 5);
                }
            }
        });


    },
});

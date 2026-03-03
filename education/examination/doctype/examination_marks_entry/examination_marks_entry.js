// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Marks Entry", {
    refresh(frm) {

    },

    assessment_component: function(frm) {
        if (frm.doc.assessment_component) {
            // Get assessment role to conditionally set tutor field properties
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Assessment Component",
                    fieldname: "assessment_role",
                    filters: { name: frm.doc.assessment_component }
                },
                callback: function(r) {
                    if (r.message) {
                        const assessment_role = r.message.assessment_role;
                        
                        // Set tutor field as mandatory only for Tutor role
                        if (assessment_role === "Exam Cell") {
                            frm.set_df_property('tutor', 'reqd', 0);
                            frm.set_df_property('tutor', 'hidden', 0); // Keep visible but not mandatory
                        } else {
                            frm.set_df_property('tutor', 'reqd', 1);
                            frm.set_df_property('tutor', 'hidden', 0);
                        }
                    }
                }
            });
        }
        exam_registration_filter(frm);
    },

    exam_type: function(frm){
        exam_registration_filter(frm);
    },

    get_students: function(frm){
        // Validate required fields
        if (!frm.doc.assessment_component) {
            frappe.msgprint(__("Please select Assessment Component first"));
            return;
        }
        if (!frm.doc.examination_registration) {
            frappe.msgprint(__("Please select Examination Registration"));
            return;
        }
        
        // Get assessment role to conditionally validate tutor
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Assessment Component",
                fieldname: "assessment_role",
                filters: { name: frm.doc.assessment_component }
            },
            callback: function(role_response) {
                const assessment_role = role_response.message ? role_response.message.assessment_role : "Tutor";
                
                // Validate tutor only if assessment_role is Tutor and exam type requires it
                if (assessment_role === "Tutor" && !frm.doc.tutor) {
                    frappe.msgprint(__("Please select Tutor"));
                    return;
                }
                
                // Proceed with getting students
                frappe.call({
                    method: "education.examination.doctype.examination_marks_entry.examination_marks_entry.get_students",
                    args: {
                        examination_registration: frm.doc.examination_registration,
                        doc: frm.doc
                    },
                    callback: function(r) {
                        if (r.message) {
                            console.table(r.message);

                            // Clear and populate child table
                            frm.clear_table('items');
                            
                            r.message.forEach(student => {
                                let elg_std_row = frm.add_child('items');
                                elg_std_row.student = student.student;
                                elg_std_row.student_name = student.student_name;
                                elg_std_row.programme = student.programme;
                            });
                            
                            // Refresh child table
                            frm.refresh_field('items');
                            
                            frappe.show_alert({
                                message: __("Fetched {0} students", [r.message.length]),
                                indicator: 'green'
                            }, 3);
                        }
                    }
                });
            }
        });
    }
});

function exam_registration_filter(frm) {
    if (!frm.doc.assessment_component) {
        return;
    }
    
    // Get assessment role to conditionally set filters
    frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "Assessment Component",
            fieldname: "assessment_role",
            filters: { name: frm.doc.assessment_component }
        },
        callback: function(role_response) {
            const assessment_role = role_response.message ? role_response.message.assessment_role : "Tutor";
            
            frm.set_query('examination_registration', function() {
                let filters = {
                    assessment_component: frm.doc.assessment_component,
                    module: frm.doc.module,
                    academic_term: frm.doc.academic_term,
                    company: frm.doc.college
                };
                
                // Add tutor filter only for Tutor role
                if (assessment_role === "Tutor" && frm.doc.tutor) {
                    filters.tutor = frm.doc.tutor;
                }
                
                // Add reassesment filter based on exam_type
                if (frm.doc.exam_type === 'Exam Re-Assessment') {
                    filters.reassesment = 1;
                } else if (frm.doc.exam_type === 'Regular Assessment') {
                    filters.reassesment = 0;
                }
                
                return {
                    filters: filters
                };
            });
            
            // Refresh the field to apply new filter
            frm.refresh_field('examination_registration');
        }
    });
}
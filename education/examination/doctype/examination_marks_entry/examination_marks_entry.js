// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Marks Entry", {
    refresh(frm) {
        // Add module field visibility based on assessment role
        this.set_module_field_visibility(frm);
    },

    assessment_component: function(frm) {
        if (frm.doc.assessment_component) {
            // Get assessment role to conditionally set tutor field properties and module visibility
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
                            frm.set_df_property('tutor', 'hidden', 0);
                            // For Exam Cell, make module optional
                            frm.set_df_property('module', 'reqd', 0);
                        } else {
                            frm.set_df_property('tutor', 'reqd', 1);
                            frm.set_df_property('tutor', 'hidden', 0);
                            // For Tutor, module is mandatory
                            frm.set_df_property('module', 'reqd', 1);
                        }
                    }
                }
            });
        }
    },

    exam_type: function(frm){
        this.set_module_field_visibility(frm);
    },

    get_students: function(frm){
        // Validate required fields
        if (!frm.doc.assessment_component) {
            frappe.msgprint(__("Please select Assessment Component first"));
            return;
        }
        if (!frm.doc.academic_year) {
            frappe.msgprint(__("Please select Academic Year"));
            return;
        }
        if (!frm.doc.academic_term) {
            frappe.msgprint(__("Please select Academic Term"));
            return;
        }
        if (!frm.doc.college) {
            frappe.msgprint(__("Please select College"));
            return;
        }
        
        // Get assessment role to conditionally validate tutor and module
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Assessment Component",
                fieldname: "assessment_role",
                filters: { name: frm.doc.assessment_component }
            },
            callback: function(role_response) {
                const assessment_role = role_response.message ? role_response.message.assessment_role : "Tutor";
                
                if (assessment_role === "Tutor" && !frm.doc.tutor) {
                    frappe.msgprint(__("Please select Tutor"));
                    return;
                }
                
                if (assessment_role === "Tutor" && !frm.doc.module) {
                    frappe.msgprint(__("Please select Module"));
                    return;
                }

                frappe.call({
                    method: "education.examination.doctype.examination_marks_entry.examination_marks_entry.get_students",
                    args: {
                        examination_registration: frm.doc.examination_registration || null,
                        doc: frm.doc
                    },
                    callback: function(r) {
                        if (r.message) {
                
                            const students = r.message;
                
                            console.table(students);
                
                            // Clear and populate child table
                            frm.clear_table('items');
                
                            students.forEach(student => {
                                let row = frm.add_child('items');
                                row.student = student.student;
                                row.student_name = student.student_name;
                                row.programme = student.program;
                            });
                
                            // Refresh child table
                            frm.refresh_field('items');
                
                            // Simple alert
                            frappe.show_alert({
                                message: __("Fetched {0} students", [students.length]),
                                indicator: 'green'
                            }, 5);
                        }
                    }
                });
            }
        });
    },
    
    set_module_field_visibility: function(frm) {
        // Function to set module field visibility based on exam type and assessment role
        if (frm.doc.exam_type && frm.doc.assessment_component) {
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
                        
                        // For Exam Cell, module is optional
                        if (assessment_role === "Exam Cell") {
                            frm.set_df_property('module', 'reqd', 0);
                            frm.set_df_property('module', 'hidden', 0);
                        } 
                        // For Tutor, module is mandatory
                        else {
                            frm.set_df_property('module', 'reqd', 1);
                            frm.set_df_property('module', 'hidden', 0);
                        }
                                              
                    }
                }
            });
        }
    }
});
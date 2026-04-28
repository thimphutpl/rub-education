// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Marks Entry", {
    onload(frm) {
		if (!frm.doc.posting_date) {
			frm.set_value("posting_date", frappe.datetime.now_date());
		}
	},
    setup(frm){
        frm.set_query('module_enrolment_key', function () {
            return {
              filters: {
                // program: frm.doc.programme,
                academic_term: frm.doc.academic_term,
                docstatus: 1,
              },
            }
          })
        frm.set_query("college", function () {
            return {
                filters: {
                    is_group: 0,
            name: ["!=", "Office of Vice Chancellor"]
                },
            };
        });
        frm.set_query('programme', function () {
            return {
                query:
                'education.education.doctype.module_enrolment_tool.module_enrolment_tool.get_programme',
              filters: {
                college: frm.doc.college,
                date: frm.doc.posting_date,
                validate: 1
              },
            }
        })
        frm.set_query('tutor', function () {
            return {
                query:
                'erpnext.controllers.queries.filter_module_tutors',
                filters: {
                // program: frm.doc.programme,
                college: frm.doc.college,
                programme: frm.doc.programme,
                module: frm.doc.module,
                },
            }
        })
        frm.set_query('assessment_component', function () {
            return {
                query:
                'erpnext.controllers.queries.filter_assessment_component',
                filters: {
                college: frm.doc.college,
                programme: frm.doc.programme,
                module: frm.doc.module,
                tutor: frm.doc.tutor,
                academic_term: frm.doc.academic_term,
                examination_assesment: 1
                },
            }
        })
    },
    refresh(frm) {
        // Set module field visibility based on exam type
        this.set_module_field_visibility(frm);

        frm.set_query('assessment_component', function () {
            return {
                query:
                'erpnext.controllers.queries.filter_assessment_component',
                filters: {
                college: frm.doc.college,
                programme: frm.doc.programme,
                module: frm.doc.module,
                tutor: frm.doc.tutor,
                academic_term: frm.doc.academic_term,
                },
            }
        })
    },
    

   
        

    // assessment_component: function(frm) {
    //     if (frm.doc.assessment_component) {
    //         // Get assessment component details
    //         frappe.call({
    //             method: "frappe.client.get_value",
    //             args: {
    //                 doctype: "Assessment Component",
    //                 fieldname: ["assessment_role", "assessment_name"],
    //                 filters: { name: frm.doc.assessment_component }
    //             },
    //             callback: function(r) {
    //                 if (r.message) {
    //                     // Set tutor field as mandatory
    //                     frm.set_df_property('tutor', 'reqd', 1);
    //                     frm.set_df_property('tutor', 'hidden', 0);
    //                     // Module is mandatory for Regular Assessment
    //                     if (frm.doc.exam_type === 'Regular Assessment') {
    //                         frm.set_df_property('module', 'reqd', 1);
    //                     } else {
    //                         frm.set_df_property('module', 'reqd', 0);
    //                     }
    //                 }
    //             }
    //         });
    //     }
    // },

    exam_type: function(frm){
        this.set_module_field_visibility(frm);
        // Clear examination registration when switching to Regular Assessment
        if (frm.doc.exam_type === 'Regular Assessment') {
            frm.set_value('examination_registration', null);
        }
    },

    get_students: function(frm){
        // Validate required fields based on exam type
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
        if (!frm.doc.semester) {
            frappe.msgprint(__("Please select Semester"));
            return;
        }
        
        // Validate tutor (always required now)
        if (!frm.doc.tutor) {
            frappe.msgprint(__("Please select Tutor"));
            return;
        }
        
        // For Regular Assessment, module is required
        if (frm.doc.exam_type === 'Regular Assessment' && !frm.doc.module) {
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
                    
                    if (students.length === 0) {
                        frappe.msgprint(__("No students found for the selected criteria"));
                        return;
                    }
                    
                    // Clear and populate child table
                    frm.clear_table('items');
                    
                    students.forEach(student => {
                        let row = frm.add_child('items');
                        row.student = student.student;
                        row.student_name = student.student_name;
                        row.programme = student.programme;
                    });
                    
                    // Refresh child table
                    frm.refresh_field('items');
                    
                    // Show success message
                    frappe.show_alert({
                        message: __("Fetched {0} students", [students.length]),
                        indicator: 'green'
                    }, 5);
                }
            }
        });
    },
    
    set_module_field_visibility: function(frm) {
        // Function to set module field visibility based on exam type
        if (frm.doc.exam_type) {
            // For Regular Assessment, module is mandatory
            if (frm.doc.exam_type === 'Regular Assessment') {
                frm.set_df_property('module', 'reqd', 1);
                frm.set_df_property('module', 'hidden', 0);
                frm.set_df_property('examination_registration', 'hidden', 1);
                frm.set_df_property('examination_registration', 'reqd', 0);
            } 
            // For other exam types, module is optional and examination registration may be needed
            else {
                frm.set_df_property('module', 'reqd', 0);
                frm.set_df_property('module', 'hidden', 0);
                frm.set_df_property('examination_registration', 'hidden', 0);
            }
        }
    }
});
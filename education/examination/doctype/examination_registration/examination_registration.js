// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Registration", {
    refresh(frm) {
        // Add any custom refresh logic here
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
        if (!frm.doc.module) {
            frappe.msgprint(__("Please select Module"));
            return;
        }
        if (!frm.doc.company) {
            frappe.msgprint(__("Please select College"));
            return;
        }
        
        // Get assessment role first to conditionally validate tutor
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Assessment Component",
                fieldname: "assessment_role",
                filters: { name: frm.doc.assessment_component }
            },
            callback: function(role_response) {
                const assessment_role = role_response.message ? role_response.message.assessment_role : "Tutor";
                
                // Validate tutor only if assessment_role is Tutor
                if (assessment_role === "Tutor" && !frm.doc.tutor) {
                    frappe.msgprint(__("Please select Tutor"));
                    return;
                }

                
                
                if (frm.doc.reassesment === undefined || frm.doc.reassesment === null) {
                    frappe.msgprint(__("Please select Reassessment option"));
                    return;
                }
                
                // Proceed with getting students
                frappe.call({
                    method: "education.examination.doctype.examination_registration.examination_registration.get_students",
                    args: {
                        academic_year: frm.doc.academic_year,
                        academic_term: frm.doc.academic_term,
                        module: frm.doc.module,
                        company: frm.doc.company,
                        tutor: frm.doc.tutor || "", // Send empty string if no tutor
                        reassesment: frm.doc.reassesment,
                        assessment_component: frm.doc.assessment_component
                    },
                    callback: function(r) {
                        if (r.message) {
                            const response = r.message;
                            const students = response.students;
                            const summary = response.summary;
                            

                            // Clear tables first
                            frm.clear_table('eligible_students');
                            frm.clear_table('non_eligible_students');
                            
                            let eligibleCount = 0;
                            let nonEligibleCount = 0;
                            
                            students.forEach(student => {
                                // Check if student is excluded
                                if (student.excluded === 1) {
                                    // Add to non-eligible students
                                    let non_elg_std_row = frm.add_child('non_eligible_students');
                                    non_elg_std_row.student = student.student;
                                    non_elg_std_row.student_name = student.student_name;
                                    non_elg_std_row.attendance_percentage = student.attendance_percentage || 0;
                                    
                                    // Set exclusion reasons
                                    non_elg_std_row.exclusion_reasons = student.exclusion_reasons || "";
                                    
                                    // Set disciplinary issue if available
                                    if (student.disciplinary_issue_type) {
                                        non_elg_std_row.disciplinary_issue = student.disciplinary_issue_type;
                                    }
                                    
                                    // Set financial issue for unpaid credit clearance
                                    if (student.credit_clearance_amount) {
                                        non_elg_std_row.financial_issue = "Unpaid: " + student.credit_clearance_amount;
                                    }
                                    
                                    // Reset consideration fields
                                    non_elg_std_row.consider_attendance = 0;
                                    non_elg_std_row.reason_for_consideration = "";
                                    non_elg_std_row.attachment = "";
                                    
                                    nonEligibleCount++;
                                }
                                else {
                                    // Add to eligible students
                                    let elg_std_row = frm.add_child('eligible_students');
                                    elg_std_row.student = student.student;
                                    elg_std_row.student_name = student.student_name;
                                    elg_std_row.attendance_percentage = student.attendance_percentage || 100;
                                    eligibleCount++;
                                }
                            });
                            
                            // Set the total eligible students count
                            frm.set_value('total_eligible_student', eligibleCount.toString());
                            
                            // Refresh all fields
                            frm.refresh_field('eligible_students');
                            frm.refresh_field('non_eligible_students');
                            frm.refresh_field('total_eligible_student');
                            
                            
                            
                            // Show brief alert
                            frappe.show_alert({
                                message: __("Processed {0} students: {1} eligible, {2} non-eligible", 
                                           [summary.total_students, summary.total_eligible, summary.total_non_eligible]),
                                indicator: 'green'
                            }, 5);
                        }
                    },
                    error: function(r) {
                        frappe.msgprint(__("Error fetching students: ") + r.message);
                    }
                });
            }
        });
    },
    
    assessment_component: function(frm) {
        // Clear students when assessment component changes
        if (frm.doc.assessment_component) {
            frm.clear_table('eligible_students');
            frm.clear_table('non_eligible_students');
            frm.set_value('total_eligible_student', '');
            frm.refresh_field('eligible_students');
            frm.refresh_field('non_eligible_students');
            frm.refresh_field('total_eligible_student');
            
            // Get assessment role to conditionally hide/show tutor field
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
    },
    
    reassesment: function(frm) {
        // Clear students when reassessment status changes
        frm.clear_table('eligible_students');
        frm.clear_table('non_eligible_students');
        frm.set_value('total_eligible_student', '');
        frm.set_value('examination_registration', '');
        frm.refresh_field('eligible_students');
        frm.refresh_field('non_eligible_students');
        frm.refresh_field('total_eligible_student');
        frm.refresh_field('examination_registration');
    }
});
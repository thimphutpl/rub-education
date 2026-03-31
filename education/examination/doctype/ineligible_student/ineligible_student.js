// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ineligible Student", {
    refresh(frm) {
        if (frm.doc.non_eligible_students && frm.doc.non_eligible_students.length > 0) {
            frm.add_custom_button(__('Notify Students'), function() {
                notify_non_eligible_students(frm);
            });
        }
    },

    get_students: function(frm){
        // Validate required fields
        if (!frm.doc.academic_year) {
            frappe.msgprint(__("Please select Academic Year"));
            return;
        }
        if (!frm.doc.academic_term) {
            frappe.msgprint(__("Please select Academic Term"));
            return;
        }
        if (!frm.doc.company) {
            frappe.msgprint(__("Please select College"));
            return;
        }
        
        // Proceed with getting students
        frappe.call({
            method: "education.examination.doctype.ineligible_student.ineligible_student.get_students",
            args: {
                academic_year: frm.doc.academic_year,
                academic_term: frm.doc.academic_term,
                company: frm.doc.company
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

// Function to notify non-eligible students
function notify_non_eligible_students(frm) {
    if (!frm.doc.non_eligible_students || frm.doc.non_eligible_students.length === 0) {
        frappe.msgprint(__("No non-eligible students to notify"));
        return;
    }
    
    // Prepare the data to send - convert child table data to a proper array
    let students_data = [];
    frm.doc.non_eligible_students.forEach(function(student) {
        students_data.push({
            "student": student.student,
            "student_name": student.student_name,
            "attendance_percentage": student.attendance_percentage,
            "disciplinary_issue": student.disciplinary_issue,
            "financial_issue": student.financial_issue,
            "exclusion_reasons": student.exclusion_reasons,
            "consider_attendance": student.consider_attendance,
            "reason_for_consideration": student.reason_for_consideration
        });
    });
    
    // Confirm before sending emails
    frappe.confirm(
        __("Are you sure you want to send notifications to {0} non-eligible students?", [students_data.length]),
        function() {
            // Show loading message
            frappe.show_alert({
                message: __("Sending notifications..."),
                indicator: 'orange'
            }, 10);
            
            // Call server-side function to send emails
            frappe.call({
                method: "education.examination.doctype.ineligible_student.ineligible_student.notify_non_eligible_students",
                args: {
                    docname: frm.doc.name,
                    non_eligible_students: students_data  // Send as array, not as string
                },
                callback: function(r) {
                    if (r.message) {
                        const result = r.message;
                        if (result.success) {
                            frappe.show_alert({
                                message: __("Notifications sent successfully to {0} students. Failed: {1}", 
                                           [result.success_count, result.failed_count]),
                                indicator: 'green'
                            }, 5);
                            
                            // Optionally add a custom button to view failed students
                            if (result.failed_count > 0 && result.failed_students && result.failed_students.length > 0) {
                                frm.add_custom_button(__('View Failed Notifications'), function() {
                                    let failed_list = result.failed_students.map(s => s.student_name + ": " + s.reason).join("\n");
                                    frappe.msgprint({
                                        title: __("Failed Notifications"),
                                        message: __("Failed to send to the following students:\n{0}", [failed_list]),
                                        indicator: 'red'
                                    });
                                });
                            }
                        } else if (result.failed_count > 0) {
                            frappe.msgprint({
                                title: __("Partial Success"),
                                message: __("Sent to {0} students. Failed to send to {1} students. Check error log for details.", 
                                           [result.success_count, result.failed_count]),
                                indicator: 'orange'
                            });
                        } else {
                            frappe.msgprint(__("Failed to send notifications. Please check error log."));
                        }
                    } else {
                        frappe.msgprint(__("Failed to send notifications. Please try again."));
                    }
                },
                error: function(r) {
                    frappe.msgprint(__("Error sending notifications: ") + (r.message || "Unknown error"));
                }
            });
        },
        function() {
            // User cancelled
            frappe.show_alert({
                message: __("Notification cancelled"),
                indicator: 'red'
            }, 3);
        }
    );
}
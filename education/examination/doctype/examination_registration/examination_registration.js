// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Registration", {
	refresh(frm) {

	},

    get_students: function(frm){
        frappe.call({
            method: "education.examination.doctype.examination_registration.examination_registration.get_students",
            args: {
                academic_year: frm.doc.academic_year,
                academic_term: frm.doc.academic_term,
                module: frm.doc.module,
                company: frm.doc.company,
                tutor: frm.doc.tutor,
                reassesment: frm.doc.reassesment,
                assesment_component: frm.doc.assessment_component,
                academic_term: frm.doc.academic_term
                // doc : frm.doc
            },
            callback: function(r) {
                if (r.message) {
                    // frappe.msgprint(`Fetched ${r.message.length} students.`);
                    console.table(r.message);

                    // Example: populate a child table
                    frm.clear_table('eligible_students');
                    frm.clear_table('non_eligible_students');
                    r.message.forEach(student => {
                        if(student.datatype ==="Review" ){
                            let elg_std_row = frm.add_child('eligible_students');
                            elg_std_row.student = student.student;
                            elg_std_row.student_name = student.student_name;
                        }
                        else if (student.attendance_percentage >= 90) {
                            // Add to eligible students table
                            let elg_std_row = frm.add_child('eligible_students');
                            elg_std_row.student = student.student;
                            elg_std_row.student_name = student.student_name;
                            elg_std_row.attendance_percentage = student.attendance_percentage;
                        } 
                        
                        else {
                            // Add to non-eligible students table
                            let non_elg_std_row = frm.add_child('non_eligible_students');
                            non_elg_std_row.student = student.student;
                            non_elg_std_row.student_name = student.student_name;
                            non_elg_std_row.attendance_percentage = student.attendance_percentage;
                        }
                    });
                    
                    // Refresh both child tables to show updates
                    frm.refresh_field('eligible_students');
                    frm.refresh_field('non_eligible_students');
                }
            }
        });

    }
});

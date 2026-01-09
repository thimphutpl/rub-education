// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Marks Entry", {
	refresh(frm) {

	},

    exam_type: function(frm){
        exam_registration_filter(frm)
    },

    get_students: function(frm){
        frappe.call({
            method: "education.examination.doctype.examination_marks_entry.examination_marks_entry.get_students",
            args: {
                examination_registration: frm.doc.examination_registration,
                doc: frm.doc
               
                // doc : frm.doc
            },
            callback: function(r) {
                if (r.message) {
                    // frappe.msgprint(`Fetched ${r.message.length} students.`);
                    console.table(r.message);

                    // Example: populate a child table
                    frm.clear_table('items');
                    // frm.clear_table('non_eligible_students');
                    r.message.forEach(student => {
                        // if (student.attendance_percentage >= 90) {
                            // Add to eligible students table
                            let elg_std_row = frm.add_child('items');
                            elg_std_row.student = student.student;
                            elg_std_row.student_name = student.student_name;
                            // elg_std_row.attendance_percentage = student.attendance_percentage;
                        // } else {
                        //     // Add to non-eligible students table
                        //     let non_elg_std_row = frm.add_child('non_eligible_students');
                        //     non_elg_std_row.student = student.student;
                        //     non_elg_std_row.student_name = student.student_name;
                        //     non_elg_std_row.attendance_percentage = student.attendance_percentage;
                        // }
                    });
                    
                    // Refresh both child tables to show updates
                    frm.refresh_field('items');
                   
                }
            }
        });

    }
});


function exam_registration_filter(frm) {
    frm.set_query('examination_registration', function() {
        if (frm.doc.exam_type === 'Exam Re-Assessment') {
            return {
                filters: {
                    reassesment: 1
                }
            };
        
        }else if (frm.doc.exam_type === 'Regular Assessment') {
            return {
                filters: {
                    reassesment: 0
                }
            };
        
        } else {
            // Return an empty object instead of None
            return {
                filters: {
                    reassesment: ["!=", 2]
                }
            };
        }
    });
}

// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Module Enrollment Tool", {
	refresh(frm) {
        frm.set_query('course', function () {
            return {
                query:
                'education.education.doctype.program_enrollment.program_enrollment.get_program_courses',
              filters: {
                program: frm.doc.programme,
                college: frm.doc.college,
                semester: frm.doc.semester,
                validate: 1
              },
            }
          })
          frm.set_query('programme', function () {
            return {
                query:
                'education.education.doctype.module_enrollment_tool.module_enrollment_tool.get_programme',
              filters: {
                college: frm.doc.college,
                date: frm.doc.enrollment_date,
                validate: 1
              },
            }
          })
          frm.set_query('student_section', function () {
            return {
                query:
                'education.education.doctype.module_enrollment_tool.module_enrollment_tool.filter_student_section',
              filters: {
                college: frm.doc.college,
                programme: frm.doc.programme,
                academic_term: frm.doc.academic_term,
                validate: 1
              },
            }
          })
        frappe.db.get_value('Academic Term', frm.doc.academic_term, 'academic_session', (r) => {
            frm.set_query('semester', function () {
                return {
                filters: {
                    session: r.academic_session,
                },
                }
            })
        });
	},
    academic_term: function(frm){
        frm.set_value('semester', '');
        frm.set_value('student_section', '');
        if(frm.doc.academic_term){
            frappe.db.get_value('Academic Term', frm.doc.academic_term, 'academic_session', (r) => {
                frm.set_query('semester', function () {
                    return {
                    filters: {
                        session: r.academic_session,
                    },
                    }
                })
            });
        }
        else{
            frm.set_query('semester', function () {
                return {
                    filters: {
                        name: ["=", "Please select Academic Term"],
                    }
                };
            });
        }
    },
    get_students(frm){
        frappe.call({
            method: "get_students",
            doc: frm.doc,
            args: {
                programme: frm.doc.programme,
                college: frm.doc.college,
                course: frm.doc.course,
                semester: frm.doc.semester,
                student_section: frm.doc.student_section,
                batch: frm.doc.batch
            },
            callback: function(r) {
                if(r.message){
                    let students = r.message;
                    students.forEach(student => {
                        let row = frm.add_child("students");
                        row.student = student.name;
                        row.student_name = student.student_name;
                    })
                    frm.refresh_field("students");
                }
            }
        });       
    }
});

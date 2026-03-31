// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Module Enrolment Key", {
    setup(frm){
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
                'erpnext.controllers.queries.get_programme',
              filters: {
                college: frm.doc.college,
                date: frm.doc.posting_date,
                validate: 1
              },
            }
        });
        frm.set_query('module', function () {
            return {
              query: 'erpnext.controllers.queries.filter_college_programme_modules',
              filters: {
                college: frm.doc.college,
                programme: frm.doc.programme,
                academic_session: frm.doc.academic_session,
                check_tutor: 1,
                user: frappe.session.user,
              },
            }
        });
        frm.set_query('academic_term', function(doc, cdt, cdn) {
          if (!frm.doc.college) {
            return {
              filters: {
                college: ["=", "Please Select College"]
              }
            };
          }
          else{
            return {
              filters: {
                college: frm.doc.college,
              }
            };
          }
        });
        frm.set_query('student_section', function(doc, cdt, cdn) {
          if (!frm.doc.college) {
            return {
              filters: {
                college: ["=", "Please Select College"]
              }
            };
          }
          else if (!frm.doc.academic_term) {
            return {
              filters: {
                college: ["=", "Please Select Academic Term"]
              }
            };
          }
          else if (!frm.doc.programme) {
            return {
              filters: {
                college: ["=", "Please Select Programme"]
              }
            };
          }
          else{
            return {
              filters: {
                college: frm.doc.college,
                academic_term: frm.doc.academic_term,
                program: frm.doc.programme,
              }
            };
          }
        });
    },
	refresh(frm) {

	},
    
});

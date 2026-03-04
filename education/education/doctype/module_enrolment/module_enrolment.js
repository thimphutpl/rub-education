// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Module Enrolment', {
  setup: function(frm){
    frm.set_query('tutor', function () {
      return {
          query:
          'erpnext.controllers.queries.filter_module_tutors',
        filters: {
          // program: frm.doc.programme,
          college: frm.doc.college,
          programme: frm.doc.program,
          module: frm.doc.course,
        },
      }
    })
    frm.set_query('module_enrollment_key', function () {
      return {
          query:
          'erpnext.controllers.queries.filter_module_enrolment_key',
        filters: {
          // program: frm.doc.programme,
          student_id: frappe.session.user,
          enrollment_date: frm.doc.enrollment_date,
        },
      }
    })
  },
  refresh: function (frm) {
    frm.set_query('student', function () {
      if(!frm.doc.module_enrollment_key){
        frappe.throw("Please select Module Enrolment Key.")
      }
      else{
        return {
          query:
            'erpnext.controllers.queries.filter_batch_section_students',
          filters: {
            batch: frm.doc.student_batch,
            section: frm.doc.student_section,
            student: frappe.session.user,
          },
        }
      }
    })
  },
  module_enrollment_key: function(frm){
    frappe.call({
      method: "get_module_tutor",
      doc: frm.doc,
      callback: function(r){
        frm.refresh_field("tutors");
      }
    })
  }
})

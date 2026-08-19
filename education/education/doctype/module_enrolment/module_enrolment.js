// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Module Enrolment', {
  onload: function(frm){
    if(frm.is_dirty() && frm.doc.__islocal){
      frappe.call({
        method: "get_college_student",
        doc: frm.doc,
        callback: function(r){
          if(r.message){
            frm.set_value("college", r.message[0]);
            frm.set_value("student", r.message[1]);
            frm.refresh_field("college");
            frm.refresh_field("student");
          }
        }
      })
    }

  },
  setup: function(frm){
    if(frm.is_dirty() && frm.doc.__islocal){
      frm.set_value("academic_term", undefined);
      frm.set_value("academic_year", undefined);
      frm.refresh_fields();
    }

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
          college: frm.doc.college,
          academic_term: frm.doc.academic_term,
          program: frm.doc.program,
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
      method: "get_module_details",
      doc: frm.doc,
      callback: function(r){
        if(r.message){
          console.log(r.message['student_section'])
          frm.set_value("student_section", r.message['student_section'])
          frm.set_value("academic_term", r.message['academic_term'])
          frm.set_value("academic_year", r.message['academic_year'])
          frm.set_value("student", r.message['student'])
          frm.set_value("course", r.message['module'])
        }
        frm.refresh_fields();
      }
    })
  },
  course: function(frm){
    frappe.call({
      method: "get_tutor_details",
      doc: frm.doc,
      callback: function(r){
        frm.refresh_field("tutors");
      }
    })
  }
})

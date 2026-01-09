// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Leave Application', {
  student: function (frm) {
    frappe.call({
      method:
        'education.education.doctype.student_leave_application.student_leave_application.get_student_groups',
      args: {
        student: frm.doc.student,
      },
      callback: function (r) {
        if (r.message) {
          frm.set_query('student_group', () => {
            return {
              filters: {
                name: ['in', r.message],
              },
            }
          })
          frm.set_query('course_schedule', () => {
            return {
              filters: {
                student_group: ['in', r.message],
              },
            }
          })
        }
      },
    })
  },
  from_date: function (frm) {
    if (frm.doc.from_date && frm.doc.to_date) {
      frappe.call({
        method:
          'education.education.doctype.student_leave_application.student_leave_application.calculate_leave_days',
        args: {
          from_date: frm.doc.from_date,
          to_date: frm.doc.to_date,
        },
        callback: function (r) {
          if (r.message) {
            frm.set_value('total_leave_days', r.message);
            frm.refresh_field('total_leave_days');
          }
        },
      });
    }
  },
  to_date: function (frm) {
    if (frm.doc.from_date && frm.doc.to_date) {
      frappe.call({
        method:
          'calculate_leave_days',
        doc: frm.doc,
        args: {
          from_date: frm.doc.from_date,
          to_date: frm.doc.to_date,
        },
        callback: function (r) {
          if (r.message) {
            frm.set_value('total_leave_days', r.message);
            frm.refresh_field('total_leave_days');
          }
        },
      });
    }
  }
})

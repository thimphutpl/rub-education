frappe.ui.form.on('Student Section Creation Tool', 'refresh', function (frm) {
  // frm.disable_save()
  if (!frm.doc.__islocal) {
    frm.page.set_primary_action(__('Create Student Section'), function () {
      frappe.call({
        method: 'create_student_groups',
        doc: frm.doc,
      })
    })
  }

  frappe.realtime.on('student_group_creation_progress', function (data) {
    if (data.progress) {
      frappe.hide_msgprint(true)
      frappe.show_progress(
        __('Creating student groups'),
        data.progress[0],
        data.progress[1]
      )
    }
  })
})

frappe.ui.form.on('Student Section Creation Tool', 'get_students', function (frm) {
  if (
    frm.doc.group_based_on == 'Batch' ||
    frm.doc.group_based_on == 'Course'
  ) {
    var student_list = []
    var max_roll_no = 0
    $.each(frm.doc.students, function (_i, d) {
      student_list.push(d.student)
      if (d.group_roll_number > max_roll_no) {
        max_roll_no = d.group_roll_number
      }
    })

    if (frm.doc.academic_year) {
        if(!frm.doc.college){
          frappe.throw("Please select College.")
        }
        if(!frm.doc.program){
          frappe.throw("Please select Programme.")
        }
        frappe.call({
            method: "get_students",
            doc: frm.doc,
            args: {
                programme: frm.doc.program,
                college: frm.doc.college,
                batch: frm.doc.batch
            },
            callback: function(r) {
                if(r.message){
                    console.log(r.message)
                    let students = r.message;
                    let roll_no = 1
                    let section_count = 0
                    let student_count = 1
                    students.forEach(student => {
                        let row = frm.add_child("students");
                        row.student = student.name;
                        row.student_name = student.student_name;
                        row.group_roll_number = roll_no;
                        row.section_name = frm.doc.student_group_name+" "+String.fromCharCode(65 + section_count);
                        roll_no += 1;
                        if(student_count%frm.doc.max_strength == 0){
                          section_count += 1
                          roll_no = 1
                        }
                        student_count += 1
                    })
                    frm.refresh_field("students");
                }
            }
        });       
      // frappe.call({
      //   method:
      //     'education.education.doctype.student_section.student_section.get_students',
      //   args: {
      //     academic_year: frm.doc.academic_year,
      //     academic_term: frm.doc.academic_term,
      //     group_based_on: frm.doc.group_based_on,
      //     program: frm.doc.program,
      //     batch: frm.doc.batch,
      //     student_category: frm.doc.student_category,
      //     course: frm.doc.course,
      //   },
      //   callback: function (r) {
      //     if (r.message) {
      //       $.each(r.message, function (i, d) {
      //         if (!in_list(student_list, d.student)) {
      //           var s = frm.add_child('students')
      //           s.student = d.student
      //           s.student_name = d.student_name
      //           if (d.active === 0) {
      //             s.active = 0
      //           }
      //           s.group_roll_number = ++max_roll_no
      //         }
      //       })
      //       refresh_field('students')
      //       frm.save()
      //     } else {
      //       frappe.msgprint(__('Student Section is already updated.'))
      //     }
      //   },
      // })
    }
  } else {
    frappe.msgprint(
      __('Select students manually for the Activity based Group')
    )
  }
})
frappe.ui.form.on('Student Section Creation Tool', 'setup', function (frm) {
  // frm.disable_save()
    frm.set_query('program', function () {
      return {
        query: 'erpnext.controllers.queries.filter_college_programmes',
        filters: {
          college: frm.doc.college,
        },
      }
    })
    frm.set_query('batch', function () {
      return {
        filters: {
          college: frm.doc.college,
        },
      }
    })
})

frappe.ui.form.on('Student Section Creation Tool', 'get_courses', function (frm) {
  frm.set_value('courses', [])
  if (frm.doc.academic_year && frm.doc.program) {
    frappe.call({
      method: 'get_courses',
      doc: frm.doc,
      callback: function (r) {
        if (r.message) {
          frm.set_value('courses', r.message)
        }
      },
    })
  }
})

frappe.ui.form.on('Student Section Creation Tool', 'onload', function (frm) {
  cur_frm.set_query('academic_term', function () {
    return {
      filters: {
        academic_year: frm.doc.academic_year,
      },
    }
  })
})

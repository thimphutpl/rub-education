frappe.ui.form.on('Student Section Creation Tool', 'refresh', function (frm) {
  // frm.disable_save()
  if (!frm.doc.__islocal && frm.doc.student_sections_created == 0) {
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
    frm.doc.group_based_on == 'Semester'
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
                  frm.clear_table("students");

                  let students = r.message;
                  let max = frm.doc.max_strength;
                  
                  let total = students.length;
                  
                  // Step 1: minimum sections needed
                  let section_count = Math.ceil(total / max);
                  
                  // Step 2: try reducing sections if possible
                  while (section_count > 1) {
                      let avg = Math.ceil(total / (section_count - 1));
                  
                      // allow exceeding max to balance (your requirement)
                      if (avg <= max + 5) {  // tolerance (adjust if needed)
                          section_count -= 1;
                      } else {
                          break;
                      }
                  }
                  
                  // Step 3: even distribution
                  let base = Math.floor(total / section_count);
                  let remainder = total % section_count;
                  
                  let student_index = 0;
                  
                  for (let sec = 0; sec < section_count; sec++) {
                      let roll_no = 1;
                  
                      // top-down distribution
                      let size = base + (sec < remainder ? 1 : 0);
                  
                      for (let i = 0; i < size; i++) {
                          let student = students[student_index];
                  
                          let row = frm.add_child("students");
                          row.student = student.name;
                          row.student_name = student.student_name;
                          row.group_roll_number = roll_no;
                          row.section_name =
                              frm.doc.student_group_name + " " + String.fromCharCode(65 + sec);
                  
                          roll_no++;
                          student_index++;
                      }
                  }
                  
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
    if(frm.doc.__islocal){
      let college = ""
      frappe.call({
        method: "education.academic_management.utils.get_signed_in_user_college",
        args: {"user": frappe.session.user},
        async: false,
        callback: function(r){
          if(r.message){
            frm.set_value("college", r.message)
            frm.refresh_field('college');
            college = r.message
          }
        }
      })
      frappe.call({
        method: "get_current_academic_term",
        doc: frm.doc,
        args: {"college": college},
        callback: function(r){
          if(r.message){
            frm.set_value("academic_term", r.message);
            frm.refresh_field("academic_term");
          }
        }
      })
      frm.set_query('semester', function () {
        return {
        filters: {
            session: frm.doc.academic_session,
        },
        }
      })
    }
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
        // academic_year: frm.doc.academic_year,
        college: frm.doc.college,
      },
    }
  })
})

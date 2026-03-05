// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Module", {
  setup(frm){
    frm.set_query('student_group', 'tutors', function () {
      return {
          query:
          'erpnext.controllers.queries.filter_college_programme_student_section',
          filters: {
          // program: frm.doc.programme,
          college: frm.doc.college,
          programme: frm.doc.programme,
          module: frm.doc.module,
          },
      }
  })
  frm.set_query('programme', 'colleges', function (frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    // let college = [];
    // frm.doc.colleges.forEach(function(item) {
    //     college.push(item.college);
    // });
  //   return {
  //     // query:
  //     // 'erpnext.controllers.queries.filter_college_programme_module_tutors',
  //     filters: {
  //       // program: frm.doc.progr name,
  //       docstatus: 1,
  //     },
  // }
    return {
      query:
      'erpnext.controllers.queries.get_college_programme',
    filters: {
      college: row.college,
    },
  }
})
},
	refresh(frm) {
        frm.set_query('tutor', 'tutors', function (cdt, cdn) {
          let college = [];
          frm.doc.colleges.forEach(function(item) {
              college.push(item.college);
          });
          return {
            query:
            'erpnext.controllers.queries.filter_college_programme_module_tutors',
            filters: {
              // program: frm.doc.progr name,
              college: college,
            },
        }
      })
	},
});

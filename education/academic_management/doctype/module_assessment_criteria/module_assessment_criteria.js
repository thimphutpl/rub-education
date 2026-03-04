// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Module Assessment Criteria", {
    setup(frm){
        frm.set_query("college", function () {
			return {
				filters: {
					is_group: 0,
          name: ["!=", "Office of Vice Chancellor"]
				},
			};
      
		});
    frm.set_query('semester', function () {
      return {
      filters: {
          session: frm.doc.academic_session,
      },
      }
    })
    frm.set_query('tutor', function () {
        return {
            query:
            'erpnext.controllers.queries.filter_module_tutors',
          filters: {
            // program: frm.doc.programme,
            college: frm.doc.college,
            programme: frm.doc.programme,
            module: frm.doc.module,
          },
        }
      })
      if(frm.doc.__islocal){
          frm.set_value("academic_term", undefined);
          frm.refresh_field("academic_term")
      }
    },
	refresh(frm) {
        // frm.set_query('tutor', 'tutors', function () {
        //     return {
        //       filters: {
        //         status: "Active",
        //         is_teaching_staff: 1
        //       },
        //     }
        // })
        frm.set_query('module', function () {
            return {
                query:
                'education.academic_management.doctype.annual_programme_monitoring_report.annual_programme_monitoring_report.get_program_module',
              filters: {
                // program: frm.doc.programme,
                college: frm.doc.college,
                validate: 1
              },
            }
        })
        frm.set_query('programme', function () {
            return {
              query: 'erpnext.controllers.queries.filter_college_programmes',
              filters: {
                college: frm.doc.college,
              },
            }
          })
          frm.set_query('module', function () {
            return {
              query: 'erpnext.controllers.queries.filter_college_programme_modules',
              filters: {
                college: frm.doc.college,
                programme: frm.doc.programme,
                academic_session: frm.doc.academic_session,
              },
            }
          })
        // update_refs(frm)
	},
    college(frm){
        frm.set_value("programme", undefined);
        frm.set_value("module", undefined);
        frm.refresh_fields();
    }

});

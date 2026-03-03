// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Annual Programme Monitoring Report", {
  setup(frm){
    frm.set_query("college", "cross_college_team", function(doc, cdt, cdn) {
      return {
          filters: {
              is_group: 0,
              name: ["not in", ["Office of Vice Chancellor",frm.doc.college]]
          }
      };
  });
    frappe.call({
      method: "check_reference",
      doc: frm.doc,
      callback: function(r){
        if(r.message){
          if(r.message[0] == 1 && r.message[1] == "Module Level Input"){
            frm.add_custom_button(
              __("Create "+r.message[3]),
              () => make_next_doc(frm, r.message[3], r.message[4]),
              __("Create")
            );
          }
          else if(r.message[0] == 1 && r.message[2]){
            frm.add_custom_button(
              __("Create "+r.message[3]),
              () => make_next_doc(frm, r.message[3], r.message[4]),
              __("Create")
            );
          }
        }
      }
    })
  },
	refresh(frm) {
    frm.set_query("college", function () {
			return {
				filters: {
					is_group: 0,
          name: ["!=", "Office of Vice Chancellor"]
				},
			};
		});
    frappe.call({
      method: "check_reference",
      doc: frm.doc,
      callback: function(r){
        if(r.message){
          if(r.message[0] == 1 && r.message[1] == "Module Level Input"){
            frm.add_custom_button(
              __("Create "+r.message[3]),
              () => make_next_doc(frm, r.message[3], r.message[4]),
              __("Create")
            );
          }
          else if(r.message[0] == 1 && r.message[2]){
            frm.add_custom_button(
              __("Create "+r.message[3]),
              () => make_next_doc(frm, r.message[3], r.message[4]),
              __("Create")
            );
          }
        }
      }
    })
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
        update_refs(frm)
	},
});
var make_next_doc = function (frm, next_doc, ref_field) {
  frappe.call({
    method: "validate_permitted_users",
    doc: frm.doc,
    args: {"client_side": 1},
    callback: function(r){
      if(r.message){
        frappe.throw(String(r.message))
      }
      else{
        frappe.model.open_mapped_doc({
          method: "education.academic_management.doctype.annual_programme_monitoring_report.annual_programme_monitoring_report.make_next_doc",
          frm: frm,
          args: {"next_doc": next_doc, "ref_field": ref_field}, // No default_supplier passed
        });
      }
    }
  })

}
var update_refs = function(frm){
  if(frm.doc.apmr_type == "Module Level Input"){
    frm.set_value("module_level_ref", undefined);
    frm.set_value("programme_level_ref", undefined);
    frm.set_value("college_level_ref", undefined);
  }
  else if(frm.doc.apmr_type == "Programme Level Compilation (APMR Development)"){
    frm.set_value("programme_level_ref", undefined);
    frm.set_value("college_level_ref", undefined);
  }
  else if(frm.doc.apmr_type == "College Level Review"){
    frm.set_value("module_level_ref", undefined);
    frm.set_value("college_level_ref", undefined);
  }
  else if(frm.doc.apmr_type == "University Level Review & Recommendation"){
    frm.set_value("module_level_ref", undefined);
    frm.set_value("programme_level_ref", undefined);
  }
  frm.refresh_fields()
}
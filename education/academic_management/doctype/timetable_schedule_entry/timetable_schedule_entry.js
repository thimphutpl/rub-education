frappe.ui.form.on("Timetable Schedule Entry", {

    module(frm) {
		frm.set_value("student_section", "");

        if (frm.doc.session_type === "Combined") {
            (frm.doc.combined_class || []).forEach(row => {
                frappe.model.set_value(
                    row.doctype,
                    row.name,
                    "module",
                    frm.doc.module
                );
            });
        }
    },

    combined_class_add(frm, cdt, cdn) {
        if (frm.doc.session_type === "Combined" && frm.doc.module) {
            frappe.model.set_value(
                cdt,
                cdn,
                "module",
                frm.doc.module
            );
        }
    },

	onload: function(frm) {
		if (frm.doc.session_type==""){
			frm.set_df_property("combined_class", "hidden", 1);
			frm.set_df_property("combined_class", "reqd", 0);
			frm.set_df_property("student_section", "hidden", 1);
			frm.set_df_property("student_section", "reqd", 0);
		}
	
	},


	setup(frm) {

		frm.set_query("tutor", function () {
			return {
				filters: {
					company: frm.doc.college,
					employment_status: ["not in", ["Left", "Suspended"]]
				}
			};
		});

		frm.set_query("academic_term", function () {
			return {
				filters: {
					college: frm.doc.college
				}
			};
		});

		frm.set_query("module_enrollment_key",function(){

			  return{
                query: "education.academic_management.doctype.timetable_schedule_entry.timetable_schedule_entry.get_module_enrollment_key",
				filters: {
					college:frm.doc.college,
					tutor:frm.doc.tutor,
                    module:frm.doc.module,
                    programme:frm.doc.programme
				}
			}

		})

		frm.set_query("class_room", function () {
			return {
				filters: {
					company: frm.doc.college
				}
			};
		});

		frm.set_query("programme", function () {
			return {
				query: "education.academic_management.doctype.timetable_schedule_entry.timetable_schedule_entry.get_programmes_by_college_and_tutor",
				filters: {
					college: frm.doc.college,
					tutor:frm.doc.tutor
				}
			};
		});


		frm.set_query("module", function () {
			return {
				query: "education.academic_management.doctype.timetable_schedule_entry.timetable_schedule_entry.get_modules_programme_by_tutor",
				filters: {
					college: frm.doc.college,
					programme: frm.doc.programme,
					tutor: frm.doc.tutor
				}
			};
		});

		frm.set_query("student_section", function () {
			return {
				query: "education.academic_management.doctype.timetable_schedule_entry.timetable_schedule_entry.get_student_sections",
				filters: {
					class_type: frm.doc.class_type,
					college: frm.doc.college,
					tutor: frm.doc.tutor,
					programme: frm.doc.programme,
            		module: frm.doc.module
					
				}
			};
		});

        frm.set_query("section","combined_class",function(){
            return {
				query: "education.academic_management.doctype.timetable_schedule_entry.timetable_schedule_entry.get_combined_sections",
				filters: {
                    module:frm.doc.module,
					college: frm.doc.college,
					programme: frm.doc.programme
				}
			};

        })

        frm.set_query("module","combined_class",function(){
            return {
                query: "education.academic_management.doctype.timetable_schedule_entry.timetable_schedule_entry.get_modules_programme_by_tutor",
                filters: {
                    college: frm.doc.college,
                    programme: frm.doc.programme,
                    tutor: frm.doc.tutor
                }
            };

        })

	},
	session_type: function(frm) {

		if (frm.doc.session_type === "Combined") {

			frm.set_df_property("student_section", "hidden", 1);
			frm.set_df_property("student_section", "reqd", 0);
			frm.set_df_property("combined_class","hidden",0)
			frm.set_df_property("combined_class","reqd",1)
            if (!frm.doc.combined_class?.length) { 
                let row = frm.add_child("combined_class"); 
                row.module = frm.doc.module || ""; 
                frm.refresh_field("combined_class"); 
            }

		} else if (frm.doc.session_type === "Regular") {

			frm.set_df_property("student_section", "hidden", 0);
			frm.set_df_property("student_section", "reqd", 1);
			frm.set_df_property("combined_class","reqd",0)
			frm.set_df_property("student_section", "hidden", 0);

        }else if (frm.doc.session_type === "Extra Class") {

			frm.set_df_property("student_section", "hidden", 0);
			frm.set_df_property("student_section", "reqd", 0);
			frm.set_df_property("combined_class","reqd",0)
			frm.set_df_property("student_section", "hidden", 0);
            frm.set_df_property("combined_class","hidden",0)
            frm.set_df_property("class_type","hidden",1)
            frm.set_df_property("class_type","reqd",0)
            frm.set_df_property("student_section","hidden",1)


		} else {

			frm.set_df_property("student_section", "hidden", 0);
			frm.set_df_property("student_section", "reqd", 1);

		}

	},


	college(frm) {

		frm.set_value("programme", "");
		frm.set_value("tutor", "");
		frm.set_value("module", "");
		frm.set_value("student_section", "");

		if (!frm.doc.college) {

			frm.doc.academic_term = null;
			frm.doc.academic_year = null;
			frm.doc.academic_session = null;
			frm.doc.tutor = null;
			frm.doc.class_type = null;
			frm.doc.student_section = null;
			frm.doc.module = null;
			frm.doc.from_time = null;
			frm.doc.to_time = null;
			frm.doc.day = null;
			frm.doc.tutor_name = null;
			frm.doc.module_code = null;

			frm.refresh_field("academic_term");
			frm.refresh_field("academic_year");
			frm.refresh_field("academic_session");
			frm.refresh_field("tutor");
			frm.refresh_field("class_type");
			frm.refresh_field("student_section");
			frm.refresh_field("module");
			frm.refresh_field("from_time");
			frm.refresh_field("to_time");
			frm.refresh_field("day");
			frm.refresh_field("tutor_name");
			frm.refresh_field("module_code");
		}
	},

   


	// When Programme changes
	programme(frm) {
		frm.set_value("module", "");
		frm.set_value("student_section", "");
	},


	// When Tutor changes
	tutor(frm) {
		frm.set_value("module", "");
		frm.set_value("student_section", "");
	},


	// When Class Type changes
	class_type(frm) {
		frm.set_value("student_section", "");
	}

});

frappe.ui.form.on("Combined Class Item", 
    { combined_class_add(frm, cdt, cdn) { 
        let row = locals[cdt][cdn]; 
        if (frm.doc.module) { 
            frappe.model.set_value( cdt, cdn, "module", frm.doc.module ); 
        } 
    } 
});
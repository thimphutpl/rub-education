frappe.ui.form.on("Timetable Schedule Entry", {

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

        frm.set_query("class_room", function () {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });

        frm.set_query("programme", function () {
            return {
                query: "education.academic_management.doctype.timetable_schedule_entry.timetable_schedule_entry.get_programmes_by_college",
                filters: {
                    college: frm.doc.college
                }
            };
        });

        // Module = College + Programme + Tutor
        frm.set_query("module", function () {
            return {
                query: "education.academic_management.doctype.timetable_schedule_entry.timetable_schedule_entry.get_modules_by_programme_tutor",
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
                    tutor: frm.doc.tutor
                }
            };
        });

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
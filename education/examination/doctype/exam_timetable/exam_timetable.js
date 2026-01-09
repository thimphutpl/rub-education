frappe.ui.form.on("Exam Timetable", {
    refresh(frm) {
        frm.add_custom_button(__("Upload File"), function () {
            frm.events.upload_file(frm);
        }).addClass("btn-dark");
    },

    // Upload Excel Function
    upload_file(frm) {
        if (frm.is_new()) {
            frappe.msgprint(__("Please save the document before uploading the Excel file."));
            return;
        }

        frappe.prompt(
            [
                {
                    fieldname: "excel_file",
                    fieldtype: "Attach",
                    label: "Select Excel File",
                    reqd: 1,
                },
            ],
            (data) => {
                frappe.call({
                    method: "education.examination.doctype.exam_timetable.exam_timetable.upload_excel",
                    args: {
                        file_url: data.excel_file,
                        docname: frm.doc.name,
                    },
                    freeze: true,
                    freeze_message: __("Uploading and Processing Excel..."),
                    callback: function (r) {
                        if (!r.exc) {
                            frappe.msgprint(__("Excel data has been imported successfully!"));
                            frm.reload_doc();
                        }
                    },
                });
            },
            __("Upload Excel File"),
            __("Upload")
        );
    },

    // Get Students (No confirmation)
    get_student(frm) {
        if (frm.is_new()) {
            frappe.msgprint(__("Please save the document before fetching students."));
            return;
        }

        const company = frm.doc.college;
        const academic_year = frm.doc.academic_year;
        const academic_term = frm.doc.academic_term;

        // Collect all modules from child table exam_module
        const modules = (frm.doc.exam_module || [])
            .map(row => row.module)
            .filter(m => m);

        if (!company || !academic_year || !academic_term) {
            frappe.msgprint(__("Please ensure College, Academic Year, and Academic Term are filled in before fetching students."));
            return;
        }

        if (modules.length === 0) {
            frappe.msgprint(__("No modules found in Exam Module table."));
            return;
        }

        frm.clear_table("exam_timetable_student");
        frm.refresh_field("exam_timetable_student");

        const fetchNext = (index = 0) => {
            if (index >= modules.length) {
                frappe.msgprint(__("Students added successfully for all modules."));
                frm.refresh_field("exam_timetable_student");
                return;
            }

            const module = modules[index];

            frappe.call({
                method: "education.examination.doctype.exam_timetable.exam_timetable.get_students",
                args: {
                    company: company,
                    academic_year: academic_year,
                    academic_term: academic_term,
                    module: module,
                    docname: frm.doc.name
                },
                freeze: true,
                freeze_message: __("Fetching Students for Module: {0}...", [module]),
                callback: function (r) {
                    if (r.message && r.message.length > 0) {
                        r.message.forEach((row) => {
                            let child = frm.add_child("exam_timetable_student");
                            child.student = row.student;
                            child.student_name = row.student_name;
                            child.module = row.module;
                            child.programme = row.programme || "";
                            child.examination_registration = row.examination_registration || "";
                        });
                    } else {
                        frappe.msgprint(__("No students found for Module: {0}", [module]));
                    }
                    fetchNext(index + 1);
                }
            });
        };
        fetchNext();
    }
});

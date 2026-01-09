

frappe.ui.form.on("Call For Paper", {

    onload_post_render: function (frm) {
        if ((!frm.doc.master_evaluation_criteria_call_for_paper || frm.doc.master_evaluation_criteria_call_for_paper.length === 0)) {
            fetch_master_avg_marks(frm);
        }
        frappe.call({
            method: "education.event_management.doctype.word_limit_settings.word_limit_settings.get_word_limits",
            callback: function (r) {
                if (r.message) {
                    const wordLimits = r.message;

                    // Get the child table field
                    const bioField = frm.fields_dict['brief_bio'];

                    // Set description in the DF
                    bioField.df.description = `Each author's bio must be between ${wordLimits.min_words} - ${wordLimits.max_words} words.`;

                    // Append description manually with red asterisk in the DOM
                    const $bioWrapper = $(bioField.wrapper);
                    if ($bioWrapper.length) {
                        $bioWrapper.find('.word-limit-desc').remove(); // remove old if any
                        $bioWrapper.append(`
                            <small class="word-limit-desc" style="color:#555; display:block; margin-top:4px;">
                                Each author's bio must be between ${wordLimits.min_words} - ${wordLimits.max_words} words.
                                <span style="color:red">*</span>
                            </small>
                        `);
                    }

                    // Abstract textarea description
                    const abstractField = frm.fields_dict['abstract'];
                    if (abstractField) {
                        abstractField.df.description = `Write between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words.`;
                        $(abstractField.wrapper).find('.word-limit-desc').remove();
                        $(abstractField.wrapper).append(`
                            <small class="word-limit-desc" style="color:#555; display:block; margin-top:4px;">
                                Write between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words.
                                <span style="color:red">*</span>
                            </small>
                        `);

                    }
                }
            }
        });

    },
    refresh: function (frm) {
        // Check if the user has already given marks
        frm.call("has_given_mark").then((r) => {
            if (!r.message.has_given_mark) {
                frm.toggle_display('give_marks', true);
                frm.toggle_display('view_marks', false);
            } else {
                frm.toggle_display('give_marks', false);
                frm.toggle_display('view_marks', true);
            }
        });

        // Update panel summary safely (use frm.doc + refresh_field)
        frm.call("update_panel_summary").then((r) => {
            if (!r.message) return;
            frm.doc.total_panel_member = r.message.total_panel_member;
            frm.doc.total_mark_submitted = r.message.total_mark_submitted;
            frm.doc.waiting_for_review = r.message.waiting_for_review;

            frm.refresh_field("total_panel_member");
            frm.refresh_field("total_mark_submitted");
            frm.refresh_field("waiting_for_review");
        });

        // Update total mark safely
        frm.call("calculate_total_mark").then((r) => {
            if (r.message !== undefined) {
                frm.doc.total_mark = r.message;
                frm.refresh_field("total_mark");
            }
        });

        // Fetch master evaluation criteria only if not already loaded
        if (!frm.doc.master_evaluation_criteria_call_for_paper || frm.doc.master_evaluation_criteria_call_for_paper.length === 0) {
            fetch_master_avg_marks(frm);
        }

        // Only allow certain roles to see summary fields and child table
        const allowed_roles = ["Administrator", "System Manager", "Super Admin"];
        const can_view = frappe.user_roles.some(role => allowed_roles.includes(role));

        frm.toggle_display("master_evaluation_criteria_call_for_paper", can_view);
        frm.toggle_display("total_panel_member", can_view);
        frm.toggle_display("total_mark_submitted", can_view);
        frm.toggle_display("waiting_for_review", can_view);
        frm.toggle_display("total_mark", can_view);
    },

    theme: function (frm) {
        load_rubric_based_on_theme(frm);
    },
    give_marks: function (frm) {
        frm.trigger("has_mark");
    },

    has_mark: function (frm) {
        frappe.call({
            method: "education.event_management.doctype.call_for_paper_panel_mark.call_for_paper_panel_mark.get_conference_info",
            args: {
                source_doctype: frm.doc.doctype,
                source_name: frm.doc.name
            },
            callback: function (r) {
                if (r.message) {
                    frappe.set_route(
                        "Form",
                        r.message.doctype,
                        r.message.name
                    );
                }
            }
        });
    },


    // give_marks: function (frm) {
    //     frm.events.has_mark(frm);
    // },
    // has_mark: function (frm) {
    //     method = "education.event_management.doctype.panel_mark.panel_mark.get_conference_info";
    //     return frappe.call({
    //         method: method,
    //         // args: {
    //         //     dt: frm.doc.doctype,
    //         //     dn: frm.doc.name,
    //         // },
    //         args: {
    //             source_doctype: frm.doc.doctype,
    //             source_name: frm.doc.name
    //         },
    //         callback: function (r) {
    //             if (r.message) {
    //                 var doclist = frappe.model.sync(r.message);
    //                 frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
    //             }
    //         },
    //     });
    // },
    view_marks: function (frm) {
        frm.call("has_given_mark").then(r => {
            if (r.message.has_given_mark) {
                frappe.set_route('Form', 'Call For Paper Panel Mark', r.message);
            } else {
                frappe.msgprint("No Project Formulation Grant found for this record.");
            }
        });

    },

});



// function fetch_master_avg_marks(frm) {
//     if (!frm.doc.name) return;

//     frappe.call({
//         method: "education.event_management.doctype.call_for_paper_panel_mark.call_for_paper_panel_mark.get_master_avg_marks",
//         args: { conference_name: frm.doc.name },
//         callback: function (r) {
//             if (r.message) {
//                 frm.clear_table("master_evaluation_criteria");
//                 r.message.forEach(row => {
//                     let child = frm.add_child("master_evaluation_criteria");
//                     child.criteria = row.criteria;
//                     child.avg_weight = row.avg_weight;
//                     child.avg_excellent = row.avg_excellent;
//                     child.avg_good = row.avg_good;
//                     child.avg_fair = row.avg_fair;
//                     child.avg_poor = row.avg_poor;
//                 });
//                 frm.refresh_field("master_evaluation_criteria");
//             }
//         }
//     });
// }

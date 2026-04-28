

frappe.ui.form.on("Call For Paper", {
    refresh:function(frm){
       frm.call("has_given_mark").then((r) => {
            if (!r.message.has_given_mark) {
                frm.toggle_display('give_marks', true);
                frm.toggle_display('view_marks', false);
            } else {
                frm.toggle_display('give_marks', false);
                frm.toggle_display('view_marks', true);
            }
        });
        
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
        // const allowed_roles = ["Panel Memeber"];
        const can_view = frappe.user_roles.some(role => allowed_roles.includes(role));

        frm.toggle_display("master_evaluation_criteria_call_for_paper", can_view);
        frm.toggle_display("total_panel_member", can_view);
        frm.toggle_display("first_name",can_view)
        frm.toggle_display("middle_name",can_view)
        frm.toggle_display("last_name",can_view)
        frm.toggle_display("nationality",can_view)
        frm.toggle_display("passport__cid_number",can_view)
        frm.toggle_display("email",can_view)
        frm.toggle_display("name1",can_view)
        frm.toggle_display("contact_number",can_view)
        frm.toggle_display("relationship",can_view)
        frm.toggle_display("prefix",can_view)
        frm.toggle_display("country_of_your_current_location",can_view)
        frm.toggle_display("mobile_number",can_view)
        frm.toggle_display("total_mark_submitted", can_view);
        frm.toggle_display("waiting_for_review", can_view);
        frm.toggle_display("total_mark", can_view);
        frm.trigger("set_employee_query");
         

    },

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



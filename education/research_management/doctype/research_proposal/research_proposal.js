// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Research Proposal", {
    refresh(frm) {
        update_total_word_counter(frm);
        setup_research_question_word_counter(frm);
        setup_literature_review_word_counter(frm);
        setup_word_counter(frm, "abstract", "Abstract");
        setup_word_counter(frm, "bg_and_prb_statement", "Background and Problem Statement");
        setup_word_counter_hypothesis_impact(frm, "res_q_or_hypo", "Research Questions and Hypothesis");
        setup_word_counter_hypothesis_impact(frm, "research_impact", "Research Impact");

        // // (max 1000)
        // setup_word_counter_matho(frm, "research_design", "Research Design", 1000);
        // setup_word_counter_matho(frm, "sampling_design", "Sampling Design", 1000);
        // setup_word_counter_matho(frm, "data_collection_tools_and_procedures", "Data Collection Tools", 1000);
        // setup_word_counter_matho(frm, "data_analysis_tools_and_procedures", "Data Analysis Tools", 1000);
        // setup_word_counter_matho(frm, "data_presentation", "Data Presentation", 1000);

        frm.fields_dict['researcher_details'].grid.get_field('student').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            return {
                filters: {
                    company: row.college 
                }
            };
        };
        frm.fields_dict['researcher_details'].grid.get_field('employee').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            return {
                filters: {
                    company: row.college 
                }
            };
        };
        if (!frm.doc.__islocal) {
            if (frm.doc.docstatus === 0) {
                frm.add_custom_button(__('Make Research Registration'), function() {
                    frappe.model.open_mapped_doc({
                        method: "education.research_management.doctype.research_proposal.research_proposal.make_research_registration",
                        frm: frm
                    });
                }, __('Create'));
            } 
            else if (frm.doc.docstatus === 1) {
                frm.add_custom_button(__('Make Research Project'), function() {
                    frappe.model.open_mapped_doc({
                        method: "education.research_management.doctype.research_proposal.research_proposal.make_research_project",
                        frm: frm
                    });
                }, __('Create'));
            }
        }
    },

    res_q_or_hypo(frm) {
        setup_research_question_word_counter(frm);
    },
    literature_review(frm) {
        setup_literature_review_word_counter(frm);
    },

    abstract(frm) {
        setup_word_counter(frm, "abstract", "Abstract");
    },
    bg_and_prb_statement(frm) {
        setup_word_counter(frm, "bg_and_prb_statement", "Background and Problem Statement");
    },
    res_q_or_hypo(frm) {
        setup_word_counter_hypothesis_impact(frm, "res_q_or_hypo", "Research Questions and Hypothesis");
    },
    research_impact(frm) {
        setup_word_counter_hypothesis_impact(frm, "research_impact", "Research Impact");
    },

    // research_design(frm) {
    //     setup_word_counter_matho(frm, "research_design", "Research Design", 1000);
    // },
    // sampling_design(frm) {
    //     setup_word_counter_matho(frm, "sampling_design", "Sampling Design", 1000);
    // },
    // data_collection_tools_and_procedures(frm) {
    //     setup_word_counter_matho(frm, "data_collection_tools_and_procedures", "Data Collection Tools", 1000);
    // },
    // data_analysis_tools_and_procedures(frm) {
    //     setup_word_counter_matho(frm, "data_analysis_tools_and_procedures", "Data Analysis Tools", 1000);
    // },
    // data_presentation(frm) {
    //     setup_word_counter_matho(frm, "data_presentation", "Data Presentation", 1000);
    // },
    research_design(frm) { update_total_word_counter(frm); },
    sampling_design(frm) { update_total_word_counter(frm); },
    data_collection_tools_and_procedures(frm) { update_total_word_counter(frm); },
    data_analysis_tools_and_procedures(frm) { update_total_word_counter(frm); },
    data_presentation(frm) { update_total_word_counter(frm); }


});

frappe.ui.form.on("Research Proposal Milestone Details", {
    milestone_percentage: function(frm, cdt, cdn) {
        let total = 0;

        frm.doc.research_proposal_milestone_details.forEach(row => {
            total += row.milestone_percentage || 0;
        });

        if (total > 100) {
            frappe.msgprint(__("Total milestone percentage cannot exceed 100%. Currently: {0}%".replace("{0}", total)));
            frappe.validated = false;
        }
    }
});

function setup_research_question_word_counter(frm) {
    let field = frm.fields_dict.res_q_or_hypo;

    if (!field || !field.$wrapper) return;

    // remove HTML tags
    let text = strip_html(frm.doc.res_q_or_hypo || "");

    let words = text.trim().split(/\s+/).filter(w => w.length > 0);
    let word_count = words.length;

    // remove old counter
    field.$wrapper.find('.word-count').remove();

    // add counter
    let color = (word_count > 100 || word_count < 50) ? "red" : "green";

    field.$wrapper.append(
        `<div class="word-count" style="margin-top:5px; color:${color}; font-weight:bold;">
            Word Count: ${word_count} / 100
        </div>`
    );

    // prevent typing more than 100 words
    if (word_count > 100) {
        frappe.msgprint("Maximum 100 words allowed");

        // trim to 100 words
        let trimmed = words.slice(0, 100).join(" ");
        frm.set_value("res_q_or_hypo", trimmed);
    }
}

function setup_literature_review_word_counter(frm) {
    let field = frm.fields_dict.literature_review;

    if (!field || !field.$wrapper) return;

    // remove HTML tags
    let text = strip_html(frm.doc.literature_review || "");

    let words = text.trim().split(/\s+/).filter(w => w.length > 0);
    let word_count = words.length;

    // remove old counter
    field.$wrapper.find('.word-count').remove();

    // add counter
    let color = (word_count > 600 || word_count < 500) ? "red" : "green";

    field.$wrapper.append(
        `<div class="word-count" style="margin-top:5px; color:${color}; font-weight:bold;">
            Word Count: ${word_count} / 600
        </div>`
    );

    // prevent typing more than 600 words
    if (word_count > 600) {
        frappe.msgprint("Maximum 600 words allowed");

        // trim to 600 words
        let trimmed = words.slice(0, 600).join(" ");
        frm.set_value("literature_review", trimmed);
    }
}

// helper to remove html
function strip_html(html) {
    let tmp = document.createElement("DIV");
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || "";
}


function setup_word_counter(frm, fieldname, label) {
    let field = frm.fields_dict[fieldname];

    if (!field || !field.$wrapper) return;

    let text = strip_html(frm.doc[fieldname] || "");

    let words = text.trim().split(/\s+/).filter(w => w.length > 0);
    let word_count = words.length;

    // remove old counter
    field.$wrapper.find('.word-count').remove();

    let color = (word_count > 300 || word_count < 250) ? "red" : "green";

    field.$wrapper.append(
        `<div class="word-count" style="margin-top:5px; color:${color}; font-weight:bold;">
            ${label} Word Count: ${word_count} / 300
        </div>`
    );

    // limit to 300 words
    if (word_count > 300) {
        frappe.msgprint(`${label}: Maximum 300 words allowed`);

        let trimmed = words.slice(0, 300).join(" ");
        frm.set_value(fieldname, trimmed);
    }
}

function setup_word_counter_hypothesis_impact(frm, fieldname, label) {
    let field = frm.fields_dict[fieldname];

    if (!field || !field.$wrapper) return;

    let text = strip_html(frm.doc[fieldname] || "");

    let words = text.trim().split(/\s+/).filter(w => w.length > 0);
    let word_count = words.length;

    // remove old counter
    field.$wrapper.find('.word-count').remove();

    let color = (word_count > 100 || word_count < 50) ? "red" : "green";

    field.$wrapper.append(
        `<div class="word-count" style="margin-top:5px; color:${color}; font-weight:bold;">
            ${label} Word Count: ${word_count} / 100
        </div>`
    );

    // limit to 100 words
    if (word_count > 100) {
        frappe.msgprint(`${label}: Maximum 100 words allowed`);

        let trimmed = words.slice(0, 100).join(" ");
        frm.set_value(fieldname, trimmed);
    }
}

// function update_total_word_counter(frm) {
//     let fields = [
//         "research_design",
//         "sampling_design",
//         "data_collection_tools_and_procedures",
//         "data_analysis_tools_and_procedures",
//         "data_presentation"
//     ];

//     let total_words = 0;

//     fields.forEach(field => {
//         let text = strip_html(frm.doc[field] || "");
//         let words = text.trim().split(/\s+/).filter(w => w.length > 0);
//         total_words += words.length;
//     });

//     // remove old counter
//     $('.total-word-count').remove();

//     let color = total_words > 1000 ? "red" : "green";

//     // show at top of form
//     frm.dashboard.clear_headline();
//     frm.dashboard.set_headline(
//         `<span class="total-word-count" style="color:${color}; font-weight:bold;">
//             Total Research Words: ${total_words} / 1000
//         </span>`
//     );

//     //block if exceeded
//     if (total_words > 1000) {
//         frappe.show_alert({
//             message: `Total word limit exceeded (Max 1000)`,
//             indicator: "red"
//         });
//     }
// }

function update_total_word_counter(frm) {
    let fields = [
        "research_design",
        "sampling_design",
        "data_collection_tools_and_procedures",
        "data_analysis_tools_and_procedures",
        "data_presentation"
    ];

    let total_words = 0;

    fields.forEach(field => {
        let text = strip_html(frm.doc[field] || "");
        let words = text.trim().split(/\s+/).filter(w => w.length > 0);
        total_words += words.length;
    });

    // remove old counter
    $('#sticky-word-counter').remove();

    let color = total_words > 1000 ? "red" : "green";

    // create sticky counter
    // <div id="sticky-word-counter" 
    // Total Research Words: ${total_words} / 1000
    let counter_html = `
        <div 
             style="
                position: fixed;
                top: 110px;
                right: 20px;
                z-index: 9999;
                background: white;
                padding: 10px 15px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                font-weight: bold;
                color: ${color};
             ">
        </div>
    `;

    $('body').append(counter_html);

    // block if exceeded
    if (total_words > 1000) {
        frappe.show_alert({
            message: `Total word limit exceeded (Max 1000)`,
            indicator: "red"
        });
    }
}

// function setup_word_counter_matho(frm, fieldname, label, max_words, min_words=null) {
//     let field = frm.fields_dict[fieldname];
//     if (!field || !field.$wrapper) return;

//     let text = strip_html(frm.doc[fieldname] || "");
//     let words = text.trim().split(/\s+/).filter(w => w.length > 0);
//     let word_count = words.length;

//     // remove old counter
//     field.$wrapper.find('.word-count').remove();

//     let color = "green";

//     if (word_count > max_words || (min_words && word_count < min_words)) {
//         color = "red";
//     }

//     field.$wrapper.append(
//         `<div class="word-count" style="margin-top:5px; color:${color}; font-weight:bold;">
//             ${label}: ${word_count} / ${max_words}
//         </div>`
//     );

//     // prevent exceeding max
//     if (word_count > max_words) {
//         frappe.show_alert({
//             message: `${label}: Max ${max_words} words allowed`,
//             indicator: "red"
//         });

//         let trimmed = words.slice(0, max_words).join(" ");
//         frm.set_value(fieldname, trimmed);
//     }
// }

// helper
function strip_html(html) {
    let tmp = document.createElement("DIV");
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || "";
}


// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Research Center Annual Reporting", {
    refresh(frm) {
        frm.set_query("research_center_name", function(doc) {
            return {
                filters: {
                    college: doc.college 
                }
            };
        });
        frm.clear_custom_buttons();
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button("Get Details", () => {

                if (!frm.doc.research_center_name || !frm.doc.posting_date) {
                    frappe.msgprint("Please select Research Center Name and Posting Date");
                    return;
                }

                frappe.call({
                    method: "education.research_management.doctype.research_center_annual_reporting.research_center_annual_reporting.get_policy_briefs",
                    args: {
                        research_center_name: frm.doc.research_center_name,
                        posting_date: frm.doc.posting_date
                    },
                    callback(r) {

                        if (r.message && r.message.length > 0) {
                            frm.clear_table("11_policy_briefs");

                            r.message.forEach(row => {
                                let child = frm.add_child("11_policy_briefs");
                                child.policy_briefs_title = row.policy_briefs_title;
                                child.publisher_policy_brief = row.publisher_policy_brief;
                                child.date_of_publisher = row.date_of_publisher;
                                child.remarks_policy_briefs = row.remarks_policy_briefs;
                            });

                            frm.refresh_field("11_policy_briefs");
                        } else {
                            frappe.msgprint("No Policy Briefs data found");
                        }
                    }
                });
                frappe.call({
                    method: "education.research_management.doctype.research_center_annual_reporting.research_center_annual_reporting.get_journals",
                    args: {
                        research_center_name: frm.doc.research_center_name,
                        posting_date: frm.doc.posting_date
                    },
                    callback(r) {
                        if (r.message && r.message.length > 0) {

                            frm.clear_table("12_journals");

                            r.message.forEach(row => {
                                let child = frm.add_child("12_journals");
                                child.name_of_the_journal = row.name_of_the_journal;
                                child.vol_no_journal = row.vol_no_journal;
                                child.issue_no_journal = row.issue_no_journal;
                                child.website_links_journal = row.website_links_journal;
                                child.year = row.year;
                            });

                            frm.refresh_field("12_journals");
                        }
                    }
                });
                frappe.call({
                    method: "education.research_management.doctype.research_center_annual_reporting.research_center_annual_reporting.get_research_articles",
                    args: {
                        research_center_name: frm.doc.research_center_name,
                        posting_date: frm.doc.posting_date
                    },
                    callback(r) {
                        if (r.message && r.message.length > 0) {
                
                            frm.clear_table("table_rad");
                
                            r.message.forEach(row => {
                                let child = frm.add_child("table_rad");
                                child.research_articles_title = row.research_articles_title;
                                child.publisher = row.publisher;
                                child.website_link_articles = row.website_link_articles;
                                child.year = row.year;
                                child.author_student = row.students.join(", ");   
                                child.author_employee = row.employees.join(", ");
                            });
                
                            frm.refresh_field("table_rad");
                        } else {
                            frappe.msgprint("No Research Articles found");
                        }
                    }
                });
                frappe.call({
                    method: "education.research_management.doctype.research_center_annual_reporting.research_center_annual_reporting.get_conference_seminar_paper",
                    args: {
                        research_center_name: frm.doc.research_center_name,
                        posting_date: frm.doc.posting_date
                    },
                    callback(r) {
                        if (r.message && r.message.length > 0) {
                
                            frm.clear_table("conference_seminar_paper"); 
                
                            r.message.forEach(row => {
                                let child = frm.add_child("conference_seminar_paper");
                                child.conference_seminar_paper_title = row.conference_seminar_paper_title;
                                child.conferenceseminar_title = row.conferenceseminar_title;
                                child.date = row.date;
                                child.nationalinternational = row.nationalinternational;
                                child.author_student = row.students.join(", ");   
                                child.author_employee = row.employees.join(", "); 
                            });
                
                            frm.refresh_field("conference_seminar_paper");
                        } else {
                            frappe.msgprint("No Conference/Seminar Paper found");
                        }
                    }
                });
                frappe.call({
                    method: "education.research_management.doctype.research_center_annual_reporting.research_center_annual_reporting.get_books_chapter",
                    args: {
                        research_center_name: frm.doc.research_center_name,
                        posting_date: frm.doc.posting_date
                    },
                    callback(r) {
                        if (r.message && r.message.length > 0) {
                
                            frm.clear_table("book_chapters"); 
                
                            r.message.forEach(row => {
                                let child = frm.add_child("book_chapters");
                                child.book_chapter_title = row.book_chapter_title;
                                child.book_title = row.book_title;
                                child.publishers = row.publishers;
                                child.website_link_books = row.website_link_books;
                                child.author_student = row.students.join(", ");  
                                child.author_employee = row.employees.join(", "); 
                            });
                
                            frm.refresh_field("book_chapters");
                        } else {
                            frappe.msgprint("No Book Chapters found");
                        }
                    }
                });
                
                
                
                frappe.call({
                    method: "education.research_management.doctype.research_center_annual_reporting.research_center_annual_reporting.get_training_workshop_organized",
                    args: {
                        research_center_name: frm.doc.research_center_name,
                        posting_date: frm.doc.posting_date
                    },
                    callback(r) {
                        if (r.message && r.message.length > 0) {
                            frm.clear_table("training_workshop_organized");
                
                            r.message.forEach(row => {
                                let child = frm.add_child("training_workshop_organized");
                                child.trainings_organized_title = row.trainings_organized_title;
                                child.employee = row.employee.join(", ");
                                child.no_of_staffs_engaged = row.no_of_staffs_engaged;
                                child.no_of_student_engaged = row.no_of_student_engaged;
                                child.no_of_external_participants = row.no_of_external_participants;
                                child.venue = row.venue;
                                child.date = row.date;
                                child.funding_source = row.funding_source;
                                child.remarks = row.remarks;
                            });
                
                            frm.refresh_field("training_workshop_organized");
                        } else {
                            frappe.msgprint("No Training/Workshop data found");
                        }
                    }
                });

                frappe.call({
                    method: "education.research_management.doctype.research_center_annual_reporting.research_center_annual_reporting.get_research_event_organized",
                    args: {
                        research_center_name: frm.doc.research_center_name,
                        posting_date: frm.doc.posting_date
                    },
                    callback(r) {
                        if (r.message && r.message.length > 0) {
                            frm.clear_table("table_gumb");
                            r.message.forEach(row => {
                                let child = frm.add_child("table_gumb");
                                child.research_event_organized_title = row.research_event_organized_title;
                                child.no_of_staffs_engageds = row.no_of_staffs_engageds;
                                child.no_of_student_engageds = row.no_of_student_engageds;
                                child.no_of_external_participantss = row.no_of_external_participantss;
                                child.venues = row.venues;
                                child.funding_sources = row.funding_sources;
                                child.remarkss = row.remarkss;
                            });
                
                            frm.refresh_field("table_gumb");
                        } else {
                            frappe.msgprint("No Research Event Organized data found");
                        }
                    }
                });
                
                
                frappe.call({
                    method: "education.research_management.doctype.research_center_annual_reporting.research_center_annual_reporting.get_research_projects_funding",
                    args: {
                        research_center_name: frm.doc.research_center_name,
                        posting_date: frm.doc.posting_date
                    },
                    callback(r) {
                        if (r.message && r.message.length > 0) {
                
                            frm.clear_table("table_drxe");
                
                            r.message.forEach(row => {
                                let child = frm.add_child("table_drxe");
                
                                child.project_title = row.project_title;
                                child.funding_agency_nameinstitution = row.funding_agency_nameinstitution;
                                child.country = row.country;
                                child.application_amount = row.application_amount;
                                child.funding_secured = row.funding_secured;
                                child.is_joint_research = row.is_joint_research;
                                child.secured_amount = row.secured_amount;
                                child.grant_in_kind = row.grant_in_kind;
                                child.project_completed = row.project_completed;
                                child.principal = row.principal?.join(", ") || "";
                                child.co = row.employees?.join(", ") || "";
                            });
                
                            frm.refresh_field("table_drxe");
                
                        } else {
                            frappe.msgprint("No Research Projects and Funding data found");
                        }
                    }
                });
                
                



            });
        }
    }
});

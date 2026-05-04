// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Research Center Reporting Items", {
	refresh(frm) {
        frm.set_query("research_center_name", function(doc) {
            return {
                filters: {
                    college: doc.college 
                }
            };
        });
        frm.set_query("sub_reporting_type", function (doc) {
			return {
				filters: { parent_task: doc.reporting_type },
			};
		});
	},
    sub_reporting_type(frm) {
		// Clear previous mandatory settings
		clear_mandatory_fields(frm);
		
		// Set new mandatory fields based on selection
		set_mandatory_fields(frm);
	},
	
	// Optional: Add validation before save
	before_save(frm) {
		return validate_mandatory_fields_client(frm);
	}
});

function clear_mandatory_fields(frm) {
	// Clear all field mandatory settings
	let all_fields = [
		"year", "research_articles_title", "publisher", "website_link_articles",
		"name_of_the_journal", "vol_no_journal", "issue_no_journal", "website_links_journal",
		"title", "conferenceseminar_title", "date", "nationalinternational",
		"book_chapter_title", "book_title", "publishers", "website_link_books",
		"trainings_organized_title", "no_of_staffs_engaged", "no_of_student_engaged",
		"no_of_external_participants", "venues", "funding_source",
		"research_event_organized_title", "no_of_staffs_engageds", "no_of_student_engageds",
		"funding_sources"
	];
	
	all_fields.forEach(field => {
		frm.fields_dict[field] && frm.set_df_property(field, "reqd", 0);
	});
}

function set_mandatory_fields(frm) {
	let sub_type = frm.doc.sub_reporting_type;
	
	if (!sub_type) return;
	
	switch(sub_type) {
		case "Research Articles":
			frm.set_df_property("year", "reqd", 1);
			frm.set_df_property("research_articles_title", "reqd", 1);
			frm.set_df_property("publisher", "reqd", 1);
			frm.set_df_property("website_link_articles", "reqd", 1);
			break;
			
		case "Journals":
			frm.set_df_property("year", "reqd", 1);
			frm.set_df_property("name_of_the_journal", "reqd", 1);
			frm.set_df_property("vol_no_journal", "reqd", 1);
			frm.set_df_property("issue_no_journal", "reqd", 1);
			frm.set_df_property("website_links_journal", "reqd", 1);
			break;
			
		case "Conference Seminar Paper":
			frm.set_df_property("year", "reqd", 1);
			frm.set_df_property("title", "reqd", 1);
			frm.set_df_property("conferenceseminar_title", "reqd", 1);
			frm.set_df_property("date", "reqd", 1);
			frm.set_df_property("nationalinternational", "reqd", 1);
			break;
			
		case "Book Chapters":
			frm.set_df_property("year", "reqd", 1);
			frm.set_df_property("book_chapter_title", "reqd", 1);
			frm.set_df_property("book_title", "reqd", 1);
			frm.set_df_property("publishers", "reqd", 1);
			frm.set_df_property("website_link_books", "reqd", 1);
			break;
			
		case "Training and workshop":
			frm.set_df_property("year", "reqd", 1);
			frm.set_df_property("trainings_organized_title", "reqd", 1);
			frm.set_df_property("no_of_staffs_engaged", "reqd", 1);
			frm.set_df_property("no_of_student_engaged", "reqd", 1);
			frm.set_df_property("no_of_external_participants", "reqd", 1);
			frm.set_df_property("venues", "reqd", 1);
			frm.set_df_property("funding_source", "reqd", 1);
			break;
			
		case "Research Event Organized":
			frm.set_df_property("year", "reqd", 1);
			frm.set_df_property("research_event_organized_title", "reqd", 1);
			frm.set_df_property("no_of_staffs_engageds", "reqd", 1);
			frm.set_df_property("no_of_student_engageds", "reqd", 1);
			frm.set_df_property("no_of_external_participants", "reqd", 1);
			frm.set_df_property("venues", "reqd", 1);
			frm.set_df_property("funding_sources", "reqd", 1);
			break;
	}
	
	// Refresh the form to show asterisks
	frm.refresh();
}

function validate_mandatory_fields_client(frm) {
	let sub_type = frm.doc.sub_reporting_type;
	let missing_fields = [];
	
	if (!sub_type) return true;
	
	switch(sub_type) {
		case "Research Articles":
			if (!frm.doc.year) missing_fields.push("Year");
			if (!frm.doc.research_articles_title) missing_fields.push("Research Articles Title");
			if (!frm.doc.publisher) missing_fields.push("Publisher");
			if (!frm.doc.website_link_articles) missing_fields.push("Website Link");
			break;
			
		case "Journals":
			if (!frm.doc.year) missing_fields.push("Year");
			if (!frm.doc.name_of_the_journal) missing_fields.push("Name of the Journal");
			if (!frm.doc.vol_no_journal) missing_fields.push("Volume No");
			if (!frm.doc.issue_no_journal) missing_fields.push("Issue No");
			if (!frm.doc.website_links_journal) missing_fields.push("Website Link");
			break;
			
		case "Conference Seminar Paper":
			if (!frm.doc.year) missing_fields.push("Year");
			if (!frm.doc.title) missing_fields.push("Title");
			if (!frm.doc.conferenceseminar_title) missing_fields.push("Conference/Seminar Title");
			if (!frm.doc.date) missing_fields.push("Date");
			if (!frm.doc.nationalinternational) missing_fields.push("National/International");
			break;
			
		case "Book Chapters":
			if (!frm.doc.year) missing_fields.push("Year");
			if (!frm.doc.book_chapter_title) missing_fields.push("Book Chapter Title");
			if (!frm.doc.book_title) missing_fields.push("Book Title");
			if (!frm.doc.publishers) missing_fields.push("Publisher");
			if (!frm.doc.website_link_books) missing_fields.push("Website Link");
			break;
			
		case "Training and workshop":
			if (!frm.doc.year) missing_fields.push("Year");
			if (!frm.doc.trainings_organized_title) missing_fields.push("Training Title");
			if (!frm.doc.no_of_staffs_engaged) missing_fields.push("No of Staffs Engaged");
			if (!frm.doc.no_of_student_engaged) missing_fields.push("No of Students Engaged");
			if (!frm.doc.no_of_external_participants) missing_fields.push("No of External Participants");
			if (!frm.doc.venues) missing_fields.push("Venue");
			if (!frm.doc.funding_source) missing_fields.push("Funding Source");
			break;
			
		case "Research Event Organized":
			if (!frm.doc.year) missing_fields.push("Year");
			if (!frm.doc.research_event_organized_title) missing_fields.push("Research Event Title");
			if (!frm.doc.no_of_staffs_engageds) missing_fields.push("No of Staffs Engaged");
			if (!frm.doc.no_of_student_engageds) missing_fields.push("No of Students Engaged");
			if (!frm.doc.no_of_external_participants) missing_fields.push("No of External Participants");
			if (!frm.doc.venues) missing_fields.push("Venue");
			if (!frm.doc.funding_sources) missing_fields.push("Funding Source");
			break;
	}
	
	if (missing_fields.length > 0) {
		frappe.msgprint({
			title: __('Missing Mandatory Fields'),
			message: __('The following fields are mandatory for {0}:<br><br>{1}', 
				[sub_type, missing_fields.join("<br>")]),
			indicator: 'red'
		});
		return false;
	}
	
	return true;
}
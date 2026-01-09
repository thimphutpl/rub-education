frappe.ready(function () {
	const params = new URLSearchParams(window.location.search);
	const route_options = params.get("route_options");
	console.log('Route options1:', route_options);
	let wordLimits = {
		min_revise_abstract: 0,
		max_revise_abstract: 0
	};
	frappe.call({
		method: "education.event_management.doctype.word_limit_settings.word_limit_settings.get_word_limits",
		callback: function (r) {
			if (r.message) {

				wordLimits.min_revise_abstract = r.message.min_revise_abstract;
				wordLimits.max_revise_abstract = r.message.max_revise_abstract;


				// Abstract description
				const $abstractField = $('textarea[data-fieldname="revise_abstract"]');
				console.log('Abstract field element:', $abstractField);
				if ($abstractField.next('.word-limit-desc').length === 0) {
					$abstractField.after(`<small class="word-limit-desc" style="color: #555;">Write between ${wordLimits.min_revise_abstract} - ${wordLimits.max_revise_abstract} words.</small>  <span style="color:red">*</span>`);
				} else {
					$abstractField.next('.word-limit-desc').text(`Write between ${wordLimits.min_revise_abstract} - ${wordLimits.max_revise_abstract} words.`);
				}

			}
		}
	});



	if (route_options) {
		const opts = JSON.parse(decodeURIComponent(route_options));
		frappe.web_form.set_value("conference", opts.conference);
		frappe.web_form.set_value("theme", opts.theme);
		frappe.web_form.set_value("prefix", opts.prefix);
		frappe.web_form.set_value("first_name", opts.first_name);
		frappe.web_form.set_value("middle_name", opts.middle_name);
		frappe.web_form.set_value("last_name", opts.last_name);
		frappe.web_form.set_value("nationality", opts.nationality);
		frappe.web_form.set_value("passport__cid_number", opts.passport__cid_number);
		frappe.web_form.set_value("country_of_your_current_location", opts.country_of_your_current_location);
		frappe.web_form.set_value("organisation", opts.organisation);
		frappe.web_form.set_value("current_position", opts.current_position);
		frappe.web_form.set_value("email", opts.email);
		frappe.web_form.set_value("mobile_number", opts.mobile_number);
		frappe.web_form.set_value("name1", opts.name1);
		frappe.web_form.set_value("contact_number", opts.contact_number);
		frappe.web_form.set_value("relationship", opts.relationship);
		frappe.web_form.set_value("title", opts.title);
		frappe.web_form.set_value("affiliation", opts.affiliation);
		frappe.web_form.set_value("brief_bio_of_the_authors", opts.brief_bio_of_the_authors);
		frappe.web_form.set_value("abstract", opts.abstract);
		if (Array.isArray(opts.author_name)) {


			const authorField = frappe.web_form.fields_dict['author_name'];
			authorField.df.data = []; // clear existing rows
			authorField.grid.grid_rows.forEach(r => r.remove()); // remove grid rows

			opts.author_name.forEach((row, idx) => {

				authorField.grid.add_new_row();
				const newRow = authorField.grid.get_row(authorField.grid.grid_rows.length - 1);
				newRow.doc.name1 = row.name1;
				newRow.refresh(); // refresh the new row
			});

			authorField.grid.refresh();
		}
		if (Array.isArray(opts.author_details)) {
			const bioField = frappe.web_form.fields_dict['brief_bio']; // use correct child table fieldname
			bioField.df.data = []; // clear existing rows
			bioField.grid.grid_rows.forEach(r => r.remove()); // remove existing grid rows

			opts.author_details.forEach((row, idx) => {

				bioField.grid.add_new_row();
				const newRow = bioField.grid.get_row(bioField.grid.grid_rows.length - 1);
				newRow.doc.brief_bio_of_the_authors = row.brief_bio_of_the_authors;
				newRow.refresh();
			});

			;
			bioField.grid.refresh();
		}

	}
	function getWordCount(text) {
		return text.trim().split(/\s+/).filter(w => w).length;
	}

	// Intercept the submit button click instead of form submission
	$('form button[type="submit"]').on('click', function (e) {
		e.preventDefault();
		e.stopImmediatePropagation();

		console.log('Button clicked - starting duplicate check');

		const email = frappe.web_form.get_value("email");
		// const conference = frappe.web_form.get_value("conference");
		const theme = frappe.web_form.get_value("theme");
		const prefix = frappe.web_form.get_value("prefix");
		const $btn = $(this);
		// console.log("Conference:", conference);


		// $btn.prop('disabled', true).html('Checking...');
		const abstractText = $('textarea[data-fieldname="revise_abstract"]').val() || "";
		// const bioCount = getWordCount(bioText);
		const abstractCount = getWordCount(abstractText);
		if (abstractCount < wordLimits.min_revise_abstract || abstractCount > wordLimits.max_revise_abstract) {
			frappe.msgprint(`Revised Abstract must have between ${wordLimits.min_revise_abstract} - ${wordLimits.max_revise_abstract} words. Current words: ${abstractCount}`);
			return false;
		}
		if (abstractCount > wordLimits.max_revise_abstract) {
			frappe.msgprint(`Revised Abstract must not exceed ${wordLimits.max_revise_abstract} words. Current words: ${abstractCount}`);
			return false;
		}

		// Make synchronous-like call using async/await
		frappe.call({
			method: "education.event_management.web_form.full_paper.full_paper.check_duplicate_registration",
			args: {
				// doctype: "Full Paper",
				// filters: [
				// 	// ["email", "=", email],
				// 	["conference", "=", conference]
				// ],
				// conference: conference,
				email: email,
				name: frappe.web_form.doc.name
				// fields: ["name"],
				// limit: 1
			},
			callback: function (r) {
				console.log('Duplicate check result:', r.message);

				if (r.message.exists) {
					console.log('Blocking submission - duplicate found');
					frappe.msgprint("You are already registered for this full paper.");
					$btn.prop('disabled', false).html('Submit');
				} else {
					$btn.prop('disabled', false).html('Submit');
					// Submit the form
					$('form').submit();
					setTimeout(function () {
						window.location.href = '/abstract-review-status-check';
					}, 1000);
				}
			}
		});

		return false;
	});
});
frappe.ready(function () {


	const params = new URLSearchParams(window.location.search);
	const route_options = params.get("route_options");
	let wordLimits = {
		min_words: 0,
		max_words: 0,
		min_abstract: 0,
		max_abstract: 0
	};
	frappe.call({
		method: "education.event_management.doctype.word_limit_settings.word_limit_settings.get_word_limits",
		callback: function (r) {
			if (r.message) {
				wordLimits.min_words = r.message.min_words;
				wordLimits.max_words = r.message.max_words;
				wordLimits.min_abstract = r.message.min_abstract;
				wordLimits.max_abstract = r.message.max_abstract;
				const bioField = frappe.web_form.fields_dict['brief_bio'];

				bioField.df.description = `Each author's bio must be between ${wordLimits.min_words} - ${wordLimits.max_words} words.`;


				// Append description to the table label in the DOM
				const $bioWrapper = $(bioField.wrapper);
				console.log('Bio wrapper element:', $bioWrapper);
				if ($bioWrapper.length) {
					$bioWrapper.find('.word-limit-desc').remove();
					$bioWrapper.append(
						`<small class="word-limit-desc" style="color:#555; display:block; margin-top:4px;">
                    Each author's bio must be between ${wordLimits.min_words} - ${wordLimits.max_words} words.
					  <span style="color:red">*</span>
                </small>`
					);
				}

				// Abstract description
				const $abstractField = $('textarea[data-fieldname="abstract"]');
				if ($abstractField.next('.word-limit-desc').length === 0) {
					$abstractField.after(`<small class="word-limit-desc" style="color: #555;">Write between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words.</small>  <span style="color:red">*</span>`);
				} else {
					$abstractField.next('.word-limit-desc').text(`Write between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words.`);
				}

			}
		}
	});


	if (route_options) {
		const opts = JSON.parse(decodeURIComponent(route_options));
		frappe.web_form.set_value("conference", opts.conference);
		frappe.web_form.set_value("theme", opts.theme);
	}
	function getWordCount(text) {
		return text.trim().split(/\s+/).filter(w => w).length;
	}

	// Intercept the submit button click instead of form submission
	$('form button[type="submit"]').on('click', function (e) {
		e.preventDefault();
		e.stopImmediatePropagation();



		const email = frappe.web_form.get_value("email");
		const conference = frappe.web_form.get_value("conference");
		const title = frappe.web_form.get_value("title");
		const theme = frappe.web_form.get_value("theme");

		// console.log('Checking for conference:', conference, 'and theme:', theme);
		const $btn = $(this);

		if (!email || !conference) {
			frappe.msgprint("Please fill in both email and conference.");
			return false;
		}
		if (!title) {
			frappe.msgprint("Please fill in the title of the paper.");
			return false;
		}

		// const bioText = $('textarea[data-fieldname="brief_bio_of_the_authors"]').val() || "";
		const abstractText = $('textarea[data-fieldname="abstract"]').val() || "";
		// const bioCount = getWordCount(bioText);
		const abstractCount = getWordCount(abstractText);

		const bioField = frappe.web_form.fields_dict['brief_bio'];

		// Loop through each row
		for (let row of bioField.grid.get_data()) {
			const bioText = row.brief_bio_of_the_authors || "";
			const wordCount = bioText.trim().split(/\s+/).filter(w => w).length;

			if (!bioText) {
				frappe.msgprint(`Please fill in the brief bio for each author.`);
				return false; // stop submission
			}

			if (wordCount < wordLimits.min_words || wordCount > wordLimits.max_words) {
				frappe.msgprint(`Each author's bio must be between ${wordLimits.min_words} and ${wordLimits.max_words} words. Current words: ${wordCount}`);
				return false; // stop submission
			}
			if (wordCount > wordLimits.max_words) {
				frappe.msgprint(`Each author's bio must not exceed ${wordLimits.max_words} words. Current words: ${wordCount}`);
				return false;
			}
		}

		if (abstractCount < wordLimits.min_abstract || abstractCount > wordLimits.max_abstract) {
			frappe.msgprint(`Abstract must have between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words. Current words: ${abstractCount}`);
			return false;
		}
		if (abstractCount > wordLimits.max_abstract) {
			frappe.msgprint(`Abstract must not exceed ${wordLimits.max_abstract} words. Current words: ${abstractCount}`);
			return false;
		}

		$btn.prop('disabled', true).html('Checking...');

		// Make synchronous-like call using async/await
		frappe.call({
			method: "education.event_management.web_form.call_for_paper.call_for_paper.check_duplicate_registration",
			args: {
				email: email,
				conference: conference
			},
			callback: function (r) {
				if (r.message.exists) {
					// console.log('Blocking submission - duplicate found');
					frappe.msgprint("You are already registered for this conference.");
					$btn.prop('disabled', false).html('Submit');
				} else {
					$btn.prop('disabled', false).html('Submit');
					// frappe.web_form.doc.workflow_state = "Waiting for Review";
					$('form').submit();
					setTimeout(function () {
						window.location.href = '/conference-announcement';
					}, 1000);
				}
			}
		});

		return false;
	});
	const authorField = frappe.web_form.fields_dict['author_name'];
	const bioField = frappe.web_form.fields_dict['brief_bio'];
	if (!authorField || !bioField) return;
	const authorGrid = authorField.grid;
	const bioGrid = bioField.grid;
	const originalAddNewRow = authorGrid.add_new_row.bind(authorGrid);
	authorGrid.add_new_row = function ($row, idx) {
		originalAddNewRow($row, idx);
		let row_idx = authorGrid.data.length - 1;
		bioGrid.add_new_row();
		bioGrid.refresh();
	};

});
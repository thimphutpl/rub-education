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

				// Brief Bio description
				const $bioField = $('textarea[data-fieldname="brief_bio_of_the_authors"]');
				if ($bioField.next('.word-limit-desc').length === 0) {
					$bioField.after(`<small class="word-limit-desc" style="color: #555;">Write between ${wordLimits.min_words} - ${wordLimits.max_words} words.</small>`);
				} else {
					$bioField.next('.word-limit-desc').text(`Write between ${wordLimits.min_words} - ${wordLimits.max_words} words.`);
				}

				// Abstract description
				const $abstractField = $('textarea[data-fieldname="abstract"]');
				if ($abstractField.next('.word-limit-desc').length === 0) {
					$abstractField.after(`<small class="word-limit-desc" style="color: #555;">Write between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words.</small>`);
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
		const theme = frappe.web_form.get_value("theme");

		// console.log('Checking for conference:', conference, 'and theme:', theme);
		const $btn = $(this);

		if (!email || !conference) {
			frappe.msgprint("Please fill in both email and conference.");
			return false;
		}

		const bioText = $('textarea[data-fieldname="brief_bio_of_the_authors"]').val() || "";
		const abstractText = $('textarea[data-fieldname="abstract"]').val() || "";
		const bioCount = getWordCount(bioText);
		const abstractCount = getWordCount(abstractText);


		if (bioCount < wordLimits.min_words) {
			frappe.msgprint(`Brief Bio must have at least ${wordLimits.min_words} words. Current words: ${bioCount}`);
			return false;
		}
		if (bioCount > wordLimits.max_words) {
			frappe.msgprint(`Brief Bio must not exceed ${wordLimits.max_words} words. Current words: ${bioCount}`);
			return false;
		}
		if (abstractCount < wordLimits.min_abstract) {
			frappe.msgprint(`Abstract must have at least ${wordLimits.min_abstract} words. Current words: ${abstractCount}`);
			return false;
		}
		if (abstractCount > wordLimits.max_abstract) {
			frappe.msgprint(`Abstract must not exceed ${wordLimits.max_abstract} words. Current words: ${abstractCount}`);
			return false;
		}

		$btn.prop('disabled', true).html('Checking...');

		// Make synchronous-like call using async/await
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Conference Registration",
				filters: [
					["email", "=", email],
					["conference", "=", conference]
				],
				fields: ["name"],

				limit: 1
			},
			callback: function (r) {
				console.log('Duplicate check result:', r.message);

				if (r.message && r.message.length > 0) {
					console.log('Blocking submission - duplicate found');
					frappe.msgprint("You are already registered for this conference.");
					$btn.prop('disabled', false).html('Submit');
				} else {
					$btn.prop('disabled', false).html('Submit');
					$('form').submit();
					// setTimeout(function () {
					// 	window.location.href = '/conference-announcement';
					// }, 1000);
				}
			}
		});

		return false;
	});
});
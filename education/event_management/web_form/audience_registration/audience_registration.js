frappe.ready(function () {
	const params = new URLSearchParams(window.location.search);
	const route_options = params.get("route_options");

	if (route_options) {
		const opts = JSON.parse(decodeURIComponent(route_options));
		frappe.web_form.set_value("full_paper", opts.event);
	}


	// Intercept the submit button click instead of form submission
	// $('form button[type="submit"]').on('click', function (e) {
	// 	e.preventDefault();
	// 	e.stopImmediatePropagation();

	// 	console.log('Button clicked - starting duplicate check');

	// 	const email = frappe.web_form.get_value("email_address");
	// 	const event = frappe.web_form.get_value("full_paper");
	// 	const $btn = $(this);
	// 	is_submitting = true;

	// 	// if (!event) {
	// 	// 	frappe.msgprint("Please fill in both email and event.");
	// 	// 	return false;
	// 	// }

	// 	// $btn.prop('disabled', true).html('Checking...');

	// 	// Make synchronous-like call using async/await
	// 	frappe.call({
	// 		method: "education.event_management.web_form.audience_registration.audience_registration.check_duplicate_registration",
	// 		args: {
	// 			full_paper: event,
	// 			email: email
	// 		},
	// 		callback: function (r) {
	// 			if (r.message.status === "duplicate") {
	// 				alert("hi")
	// 				frappe.msgprint("You are already registered for this full paper.");
	// 				is_submitting = false;
	// 				// $btn.prop('disabled', false).html('Submit');
	// 			} else {
	// 				alert("hi11")
	// 				// $btn.prop('disabled', false).html('Submit');
	// 				// Submit the form
	// 				$('form').submit();
	// 				setTimeout(function () {
	// 					window.location.href = '/events';
	// 				}, 1000);
	// 			}
	// 		}
	// 	});

	// return false;
	// });

	let is_submitting = false;

	$('form button[type="submit"]').on('click', function (e) {

		if (is_submitting) return;

		e.preventDefault();

		is_submitting = true;

		const email = frappe.web_form.get_value("email_address");
		const event = frappe.web_form.get_value("full_paper");

		frappe.call({
			method: "education.event_management.web_form.audience_registration.audience_registration.check_duplicate_registration",
			args: {
				full_paper: event,
				email: email
			}
		}).then(r => {

			if (r.message && r.message.status === "duplicate") {
				frappe.msgprint(" " + r.message.message);
				is_submitting = false;
			} else {
				$('form').submit();
				setTimeout(function () {
					window.location.href = '/events';
				}, 1000);
			}

		});

	});
});
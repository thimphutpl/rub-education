frappe.ready(function () {
	const params = new URLSearchParams(window.location.search);
	const route_options = params.get("route_options");

	if (route_options) {
		const opts = JSON.parse(decodeURIComponent(route_options));
		frappe.web_form.set_value("full_paper", opts.event);
	}


	// Intercept the submit button click instead of form submission
	$('form button[type="submit"]').on('click', function (e) {
		e.preventDefault();
		e.stopImmediatePropagation();

		console.log('Button clicked - starting duplicate check');

		const email = frappe.web_form.get_value("email");
		const event = frappe.web_form.get_value("full_paper");
		const $btn = $(this);

		// if (!event) {
		// 	frappe.msgprint("Please fill in both email and event.");
		// 	return false;
		// }

		$btn.prop('disabled', true).html('Checking...');

		// Make synchronous-like call using async/await
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Audience Registration",
				filters: [
					// ["email", "=", email],
					["full_paper", "=", event]
				],
				fields: ["name"],
				limit: 1
			},
			callback: function (r) {
				console.log('Duplicate check result:', r.message);

				if (r.message && r.message.length > 0) {
					console.log('Blocking submission - duplicate found');
					frappe.msgprint("You are already registered for this full paper.");
					$btn.prop('disabled', false).html('Submit');
				} else {
					$btn.prop('disabled', false).html('Submit');
					// Submit the form
					$('form').submit();
					setTimeout(function () {
						window.location.href = '/events';
					}, 1000);
				}
			}
		});

		return false;
	});
});
frappe.ready(function () {

	// Read event from URL query string
	const params = new URLSearchParams(window.location.search);
	const route_options = params.get("route_options");
	console.log("route_option:", route_options)

	if (route_options) {
		const opts = JSON.parse(decodeURIComponent(route_options));
		frappe.web_form.set_value("event", opts.event);
	}
	frappe.web_form.on('faculty_email', function (value) {
		if (!value) {
			frappe.web_form.set_value('faculty_name', '');
			return;
		}
		const email = value.doc.faculty_email;
		console.log(email)
		// Call server-side whitelisted method
		frappe.call({
			method: "education.event_management.web_form.event_registration.event_registration.get_user_full_name",
			args: { email: email },
			callback: function (r) {
				frappe.web_form.set_value('faculty_name', r.message || '');
			}
		});
	});
});

frappe.ready(function () {
	alert("hi")
	// wait for Web Form fields to render
	frappe.web_form.after_load = function () {
		// Get 'event' parameter from URL
		const urlParams = new URLSearchParams(window.location.search);
		const event_param = urlParams.get('event');

		if (event_param) {
			// Find the Event input field
			const eventField = document.querySelector('input[data-fieldname="event"]');
			if (eventField) {
				eventField.value = event_param;

				// Trigger change so ERPNext picks up the value
				eventField.dispatchEvent(new Event('change'));
			}
		}
	};
});

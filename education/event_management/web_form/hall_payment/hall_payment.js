frappe.ready(function () {
	const params = new URLSearchParams(window.location.search);
	const route_options = params.get("route_options");

	if (route_options) {
		const opts = JSON.parse(decodeURIComponent(route_options));
		frappe.web_form.set_value("venue", opts.venue);
		frappe.web_form.set_value("company", opts.company);
		frappe.web_form.set_value("branch", opts.branch);
		frappe.web_form.set_value("cost_center", opts.cost_center);
		frappe.web_form.set_value("email", opts.email);
		frappe.web_form.set_value("name1", opts.name1);
		frappe.web_form.set_value("dzongkhag", opts.dzongkhag);
		frappe.web_form.set_value("country", opts.country);
		frappe.web_form.set_value("organization", opts.organization);
		frappe.web_form.set_value("designation", opts.designation);
		frappe.web_form.set_value("amount", opts.amount);
		frappe.web_form.set_value("total_days", opts.total_days);
		frappe.web_form.set_value("total_amount", opts.total_amount);



	}
	frappe.web_form.get_field("total_days").df.read_only = 1;
	frappe.web_form.get_field("total_amount").df.read_only = 1;
	frappe.web_form.get_field("amount").df.read_only = 1;
	frappe.web_form.refresh();



})	
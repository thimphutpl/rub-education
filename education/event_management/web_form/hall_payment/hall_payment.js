// frappe.ready(function () {
// 	const params = new URLSearchParams(window.location.search);
// 	const route_options = params.get("route_options");

// 	if (route_options) {
// 		const opts = JSON.parse(decodeURIComponent(route_options));
// 		frappe.web_form.set_value("venue", opts.venue);
// 		frappe.web_form.set_value("company", opts.company);
// 		frappe.web_form.set_value("branch", opts.branch);
// 		frappe.web_form.set_value("cost_center", opts.cost_center);
// 		frappe.web_form.set_value("email", opts.email);
// 		frappe.web_form.set_value("name1", opts.name1);
// 		frappe.web_form.set_value("dzongkhag", opts.dzongkhag);
// 		frappe.web_form.set_value("country", opts.country);
// 		frappe.web_form.set_value("organization", opts.organization);
// 		frappe.web_form.set_value("designation", opts.designation);
// 		frappe.web_form.set_value("amount", opts.amount);
// 		frappe.web_form.set_value("total_days", opts.total_days);
// 		frappe.web_form.set_value("total_amount", opts.total_amount);
// 		frappe.web_form.set_value("account_number",opts.account_number)



// 	}
// 	frappe.web_form.set_value("posting_date", frappe.datetime.get_today());
// 	frappe.web_form.get_field("total_days").df.read_only = 1;
// 	frappe.web_form.get_field("total_amount").df.read_only = 1;
// 	frappe.web_form.get_field("amount").df.read_only = 1;

// 		$(document).on("change", '[data-fieldname="attachment"] input[type="file"]', function () {

// 		const fileName = this.value.toLowerCase();
// 		if (fileName) {
// 			const allowed = /\.(png|jpg|jpeg)$/;

// 			if (!allowed.test(fileName)) {
// 				frappe.throw("Only PNG, JPG, and JPEG files are allowed.");
// 				$(this).val("");
// 			}
// 		}
// 	});

// 	frappe.web_form.refresh();



// })	

// frappe.ready(function () {
// 	const params = new URLSearchParams(window.location.search);
// 	const route_options = params.get("route_options");
// 	console.log(route_options)

// 	if (route_options) {
// 		const opts = JSON.parse(decodeURIComponent(route_options));

// 		frappe.web_form.set_value("venue", opts.venue);
// 		frappe.web_form.set_value("company", opts.company);
// 		frappe.web_form.set_value("branch", opts.branch);
// 		frappe.web_form.set_value("cost_center", opts.cost_center);
// 		frappe.web_form.set_value("email", opts.email);
// 		frappe.web_form.set_value("name1", opts.name1);
// 		frappe.web_form.set_value("dzongkhag", opts.dzongkhag);
// 		frappe.web_form.set_value("country", opts.country);
// 		frappe.web_form.set_value("organization", opts.organization);
// 		frappe.web_form.set_value("designation", opts.designation);
// 		frappe.web_form.set_value("amount", opts.amount);
// 		frappe.web_form.set_value("total_days", opts.total_days);
// 		frappe.web_form.set_value("total_amount", opts.total_amount);
// 		frappe.web_form.set_value("account_number", opts.account_number);
// 		frappe.web_form.set_value("qr_code", opts.qr_code);
// 		if (opts.qr_code) {
// 			frappe.web_form.set_df_property("qr_code", "options",
// 				`<img src="${opts.qr_code}"
// 					style="max-width:200px;
// 					border:1px solid #ddd;
// 					padding:5px;
// 					border-radius:8px;" />`
// 			);
// 		}
		
// 	}

// 	// posting date
// 	frappe.web_form.set_value("posting_date", frappe.datetime.get_today());

// 	// readonly fields
// 	frappe.web_form.get_field("total_days").df.read_only = 1;
// 	frappe.web_form.get_field("total_amount").df.read_only = 1;
// 	frappe.web_form.get_field("amount").df.read_only = 1;

// 	// ✅ attachment validation (real-time)
// 	$(document).on("change", '[data-fieldname="attachment"] input[type="file"]', function () {

// 		const fileName = this.value.toLowerCase();

// 		if (fileName) {
// 			const allowed = /\.(png|jpg|jpeg)$/;

// 			if (!allowed.test(fileName)) {
// 				frappe.msgprint("Only PNG, JPG, and JPEG files are allowed.");
// 				$(this).val("");
// 			}
// 		}
// 	});

// 	frappe.web_form.refresh();
// });


frappe.ready(function () {
	const params = new URLSearchParams(window.location.search);
	const name = params.get("venue");

	
	frappe.call({
		method: "education.event_management.web_form.hall_payment.hall_payment.get_hall_payment_data",  // change this path
		args: {
			name: name
		},

		callback: function (r) {
			
			if (!r.message) return;

			const opts = r.message;
	       	frappe.web_form.set_value("hall_booking",opts.name)
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
			frappe.web_form.set_value("account_number", opts.account_number);
			// frappe.web_form.set_value("qr_code", opts.qr_code);

			// // QR IMAGE DISPLAY (HTML FIELD)
			if (opts.qr_code) {
				frappe.web_form.set_df_property("qr_code", "options",
					`<img src="${opts.qr_code}"
						style="max-width:200px;
						border:1px solid #ddd;
						padding:5px;
						border-radius:8px;" />`
				);
			}
		}
	});
    	frappe.web_form.set_value("posting_date", frappe.datetime.get_today());
	// readonly fields (correct way)
	["total_days", "total_amount", "amount"].forEach(f => {
		frappe.web_form.set_df_property(f, "read_only", 1);
	});

});
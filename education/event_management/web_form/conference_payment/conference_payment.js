frappe.ready(function () {
	const params = new URLSearchParams(window.location.search);
	const name = params.get("full_paper");
	console.log("Full Paper Name:", name); // Debugging statement to check the value of 'name'

	
	frappe.call({
		method: "education.event_management.web_form.conference_payment.conference_payment.get_conference_payment_data",  // change this path
		args: {
			name: name
		},

		callback: function (r) {
			
			if (!r.message) return;

			const opts = r.message;
	       	frappe.web_form.set_value("full_paper",opts.full_paper)
			
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
    // 	frappe.web_form.set_value("posting_date", frappe.datetime.get_today());
	// // readonly fields (correct way)
	// ["total_days", "total_amount", "amount"].forEach(f => {
	// 	frappe.web_form.set_df_property(f, "read_only", 1);
	// });

});
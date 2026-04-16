
// frappe.ready(function () {
// 	const params = new URLSearchParams(window.location.search);
// 	const route_options = params.get("route_options");

// 	// Prefill venue if route_options exist
// 	if (route_options) {
// 		const opts = JSON.parse(decodeURIComponent(route_options));
// 		frappe.web_form.set_value("venue", opts.venue);
// 		frappe.web_form.set_value("amount", opts.amount)
// 	}
// 	$('form button[type="submit"]').on('click', function (e) {
// 		e.preventDefault();
// 		e.stopImmediatePropagation();
// 		const email = frappe.web_form.get_value("email");
// 		const venue = frappe.web_form.get_value("venue");


// 		const $btn = $(this);
// 		frappe.call({
// 			method: "education.event_management.web_form.hall_booking.hall_booking.check_duplicate_venue",
// 			args: {

// 				email: email,
// 				venue: venue

// 			},
// 			callback: function (r) {
// 				if (r.message.exists) {
// 					frappe.msgprint("You are already registered for this full paper.");
// 					$btn.prop('disabled', false).html('Submit');

// 				} else {
// 					$('form').submit();
// 					setTimeout(function () {
// 						window.location.href = '/room-check';
// 					}, 1000);
// 				}

// 			},
// 		});



// 	});


// });

frappe.ready(function () {
	const params = new URLSearchParams(window.location.search);
	const route_options = params.get("route_options");

	// Prefill venue and amount from route_options
	let perDayAmount = 0;
	if (route_options) {
		const opts = JSON.parse(decodeURIComponent(route_options));
		if (opts.venue) frappe.web_form.set_value("venue", opts.venue);

		if (opts.amount) {
			frappe.web_form.set_value("amount", opts.amount);
			perDayAmount = parseFloat(opts.amount);
			frappe.web_form.set_value("company", opts.company)
			frappe.web_form.set_value("branch", opts.branch);
			frappe.web_form.set_value("cost_center", opts.cost_center);
		}
	}

	// Make fields read-only
	frappe.web_form.get_field("total_days").df.read_only = 1;
	frappe.web_form.get_field("total_amount").df.read_only = 1;
	frappe.web_form.get_field("amount").df.read_only = 1;
	frappe.web_form.refresh();

	// Function to calculate total days and total amount
	const calculateTotal = () => {
		const fromDate = frappe.web_form.get_value("from_date");
		const toDate = frappe.web_form.get_value("to_date");
		const amountField = parseFloat(frappe.web_form.get_value("amount")) || 0;
		const perDay = amountField || perDayAmount || 0;

		if (fromDate && toDate && perDay > 0) {
			const result = calculateBooking(fromDate, toDate, perDay);
			frappe.web_form.set_value("total_days", result.total_days);
			frappe.web_form.set_value("total_amount", result.total_amount);
		} else {
			frappe.web_form.set_value("total_days", 0);
			frappe.web_form.set_value("total_amount", 0);
		}
	};

	// Use Frappe's event system
	frappe.web_form.on("from_date", (field, value) => calculateTotal());
	frappe.web_form.on("to_date", (field, value) => calculateTotal());
	frappe.web_form.on("amount", (field, value) => calculateTotal());

	// Helper function to calculate days and amount
	function calculateBooking(fromDate, toDate, perDayAmount) {
		let from, to;

		if (typeof fromDate === 'string') {
			if (fromDate.includes('-')) {
				const parts = fromDate.split('-');
				if (parts[0].length === 4) { // YYYY-MM-DD
					from = new Date(parts[0], parts[1] - 1, parts[2]);
					to = new Date(toDate.split('-')[0], toDate.split('-')[1] - 1, toDate.split('-')[2]);
				} else { // DD-MM-YYYY
					from = new Date(parts[2], parts[1] - 1, parts[0]);
					to = new Date(toDate.split('-')[2], toDate.split('-')[1] - 1, toDate.split('-')[0]);
				}
			}
		} else {
			from = new Date(fromDate);
			to = new Date(toDate);
		}

		const diffTime = Math.abs(to - from);
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
		const total_amount = diffDays * perDayAmount;

		return { total_days: diffDays, total_amount };
	}

	// Initial calculation
	setTimeout(calculateTotal, 500);

	$('form button[type="submit"]').on('click', function (e) {
		e.preventDefault();
		// e.stopImmediatePropagation();
		const email = frappe.web_form.get_value("email");
		const venue = frappe.web_form.get_value("venue");


		const $btn = $(this);
		frappe.call({
			method: "education.event_management.web_form.hall_booking.hall_booking.check_duplicate_venue",
			args: {

				email: email,
				venue: venue

			},
			callback: function (r) {
				if (r.message.exists) {
					frappe.msgprint("You are already booked for this venue.");
					$btn.prop('disabled', false).html('Submit');

				} else {
					$('form').submit();
					setTimeout(function () {
						window.location.href = '/room-check';
					}, 1000);
				}

			},
		});



	});

});
frappe.pages["tutor-timetable"].on_page_load = function (wrapper) {
	frappe.tutor_timetable_page = new TutorTimetablePage(wrapper);
};


class TutorTimetablePage {

	constructor(wrapper) {
		this.wrapper = wrapper;

		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Tutor Timetable"),
			single_column: true
		});

		this.make_filters();
		this.make_timetable_container();
		this.load_user_details();
	}


	// ---------------------------------------------------------
	// Filters
	// ---------------------------------------------------------

	make_filters() {

		this.college = this.page.add_field({
			label: __("College"),
			fieldname: "college",
			fieldtype: "Link",
			options: "Company",
			read_only: 1
		});


		this.tutor = this.page.add_field({
			label: __("Tutor"),
			fieldname: "tutor",
			fieldtype: "Link",
			options: "Employee",
			read_only: 1
		});


		this.academic_term = this.page.add_field({
			label: __("Academic Term"),
			fieldname: "academic_term",
			fieldtype: "Link",
			options: "Academic Term",

			get_query: () => {

				const college = this.college.get_value();

				if (!college) {
					return {};
				}

				return {
					filters: {
						college: college
					}
				};
			},

			change: () => {
				this.load_timetable();
			}
		});
	}


	// ---------------------------------------------------------
	// Get Employee from logged-in User
	// ---------------------------------------------------------

	load_user_details() {

		frappe.db.get_value(
			"Employee",
			{
				user_id: frappe.session.user
			},
			["name", "company"],
			(r) => {

				if (!r || !r.name) {

					frappe.msgprint(
						__("No Employee is linked to the logged-in User.")
					);

					return;
				}


				// Set Tutor
				this.tutor.set_value(r.name);


				// Set College
				if (r.company) {

					this.college.set_value(r.company);

					// Refresh academic term field
					this.academic_term.refresh();
				}

			}
		);
	}


	// ---------------------------------------------------------
	// Timetable Container
	// ---------------------------------------------------------

	make_timetable_container() {

		this.container = $(`
			<div class="timetable-container mt-4">

				<div class="text-muted text-center p-5">
					${__("Select Academic Term")}
				</div>

			</div>
		`);

		$(this.page.body).append(this.container);
	}


	// ---------------------------------------------------------
	// Load Timetable
	// ---------------------------------------------------------

	load_timetable() {

		const college = this.college.get_value();
		const tutor = this.tutor.get_value();
		const academic_term = this.academic_term.get_value();


		if (!college || !tutor || !academic_term) {

			this.container.html(`
				<div class="text-muted text-center p-5">
					${__("Select Academic Term")}
				</div>
			`);

			return;
		}


		this.container.html(`
			<div class="text-muted text-center p-5">
				${__("Loading Timetable...")}
			</div>
		`);


		frappe.call({

			method:
				"education.academic_management.page.timetable.timetable.get_timetable_tutor",

			args: {
				college: college,
				tutor: tutor,
				academic_term: academic_term
			},

			callback: (r) => {

				if (!r.message) {

					this.container.html(`
						<div class="text-muted text-center p-5">
							${__("No timetable found")}
						</div>
					`);

					return;
				}


				const data = r.message.timetable || [];
				const blocked = r.message.blocked || [];

				const start_time = r.message.start_time;
				const end_time = r.message.end_time;


				if (!data.length && !blocked.length) {

					this.container.html(`
						<div class="text-muted text-center p-5">
							<b>${__("No Timetable Generated")}</b>
						</div>
					`);

					return;
				}


				this.draw_timetable(
					data,
					blocked,
					start_time,
					end_time
				);

			}
		});
	}


	// ---------------------------------------------------------
	// Draw Timetable
	// ---------------------------------------------------------

	draw_timetable(data, blocked, start_time, end_time) {

		const days = [
			"Monday",
			"Tuesday",
			"Wednesday",
			"Thursday",
			"Friday"
		];


		const slots = this.generate_slots(
			data,
			blocked,
			start_time,
			end_time
		);


		if (!slots.length || slots.length < 2) {

			this.container.html(`
				<div class="text-muted text-center p-5">
					${__("No valid time slots found")}
				</div>
			`);

			return;
		}


		let table = $(`
			<table class="table table-bordered timetable-table">
				<thead>
					<tr>
						<th class="day-column">
							${__("Day")}
						</th>
					</tr>
				</thead>

				<tbody></tbody>
			</table>
		`);


		// -----------------------------------------------------
		// Header - Time as columns
		// -----------------------------------------------------

		const header = table.find("thead tr");


		for (let i = 0; i < slots.length - 1; i++) {

			const start = moment(
				slots[i],
				"HH:mm"
			);

			const end = moment(
				slots[i + 1],
				"HH:mm"
			);


			header.append(`
				<th class="time-header">
					${start.format("hh:mm A")}
					-
					${end.format("hh:mm A")}
				</th>
			`);
		}


		const tbody = table.find("tbody");


		// -----------------------------------------------------
		// Days as rows
		// -----------------------------------------------------

		days.forEach(day => {

			let row = `
				<tr>

					<td class="day-column">
						<b>${day}</b>
					</td>
			`;


			for (let i = 0; i < slots.length - 1; i++) {

				const slotStart = moment(
					slots[i],
					"HH:mm"
				);

				const slotEnd = moment(
					slots[i + 1],
					"HH:mm"
				);


				// -------------------------------------------------
				// Find timetable entry
				// -------------------------------------------------

				const entry = data.find(d => {

					if (d.day !== day) {
						return false;
					}


					const periodStart = moment(
						normalize_time(d.from_time),
						"HH:mm:ss"
					);

					const periodEnd = moment(
						normalize_time(d.to_time),
						"HH:mm:ss"
					);


					return (
						slotStart.isSameOrAfter(periodStart) &&
						slotEnd.isSameOrBefore(periodEnd)
					);

				});


				// -------------------------------------------------
				// Find blocked period
				// -------------------------------------------------

				const blockedSlot = blocked.find(b => {

					if (b.day !== day) {
						return false;
					}


					const blockStart = moment(
						normalize_time(b.from_time),
						"HH:mm:ss"
					);

					const blockEnd = moment(
						normalize_time(b.to_time),
						"HH:mm:ss"
					);


					return (
						slotStart.isSameOrAfter(blockStart) &&
						slotEnd.isSameOrBefore(blockEnd)
					);

				});


				// -------------------------------------------------
				// Blocked period
				// -------------------------------------------------

				if (blockedSlot) {

					row += `
						<td class="tt-break">

							<div class="period-name">
								${frappe.utils.escape_html(
									blockedSlot.period_name || ""
								)}
							</div>

						</td>
					`;
				}


				// -------------------------------------------------
				// Timetable Entry
				// -------------------------------------------------

				else if (entry) {

					row += `
						<td class="tt-cell">

							<div class="module">
								${frappe.utils.escape_html(
									entry.module_code || ""
								)}
							</div>

							<div class="class-type">
								${frappe.utils.escape_html(
									entry.class_type || ""
								)}
							</div>

							<div class="tutor-name">
								${frappe.utils.escape_html(
									entry.tutor_name || ""
								)}
							</div>

							<div class="room">
								Room:
								${frappe.utils.escape_html(
									entry.room_name || ""
								)}
							</div>

						</td>
					`;
				}


				// -------------------------------------------------
				// Empty
				// -------------------------------------------------

				else {

					row += `<td></td>`;

				}

			}


			row += "</tr>";

			tbody.append(row);

		});


		// ---------------------------------------------------------
		// Wrapper
		// ---------------------------------------------------------

		const tableWrapper = $(`
			<div class="timetable-print-only">
			</div>
		`);


		tableWrapper.append(table);


		this.container.html(tableWrapper);


		// ---------------------------------------------------------
		// CSS
		// ---------------------------------------------------------

		this.container.find(".timetable-print-only").css({
			width: "100%",
			overflowX: "auto"
		});


		this.container.find(".timetable-table").css({
            width: "95%",
            margin: "0 auto",
            borderCollapse: "collapse"
        });


		this.container.find(
			".timetable-table th, .timetable-table td"
		).css({
			border: "1px solid #C4C4C4",
			textAlign: "center",
			verticalAlign: "middle",
			padding: "5px",
            fontWeight: "600",

		});


		this.container.find(".day-column").css({
			width: "120px",
            height:"50px",
			background: "linear-gradient(to right, #BDDDF2)",
            fontSize:"11px",
			whiteSpace: "nowrap"
		});


		this.container.find(".time-header").css({
			background: "linear-gradient(to right, #BDDDF2)",
			fontWeight: "600",
            fontSize:"11px",
			whiteSpace: "nowrap"
		});


		this.container.find(".tt-cell").css({
			height: "90px",
			fontSize: "12px"
		});


		this.container.find(".tt-break").css({
			height: "90px",
			fontWeight: "600",
			fontSize: "11px",
            background:"#DBDBDB",
			verticalAlign: "middle"
		});


		this.container.find(".module").css({
			fontWeight: "600",
			fontSize: "14px",
			marginBottom: "4px"
		});


		this.container.find(".class-type").css({
			fontSize: "11px",
			marginBottom: "3px"
		});


		this.container.find(".tutor-name").css({
			fontSize: "11px",
			marginBottom: "3px"
		});


		this.container.find(".room").css({
			fontSize: "11px"
		});


		this.container.find(".period-name").css({
			fontWeight: "600",
            fontSize:"12px"
		});

	}


	// ---------------------------------------------------------
	// Generate Time Slots
	// ---------------------------------------------------------

	generate_slots(data, blocked, start_time, end_time) {

		const boundaries = new Set();


		// Main Config start time
		if (start_time) {

			boundaries.add(
				moment(
					normalize_time(start_time),
					"HH:mm:ss"
				).format("HH:mm")
			);

		}


		// Main Config end time
		if (end_time) {

			boundaries.add(
				moment(
					normalize_time(end_time),
					"HH:mm:ss"
				).format("HH:mm")
			);

		}


		// -----------------------------------------------------
		// Timetable boundaries
		// -----------------------------------------------------

		data.forEach(d => {

			if (d.from_time) {

				boundaries.add(
					moment(
						normalize_time(d.from_time),
						"HH:mm:ss"
					).format("HH:mm")
				);

			}


			if (d.to_time) {

				boundaries.add(
					moment(
						normalize_time(d.to_time),
						"HH:mm:ss"
					).format("HH:mm")
				);

			}

		});


		// -----------------------------------------------------
		// Blocked period boundaries
		// -----------------------------------------------------

		blocked.forEach(b => {

			if (b.from_time) {

				boundaries.add(
					moment(
						normalize_time(b.from_time),
						"HH:mm:ss"
					).format("HH:mm")
				);

			}


			if (b.to_time) {

				boundaries.add(
					moment(
						normalize_time(b.to_time),
						"HH:mm:ss"
					).format("HH:mm")
				);

			}

		});


		return Array.from(boundaries).sort(
			(a, b) =>
				moment(a, "HH:mm").diff(
					moment(b, "HH:mm")
				)
		);

	}

}


/*
=========================================================
Normalize Frappe Time
=========================================================
*/

function normalize_time(time) {

	if (!time) {
		return "00:00:00";
	}


	// Frappe/Python timedelta can arrive like:
	// "8:00:00"
	// "08:00:00"
	// "0 days, 08:00:00"
	// "08:00:00.000000"

	let value = String(time).trim();


	// Remove "0 days, "
	value = value.replace(
		/^\d+\s+days?,\s*/,
		""
	);


	// Remove milliseconds
	value = value.split(".")[0];


	// HH:MM -> HH:MM:SS
	if (value.split(":").length === 2) {
		value += ":00";
	}


	return value;

}
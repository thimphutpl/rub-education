// frappe.pages['student-module-asses'].on_page_load = function(wrapper) {

// 	let page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'Student Module Assessment Component Report',
// 		single_column: true
// 	});

// 	// ============================
// 	// FILTER SECTION
// 	// ============================
// 	let fieldContainer = $(`
// 		<div class="row" style="margin-bottom:15px;">
// 			<div class="col-md-4" id="module-enroll-field"></div>
// 			<div class="col-md-2" id="btn-field"></div>
// 		</div>
// 	`).appendTo(page.body);

// 	// ============================
// 	// MODULE ENROLLMENT FILTER
// 	// ============================
// 	let module_enroll_key = frappe.ui.form.make_control({
// 		parent: $('#module-enroll-field'),
// 		df: {
// 			label: 'Module Enrollment',
// 			fieldname: 'module_enrollment',
// 			fieldtype: 'Link',
// 			options: 'Module Enrolment',
// 			reqd: 1
// 		},
// 		render_input: true
// 	});
// 	module_enroll_key.refresh();

// 	// ============================
// 	// BUTTON
// 	// ============================
// 	let btn = $(`<button class="btn btn-primary" style="margin-top:25px;">Load Report</button>`)
// 		.appendTo('#btn-field');

// 	// ============================
// 	// DATA CONTAINER
// 	// ============================
// 	let dataContainer = $('<div style="margin-top:20px;"></div>').appendTo(page.body);

// 	// ============================
// 	// LOAD FUNCTION
// 	// ============================
// 	function load_report() {

// 		let module_enrollment = module_enroll_key.get_value();

// 		if (!module_enrollment) {
// 			frappe.msgprint("Please select Module Enrollment");
// 			return;
// 		}

// 		dataContainer.html("<p>Loading...</p>");

// 		frappe.call({
// 			method: "education.academic_management.page.student_dashboard.student_dashboard.get_ca_report",
// 			args: {
// 				module_enrollment: module_enrollment
// 			},
// 			callback: function(r) {

// 				if (!r.message || !r.message.students || !r.message.students.length) {
// 					dataContainer.html("<b>No data found</b>");
// 					return;
// 				}

// 				let { students, components, data } = r.message;

// 				let html = `<table class="table table-bordered table-sm">`;

// 				// ============================
// 				// HEADER
// 				// ============================
// 				html += `<thead><tr>
// 					<th>Student</th>`;

// 				components.forEach(c => {
// 					html += `<th>${c}</th>`;
// 				});

// 				html += `<th>Total</th></tr></thead><tbody>`;

// 				// ============================
// 				// BODY
// 				// ============================
// 				students.forEach(student => {

// 					let total = 0;

// 					html += `<tr><td>${student}</td>`;

// 					components.forEach(comp => {
// 						let val = (data[student] && data[student][comp]) ? data[student][comp] : 0;
// 						total += val;
// 						html += `<td>${val}</td>`;
// 					});

// 					html += `<td><b>${total}</b></td></tr>`;
// 				});

// 				html += `</tbody></table>`;

// 				dataContainer.html(html);
// 			}
// 		});
// 	}

// 	// ============================
// 	// EVENTS
// 	// ============================
// 	btn.on("click", load_report);
// };
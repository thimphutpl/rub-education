frappe.pages['student-module-asses'].on_page_load = function(wrapper) {

	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Assessment Component Report',
		single_column: true
	});

	// ============================
	// FILTER UI
	// ============================
	let fieldContainer = $(`
		<div class="row" style="margin-bottom:15px;">
			<div class="col-md-4" id="module-enroll-field"></div>
			<div class="col-md-2" id="btn-field"></div>
		</div>
	`).appendTo(page.body);

	let module_enroll_key = frappe.ui.form.make_control({
		parent: $('#module-enroll-field'),
		df: {
			label: 'Module Enrollment',
			fieldname: 'module_enrollment',
			fieldtype: 'Link',
			options: 'Module Enrolment Key',
			reqd: 1
		},
		render_input: true
	});
	module_enroll_key.refresh();

	let btn = $(`
		<button class="btn btn-primary" style="margin-top:25px;">
			Load Report
		</button>
	`).appendTo('#btn-field');

	let dataContainer = $('<div style="margin-top:20px;"></div>').appendTo(page.body);

	// ============================
	// LOAD REPORT
	// ============================
	function load_report() {

		let module_enrollment = module_enroll_key.get_value();

		if (!module_enrollment) {
			frappe.msgprint("Please select Module Enrollment");
			return;
		}

		dataContainer.html("<p>Loading...</p>");

		frappe.call({
			method: "education.academic_management.page.student_module_asses.student-module-asses.get_ca_report",
			args: {
				module_enrollment: module_enrollment
			},
			callback: function(r) {

				let res = r.message;

				if (!res || !res.students || !res.students.length) {
					dataContainer.html("<b>No data found</b>");
					return;
				}

				let students = res.students;
				let components = res.components;

				// 🔥 extract clean component names
				let comp_names = components.map(c => c.assessment_name);

				// ============================
				// TABLE START
				// ============================
				let html = `
				<div style="overflow-x:auto;">
				<table class="table table-bordered table-sm" style="table-layout: fixed; width: 100%;">
				`;

				// ============================
				// HEADER
				// ============================
				// html += `<thead><tr>`;
				html += `
					<thead style="
						background: #f5f5f5;
						box-shadow: 0 2px 4px rgba(0,0,0,0.08);
						position: sticky;
						top: 0;
						z-index: 2;
					">
					<tr>
					`;

				html += `<th style="width:120px;">Student ID</th>`;
				html += `<th style="width:200px;">Student Name</th>`;

				comp_names.forEach(c => {
					html += `
						<th style="text-align:center; white-space:nowrap;">
							${c}
						</th>`;
				});

				html += `<th style="width:100px; text-align:center;">Total</th>`;
				html += `</tr></thead><tbody>`;

				// ============================
				// BODY
				// ============================
				students.forEach(student => {

					html += `<tr>`;

					// ID
					html += `<td>${student.student}</td>`;

					// NAME (from backend)
					html += `<td style="font-weight:500;">
						${student.student_name || ''}
					</td>`;

					// COMPONENT VALUES
					comp_names.forEach(comp => {
						let val = student.assessments[comp] || 0;
						html += `<td style="text-align:center;">${val}</td>`;
					});

					// TOTAL (safe + no float issues)
					html += `<td style="text-align:center; font-weight:bold; background:#f5f5f5;">
						${Number(student.total || 0)}
					</td>`;

					html += `</tr>`;
				});

				html += `</tbody></table></div>`;

				dataContainer.html(html);
			}
		});
	}

	btn.on("click", load_report);
};
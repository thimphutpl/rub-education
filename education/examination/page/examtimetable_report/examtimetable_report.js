frappe.pages['examtimetable-report'].on_page_load = function(wrapper) {
	var me = this;
	
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Exam Timetable Report',
		single_column: true
	});
	
	// Add filters section
	me.fields = {};
	
	// Create filter area
	$(page.body).append(`
		<div class="filters-section" style="padding: 20px; background: #f5f7fa; border-bottom: 1px solid #d1d8dd;">
			<div class="row">
				<div class="col-md-3">
					<label>Exam Date</label>
					<input type="date" id="exam-date-filter" class="form-control" placeholder="Select Exam Date">
				</div>
				<div class="col-md-3">
					<label>Exam Room</label>
					<select id="room-filter" class="form-control">
						<option value="">All Rooms</option>
					</select>
				</div>
				<div class="col-md-2">
					<label>&nbsp;</label>
					<button id="generate-report" class="btn btn-primary form-control">Generate Report</button>
				</div>
				<div class="col-md-2">
					<label>&nbsp;</label>
					<button id="reset-filters" class="btn btn-default form-control">Reset</button>
				</div>
			</div>
		</div>
	`);
	
	// Create report container
	$(page.body).append(`
		<div id="report-container" style="padding: 20px; overflow-x: auto;">
			<div class="loading-spinner" style="text-align: center; padding: 50px;">
				<i class="fa fa-spinner fa-spin fa-3x"></i>
				<p>Loading report...</p>
			</div>
		</div>
	`);
	
	// Load rooms for filter dropdown
	function loadRooms() {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Room",
				fields: ["name"],
				limit_page_length: 500
			},
			callback: function(response) {
				var rooms = response.message || [];
				var $roomSelect = $("#room-filter");
				rooms.forEach(function(room) {
					$roomSelect.append(`<option value="${room.name}">${room.name}</option>`);
				});
			}
		});
	}
	
	// Format time to HH:MM
	function formatTime(timeStr) {
		if (!timeStr) return "";
		return timeStr.substring(0, 5);
	}
	
	// Generate the report
	function generateReport() {
		var filters = {
			exam_date: $("#exam-date-filter").val(),
			room: $("#room-filter").val()
		};
		
		// Show loading
		$("#report-container").html(`
			<div style="text-align: center; padding: 50px;">
				<i class="fa fa-spinner fa-spin fa-3x"></i>
				<p>Generating report...</p>
			</div>
		`);
		
		// Call server-side to get report data
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Exam Timetable",
				filters: { docstatus: 1 },
				fieldname: ["name"]
			},
			callback: function(response) {
				// Use server-side script to get full report data
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Exam Timetable",
						filters: getDocstatusFilter(filters),
						fields: ["name", "room", "start_time", "end_time", "capacity", "exam_date"],
						limit_page_length: 1000
					},
					callback: function(timetableResponse) {
						// Fetch all related data
						fetchCompleteReportData(timetableResponse.message, filters);
					}
				});
			}
		});
	}
	
	function getDocstatusFilter(filters) {
		var filterConditions = [["docstatus", "=", 1]];
		if (filters.exam_date) {
			filterConditions.push(["exam_date", "=", filters.exam_date]);
		}
		if (filters.room) {
			filterConditions.push(["room", "=", filters.room]);
		}
		return filterConditions;
	}
	
	function fetchCompleteReportData(timetables, filters) {
		if (!timetables || timetables.length === 0) {
			$("#report-container").html(`
				<div class="alert alert-info" style="margin: 20px;">
					No exam timetables found for the selected filters.
				</div>
			`);
			return;
		}
		
		// Get all exam IDs
		var examIds = timetables.map(t => t.name);
		
		// Fetch modules, students, and invigilators for all timetables
		var promises = [];
		
		// Fetch modules
		promises.push(frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Exam Module",
				filters: [["parent", "in", examIds]],
				fields: ["parent", "module"],
				limit_page_length: 5000
			}
		}));
		
		// Fetch students
		promises.push(frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Exam Timetable Student",
				filters: [["parent", "in", examIds]],
				fields: ["parent", "student"],
				limit_page_length: 5000
			}
		}));
		
		// Fetch invigilators
		promises.push(frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Exam Invigilator",
				filters: [["parent", "in", examIds]],
				fields: ["parent", "invigilator_name"],
				limit_page_length: 5000
			}
		}));
		
		Promise.all(promises).then(function(results) {
			var modulesData = results[0].message || [];
			var studentsData = results[1].message || [];
			var invigilatorsData = results[2].message || [];
			
			// Organize data by exam ID
			var modulesMap = {};
			var studentsMap = {};
			var invigilatorsMap = {};
			
			modulesData.forEach(function(m) {
				if (!modulesMap[m.parent]) modulesMap[m.parent] = [];
				modulesMap[m.parent].push(m.module);
			});
			
			studentsData.forEach(function(s) {
				if (!studentsMap[s.parent]) studentsMap[s.parent] = [];
				studentsMap[s.parent].push(s.student);
			});
			
			invigilatorsData.forEach(function(i) {
				if (!invigilatorsMap[i.parent]) invigilatorsMap[i.parent] = [];
				invigilatorsMap[i.parent].push(i.invigilator_name);
			});
			
			// Build complete exam data
			var completeExams = timetables.map(function(t) {
				return {
					exam_id: t.name,
					exam_hall: t.room,
					start_time: t.start_time,
					end_time: t.end_time,
					capacity: t.capacity,
					exam_date: t.exam_date,
					modules: (modulesMap[t.name] || []).join(", "),
					total_students: (studentsMap[t.name] || []).length,
					invigilators: (invigilatorsMap[t.name] || []).join(", ")
				};
			});
			
			// Build the report table
			buildReportTable(completeExams, filters);
		});
	}
	
	function buildReportTable(exams, filters) {
		// Get unique halls
		var hallsMap = {};
		exams.forEach(function(exam) {
			if (!hallsMap[exam.exam_hall]) {
				hallsMap[exam.exam_hall] = {
					room: exam.exam_hall,
					capacity: exam.capacity
				};
			}
		});
		
		var halls = Object.values(hallsMap).sort(function(a, b) {
			return a.room.localeCompare(b.room);
		});
		
		// Get unique time slots
		var timeSlotsMap = {};
		exams.forEach(function(exam) {
			var slotKey = exam.start_time + "|" + exam.end_time;
			if (!timeSlotsMap[slotKey]) {
				timeSlotsMap[slotKey] = {
					start_time: exam.start_time,
					end_time: exam.end_time
				};
			}
		});
		
		var timeSlots = Object.values(timeSlotsMap).sort(function(a, b) {
			return a.start_time.localeCompare(b.start_time);
		});
		
		// Build the HTML table
		var html = '<table class="table table-bordered report-table" style="min-width: 800px;">';
		
		// Header row
		html += '<thead><tr>';
		html += '<th style="background-color: #f5f7fa; vertical-align: middle;">Exam Hall</th>';
		html += '<th style="background-color: #f5f7fa; vertical-align: middle;">Capacity</th>';
		timeSlots.forEach(function(slot) {
			html += `<th style="background-color: #f5f7fa; text-align: center;">${formatTime(slot.start_time)} - ${formatTime(slot.end_time)}</th>`;
		});
		html += '</tr></thead>';
		
		// Body rows
		html += '<tbody>';
		halls.forEach(function(hall) {
			html += '<tr>';
			html += `<td><strong>${hall.room}</strong></td>`;
			html += `<td style="text-align: center;">${hall.capacity || '-'}</td>`;
			
			timeSlots.forEach(function(slot) {
				var examInSlot = exams.find(function(e) {
					return e.exam_hall === hall.room && 
						   e.start_time === slot.start_time && 
						   e.end_time === slot.end_time;
				});
				
				if (examInSlot) {
					var cellContent = `
						<div style="padding: 5px;">
							<strong>Modules:</strong> ${examInSlot.modules || '-'}<br>
							<strong>Students:</strong> ${examInSlot.total_students}<br>
							<strong>Invigilators:</strong> ${examInSlot.invigilators || '-'}
						</div>
					`;
					html += `<td style="vertical-align: top; background-color: #e8f5e9;">${cellContent}</td>`;
				} else {
					html += '<td style="vertical-align: middle; text-align: center; color: #999;">-</td>';
				}
			});
			
			html += '</tr>';
		});
		html += '</tbody></table>';
		
		// Add summary
		var summaryHtml = `
			<div class="report-summary" style="margin-top: 20px; padding: 15px; background: #f5f7fa; border-radius: 4px;">
				<h5>Report Summary</h5>
				<p><strong>Total Exam Halls:</strong> ${halls.length}</p>
				<p><strong>Total Time Slots:</strong> ${timeSlots.length}</p>
				<p><strong>Total Exam Sessions:</strong> ${exams.length}</p>
				${filters.exam_date ? `<p><strong>Filtered by Date:</strong> ${filters.exam_date}</p>` : ''}
				${filters.room ? `<p><strong>Filtered by Room:</strong> ${filters.room}</p>` : ''}
			</div>
		`;
		
		$("#report-container").html(`
			<div style="overflow-x: auto;">
				${summaryHtml}
				${html}
			</div>
		`);
		
		// Add some CSS styling
		addReportStyles();
	}
	
	function addReportStyles() {
		if ($("#report-styles").length === 0) {
			$("head").append(`
				<style id="report-styles">
					.report-table {
						width: 100%;
						border-collapse: collapse;
						font-size: 12px;
					}
					.report-table th,
					.report-table td {
						border: 1px solid #d1d8dd;
						padding: 8px;
					}
					.report-table th {
						font-weight: 600;
						white-space: nowrap;
					}
					.report-table tbody tr:hover {
						background-color: #f5f7fa;
					}
					.filters-section .form-control {
						font-size: 12px;
					}
					@media print {
						.filters-section,
						.btn {
							display: none;
						}
						.report-table {
							font-size: 10px;
						}
					}
				</style>
			`);
		}
	}
	
	// Event handlers
	$("#generate-report").on("click", function() {
		generateReport();
	});
	
	$("#reset-filters").on("click", function() {
		$("#exam-date-filter").val("");
		$("#room-filter").val("");
		generateReport();
	});
	
	// Initialize
	loadRooms();
	generateReport();
};
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
					<label>From Date</label>
					<input type="date" id="from-date-filter" class="form-control" placeholder="From Date">
				</div>
				<div class="col-md-3">
					<label>To Date</label>
					<input type="date" id="to-date-filter" class="form-control" placeholder="To Date">
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
				<div class="col-md-1">
					<label>&nbsp;</label>
					<button id="reset-filters" class="btn btn-default form-control">Reset</button>
				</div>
			</div>
		</div>
	`);
	
	// Create report container
	$(page.body).append(`
		<div id="report-container" style="padding: 20px;">
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
				if (response.message && response.message.length) {
					var rooms = response.message || [];
					var $roomSelect = $("#room-filter");
					$roomSelect.empty();
					$roomSelect.append('<option value="">All Rooms</option>');
					rooms.forEach(function(room) {
						$roomSelect.append(`<option value="${room.name}">${room.name}</option>`);
					});
				}
			},
			error: function(err) {
				console.error("Error loading rooms:", err);
			}
		});
	}
	
	// Format time to HH:MM
	function formatTime(timeStr) {
		if (!timeStr) return "";
		return timeStr.substring(0, 5);
	}
	
	// Get day name from date
	function getDayName(dateStr) {
		if (!dateStr) return "";
		var date = new Date(dateStr);
		return date.toLocaleDateString('en-US', { weekday: 'long' });
	}
	
	// Generate the report
	function generateReport() {
		var filters = {
			from_date: $("#from-date-filter").val(),
			to_date: $("#to-date-filter").val(),
			room: $("#room-filter").val()
		};
		
		// Show loading
		$("#report-container").html(`
			<div style="text-align: center; padding: 50px;">
				<i class="fa fa-spinner fa-spin fa-3x"></i>
				<p>Generating report...</p>
			</div>
		`);
		
		// Build filter conditions
		var filterConditions = [["docstatus", "=", 1]];
		
		if (filters.from_date && filters.to_date) {
			filterConditions.push(["exam_date", "between", [filters.from_date, filters.to_date]]);
		} else if (filters.from_date) {
			filterConditions.push(["exam_date", ">=", filters.from_date]);
		} else if (filters.to_date) {
			filterConditions.push(["exam_date", "<=", filters.to_date]);
		}
		
		if (filters.room) {
			filterConditions.push(["room", "=", filters.room]);
		}
		
		// Fetch Exam Timetable data
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Exam Timetable",
				filters: filterConditions,
				fields: ["name", "room", "start_time", "end_time", "capacity", "exam_date", "academic_year", "academic_term"],
				order_by: "exam_date, start_time",
				limit_page_length: 1000
			},
			callback: function(response) {
				if (response.message && response.message.length > 0) {
					var timetables = response.message;
					// Use the permission-safe method
					fetchCompleteReportDataSafe(timetables, filters);
				} else {
					$("#report-container").html(`
						<div class="alert alert-info" style="margin: 20px;">
							<i class="fa fa-info-circle"></i> No exam timetables found for the selected filters.
						</div>
					`);
				}
			},
			error: function(err) {
				console.error("Error fetching exam timetables:", err);
				$("#report-container").html(`
					<div class="alert alert-danger" style="margin: 20px;">
						<i class="fa fa-exclamation-triangle"></i> Error loading report: ${err.message || "Unknown error"}
					</div>
				`);
			}
		});
	}
	
	// PERMISSION-SAFE METHOD: Fetch full documents including child tables
	function fetchCompleteReportDataSafe(timetables, filters) {
		if (!timetables || timetables.length === 0) {
			return;
		}
		
		var promises = [];
		
		// Fetch each full document including child tables (bypasses child table permissions)
		timetables.forEach(function(timetable) {
			promises.push(frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Exam Timetable",
					name: timetable.name
				}
			}).catch(err => {
				console.error(`Error fetching ${timetable.name}:`, err);
				return { message: null };
			}));
		});
		
		Promise.all(promises).then(function(results) {
			var completeExams = [];
			
			results.forEach(function(result) {
				var doc = result.message;
				if (!doc) return;
				
				// Get modules from the exam_module child table
				var modules = [];
				if (doc.exam_module && Array.isArray(doc.exam_module)) {
					modules = doc.exam_module.map(m => m.module).filter(m => m);
				}
				
				// Get invigilators from the examination_invigilator child table
				var invigilators = [];
				if (doc.examination_invigilator && Array.isArray(doc.examination_invigilator)) {
					invigilators = doc.examination_invigilator.map(i => i.invigilator).filter(i => i);
				}
				
				// Get student count
				var studentCount = 0;
				if (doc.exam_timetable_student && Array.isArray(doc.exam_timetable_student)) {
					studentCount = doc.exam_timetable_student.length;
				}
				
				completeExams.push({
					exam_date: doc.exam_date,
					weekday: getDayName(doc.exam_date),
					start_time: doc.start_time,
					end_time: doc.end_time,
					module: modules.length > 0 ? modules.join(", ") : "—",
					room: doc.room,
					invigilators: invigilators,
					total_students: studentCount,
					capacity: doc.capacity,
					academic_term: doc.academic_term
				});
			});
			
			// Sort by date and time
			completeExams.sort(function(a, b) {
				var dateCompare = new Date(a.exam_date) - new Date(b.exam_date);
				if (dateCompare !== 0) return dateCompare;
				return a.start_time.localeCompare(b.start_time);
			});
			
			console.log("Complete exams data:", completeExams);
			
			// Build the report table
			buildReportTable(completeExams, filters);
		}).catch(error => {
			console.error("Error fetching documents:", error);
			$("#report-container").html(`
				<div class="alert alert-danger" style="margin: 20px;">
					<i class="fa fa-exclamation-triangle"></i> 
					<strong>Error:</strong> Could not fetch exam data.<br><br>
					Please check console for details.
				</div>
			`);
		});
	}
	
	function buildReportTable(exams, filters) {
		if (!exams || exams.length === 0) {
			$("#report-container").html(`
				<div class="alert alert-warning" style="margin: 20px;">
					<i class="fa fa-warning"></i> No exam data available after processing.
				</div>
			`);
			return;
		}
		
		// Build the HTML table
		var html = `
			<div style="overflow-x: auto;">
				<table class="table table-bordered report-table">
					<thead>
						<tr>
							<th style="background-color: #b1d6fbda; width: 18%;">Weekday & Date</th>
							<th style="background-color: #b1d6fbda; width: 12%;">Time</th>
							<th style="background-color: #b1d6fbda; width: 35%;">Module Code & Title</th>
							<th style="background-color: #b1d6fbda; width: 15%;">Room</th>
							<th style="background-color: #b1d6fbda; width: 20%;">Room Invigilator(s)</th>
						</tr>
					</thead>
					<tbody>
		`;
		
		// Add rows for each exam
		exams.forEach(function(exam) {
			var weekdayDate = `${exam.weekday}<br><small>${exam.exam_date}</small>`;
			var timeSlot = `${formatTime(exam.start_time)}–${formatTime(exam.end_time)}`;
			var invigilatorsDisplay = exam.invigilators.length > 0 ? exam.invigilators.join(", ") : "—";
			
			html += `
				<tr>
					<td style="vertical-align: top;">${weekdayDate}</td>
					<td style="vertical-align: top;">${timeSlot}</td>
					<td style="vertical-align: top;">${exam.module}</td>
					<td style="vertical-align: top;">${exam.room}</td>
					<td style="vertical-align: top;">${invigilatorsDisplay}</td>
				</tr>
			`;
		});
		
		html += `
					</tbody>
				</table>
			</div>
		`;
		
		// Calculate summary statistics
		var totalExams = exams.length;
		var uniqueRooms = [...new Set(exams.map(e => e.room))].length;
		var totalStudents = exams.reduce((sum, exam) => sum + exam.total_students, 0);
		var dateRange = "";
		if (exams.length > 0) {
			var firstDate = exams[0].exam_date;
			var lastDate = exams[exams.length - 1].exam_date;
			dateRange = firstDate === lastDate ? firstDate : `${firstDate} to ${lastDate}`;
		}
		
		var summaryHtml = `
			<div class="report-summary" style="margin-bottom: 20px; padding: 15px; background: #f5f7fa; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
				<div>
					<h5 style="margin: 0 0 10px 0;">Exam Timetable Report</h5>
					<p style="margin: 0;"><strong>Total Exam Sessions:</strong> ${totalExams} | 
					<strong>Total Rooms:</strong> ${uniqueRooms} | 
					<strong>Total Students:</strong> ${totalStudents} | 
					<strong>Date Range:</strong> ${dateRange}</p>
					${filters.from_date ? `<p style="margin: 5px 0 0 0;"><small>Filtered from: ${filters.from_date} to ${filters.to_date || 'Present'}</small></p>` : ''}
					${filters.room ? `<p style="margin: 5px 0 0 0;"><small>Filtered by Room: ${filters.room}</small></p>` : ''}
				</div>
				<div>
					
					<button id="print-report" class="btn btn-sm btn-primary form-control" style="padding: 5px 50px;">
						<i class="fa fa-print"></i> Print
					</button>
				</div>
			</div>
		`;
		
		$("#report-container").html(summaryHtml + html);
		
		// Add export functionality
		$("#export-excel").off("click").on("click", function() {
			exportToExcel(exams);
		});
		
		$("#print-report").off("click").on("click", function() {
			window.print();
		});
		
		addReportStyles();
	}
	
	function exportToExcel(exams) {
		var excelData = exams.map(function(exam) {
			return {
				"Weekday & Date": `${exam.weekday} ${exam.exam_date}`,
				"Time": `${formatTime(exam.start_time)}–${formatTime(exam.end_time)}`,
				"Module Code & Title": exam.module,
				"Room": exam.room,
				"Room Invigilator(s)": exam.invigilators.length > 0 ? exam.invigilators.join(", ") : "—"
			};
		});
		
		if (typeof XLSX === 'undefined') {
			var script = document.createElement('script');
			script.src = 'https://cdn.sheetjs.com/xlsx-0.20.2/package/dist/xlsx.full.min.js';
			script.onload = function() {
				createExcelFile(excelData);
			};
			document.head.appendChild(script);
		} else {
			createExcelFile(excelData);
		}
		
		function createExcelFile(data) {
			var ws = XLSX.utils.json_to_sheet(data);
			var wb = XLSX.utils.book_new();
			XLSX.utils.book_append_sheet(wb, ws, "Exam Timetable");
			ws['!cols'] = [{wch:25}, {wch:15}, {wch:40}, {wch:15}, {wch:35}];
			var fileName = `Exam_Timetable_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`;
			XLSX.writeFile(wb, fileName);
		}
	}
	
	function addReportStyles() {
		if ($("#report-styles").length === 0) {
			$("head").append(`
				<style id="report-styles">
					.report-table {
						width: 100%;
						border-collapse: collapse;
						font-size: 13px;
					}
					.report-table th,
					.report-table td {
						border: 1px solid #d1d8dd;
						padding: 10px;
					}
					.report-table th {
						font-weight: 600;
						background-color: #e7e7e7;
					}
					.report-table tbody tr:hover {
						background-color: #f5f7fa;
					}
					.filters-section .form-control {
						font-size: 12px;
					}
					@media print {
						.filters-section,
						.btn,
						#export-excel,
						#print-report {
							display: none;
						}
						.report-table {
							font-size: 10px;
						}
						.report-summary {
							background-color: #f5f7fa !important;
							-webkit-print-color-adjust: exact;
							print-color-adjust: exact;
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
		$("#from-date-filter").val("");
		$("#to-date-filter").val("");
		$("#room-filter").val("");
		generateReport();
	});
	
	// Initialize
	loadRooms();
	generateReport();
};
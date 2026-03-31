// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Exam Timetable Report"] = {
	"filters": [
		{
			fieldname: "exam_date",
			label: __("Exam Date"),
			fieldtype: "Date",
			reqd: 0
		},
		{
			fieldname: "room",
			label: __("Exam Room"),
			fieldtype: "Link",
			options: "Room",
			reqd: 0,
			get_query: function() {
				return {
					filters: {
						// Add any filters if needed
					}
				};
			}
		}
	],
	
	// Custom formatter for better visualization
	formatter: function(value, row, column, data, default_formatter) {
		if (column.fieldname === "hall") {
			// Add capacity badge to hall name
			if (row.capacity) {
				value = `<div style="display: flex; justify-content: space-between; align-items: center;">
					<strong>${value}</strong>
					<span style="background: #667eea; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">
						Cap: ${row.capacity}
					</span>
				</div>`;
				return value;
			}
		}
		return default_formatter(value, row, column, data);
	},
	
	// Add custom CSS styles
	onload: function(report) {
		// Add custom CSS for better table styling
		const style = document.createElement('style');
		style.textContent = `
			.report-container .dt-cell--html {
				padding: 4px !important;
			}
			
			.report-container table tbody tr:hover {
				background-color: #f8f9fa !important;
			}
			
			.report-container .dt-cell--html div {
				transition: all 0.2s ease;
			}
			
			.report-container .dt-cell--html div:hover {
				transform: translateX(2px);
			}
			
			/* Stats Cards Styling */
			.custom-stats-container {
				display: flex;
				gap: 20px;
				margin-bottom: 20px;
				flex-wrap: wrap;
			}
			
			.custom-stat-card {
				flex: 1;
				min-width: 150px;
				background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
				color: white;
				padding: 15px 20px;
				border-radius: 8px;
				box-shadow: 0 2px 4px rgba(0,0,0,0.1);
			}
			
			.custom-stat-card h4 {
				font-size: 12px;
				margin: 0 0 5px 0;
				opacity: 0.9;
				text-transform: uppercase;
				letter-spacing: 0.5px;
			}
			
			.custom-stat-card .stat-value {
				font-size: 28px;
				font-weight: bold;
				margin: 0;
			}
			
			/* Action Buttons */
			.custom-action-buttons {
				display: flex;
				gap: 10px;
				margin-bottom: 20px;
			}
			
			.custom-action-btn {
				padding: 8px 16px;
				border: none;
				border-radius: 6px;
				cursor: pointer;
				font-size: 12px;
				font-weight: 500;
				transition: all 0.2s;
			}
			
			.custom-action-btn:hover {
				transform: translateY(-1px);
			}
			
			.btn-export {
				background: #28a745;
				color: white;
			}
			
			.btn-print {
				background: #17a2b8;
				color: white;
			}
			
			.btn-refresh {
				background: #ffc107;
				color: #333;
			}
			
			/* Responsive Table */
			@media (max-width: 768px) {
				.report-container table {
					font-size: 11px;
				}
				
				.custom-stat-card {
					min-width: 120px;
				}
				
				.custom-stat-card .stat-value {
					font-size: 20px;
				}
			}
		`;
		document.head.appendChild(style);
		
		// Add custom buttons and stats after report is rendered
		report.page.add_inner_button(__("Export to CSV"), function() {
			exportToCSV(report);
		});
		
		report.page.add_inner_button(__("Print Report"), function() {
			printReport(report);
		});
		
		report.page.add_inner_button(__("Refresh"), function() {
			report.refresh();
		});
		
		// Add statistics after report data is loaded
		report.after_render = function() {
			addStatistics(report);
		};
	}
};

// Export to CSV function
function exportToCSV(report) {
	const data = report.data;
	if (!data || data.length === 0) {
		frappe.msgprint(__("No data to export"));
		return;
	}
	
	// Get columns
	const columns = report.columns;
	let csv = [];
	
	// Add headers
	const headers = columns.map(col => `"${col.label}"`).join(',');
	csv.push(headers);
	
	// Add data rows
	data.forEach(row => {
		const rowData = [];
		columns.forEach(col => {
			let value = row[col.fieldname] || '';
			// Clean HTML tags for CSV export
			value = value.replace(/<[^>]*>/g, ' ');
			value = value.replace(/\s+/g, ' ').trim();
			rowData.push(`"${value}"`);
		});
		csv.push(rowData.join(','));
	});
	
	// Download CSV
	const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = `exam_timetable_${frappe.datetime.now_date()}.csv`;
	a.click();
	URL.revokeObjectURL(url);
	
	frappe.show_alert({
		message: __("Report exported successfully"),
		indicator: "green"
	}, 3);
}

// Print report function
function printReport(report) {
	const printWindow = window.open('', '_blank');
	const tableHtml = document.querySelector('.report-container .dt-table').cloneNode(true);
	
	// Get report title
	const title = document.querySelector('.report-title')?.innerText || "Exam Timetable Report";
	
	printWindow.document.write(`
		<!DOCTYPE html>
		<html>
		<head>
			<title>${title}</title>
			<style>
				body {
					font-family: Arial, sans-serif;
					padding: 20px;
					margin: 0;
				}
				h1 {
					color: #667eea;
					margin-bottom: 10px;
				}
				.meta-info {
					color: #666;
					margin-bottom: 20px;
					font-size: 12px;
				}
				table {
					width: 100%;
					border-collapse: collapse;
					margin-top: 20px;
				}
				th {
					background: #667eea;
					color: white;
					padding: 10px;
					text-align: left;
					border: 1px solid #5a67d8;
				}
				td {
					padding: 8px;
					border: 1px solid #ddd;
					vertical-align: top;
				}
				@media print {
					body {
						padding: 0;
					}
					.no-print {
						display: none;
					}
				}
			</style>
		</head>
		<body>
			<h1>${title}</h1>
			<div class="meta-info">
				Generated on: ${new Date().toLocaleString()}<br>
				Filters Applied: ${getFilterSummary(report)}
			</div>
			${tableHtml.outerHTML}
		</body>
		</html>
	`);
	
	printWindow.document.close();
	printWindow.print();
}

// Get filter summary for print
function getFilterSummary(report) {
	const filters = report.filters;
	if (!filters || Object.keys(filters).length === 0) {
		return "None";
	}
	
	const summary = [];
	if (filters.exam_date) summary.push(`Date: ${filters.exam_date}`);
	if (filters.room) summary.push(`Room: ${filters.room}`);
	
	return summary.join(" | ") || "None";
}

// Add statistics cards
function addStatistics(report) {
	// Remove existing stats container if any
	const existingStats = document.querySelector('.custom-stats-container');
	if (existingStats) {
		existingStats.remove();
	}
	
	const data = report.data;
	if (!data || data.length === 0) return;
	
	// Calculate statistics
	let totalHalls = data.length;
	let totalExams = 0;
	let totalStudents = 0;
	
	data.forEach(row => {
		report.columns.forEach(col => {
			if (col.fieldname !== 'hall' && col.fieldname !== 'capacity') {
				const cellValue = row[col.fieldname];
				if (cellValue && cellValue !== '<span style="color: #999;">— No Exam —</span>') {
					totalExams++;
					// Extract student count from HTML
					const match = cellValue.match(/Students:<\/strong>\s*(\d+)/);
					if (match) {
						totalStudents += parseInt(match[1]);
					}
				}
			}
		});
	});
	
	// Create stats container
	const statsContainer = document.createElement('div');
	statsContainer.className = 'custom-stats-container';
	statsContainer.innerHTML = `
		<div class="custom-stat-card">
			<h4>🏛️ Total Exam Halls</h4>
			<div class="stat-value">${totalHalls}</div>
		</div>
		<div class="custom-stat-card">
			<h4>📝 Total Exams Scheduled</h4>
			<div class="stat-value">${totalExams}</div>
		</div>
		<div class="custom-stat-card">
			<h4>👨‍🎓 Total Students</h4>
			<div class="stat-value">${totalStudents}</div>
		</div>
		<div class="custom-stat-card">
			<h4>📅 Generated On</h4>
			<div class="stat-value" style="font-size: 14px;">${frappe.datetime.now_datetime()}</div>
		</div>
	`;
	
	// Insert stats at the top of report
	const reportContainer = document.querySelector('.report-container');
	if (reportContainer) {
		reportContainer.insertBefore(statsContainer, reportContainer.firstChild);
	}
}

// Add tooltip functionality for better UX
frappe.query_reports["Exam Timetable Report"].onload = function(report) {
	// Add tooltips to show detailed info
	$(document).on('mouseenter', '.dt-cell--html div', function() {
		const content = $(this).text();
		if (content && content !== '— No Exam —') {
			$(this).attr('title', content);
		}
	});
};
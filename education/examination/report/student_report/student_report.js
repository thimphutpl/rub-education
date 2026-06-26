// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Student Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 0,
			"default": get_user_company(),
			"hidden": 1  // Hide this filter since we auto-apply it
		},
		{
			"fieldname": "programme",
			"label": __("Programme"),
			"fieldtype": "Link",
			"options": "Programme",
			"reqd": 0
		},
		{
			"fieldname": "academic_term",
			"label": __("Academic Term"),
			"fieldtype": "Link",
			"options": "Academic Term",
			"reqd": 0
		},
		{
			"fieldname": "semester",
			"label": __("Semester"),
			"fieldtype": "Select",
			"options": ["", "1", "2", "3", "4", "5", "6", "7", "8"],
			"reqd": 0
		},
		{
			"fieldname": "student_section",
			"label": __("Student Section"),
			"fieldtype": "Link",
			"options": "Student Section",
			"reqd": 0
		}
	],
	
	// Function to get user's company
	get_user_company: function() {
		let user_company = null;
		
		// Get current user
		let user = frappe.session.user;
		
		// Make synchronous request to get employee company
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Employee",
				filters: {
					"user_id": user,
					"status": "Active"
				},
				fields: ["company"],
				limit: 1
			},
			async: false,
			callback: function(response) {
				if (response.message && response.message.length > 0) {
					user_company = response.message[0].company;
				}
			}
		});
		
		return user_company;
	},
	
	// On load, set the company filter automatically
	onload: function(report) {
		let user_company = this.get_user_company();
		if (user_company) {
			report.set_filter_value("company", user_company);
		}
	},
	
	// Before refresh, ensure company filter is set
	before_refresh: function(report) {
		let user_company = this.get_user_company();
		if (user_company) {
			report.set_filter_value("company", user_company);
		}
	}
};
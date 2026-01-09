# Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
import frappe
from frappe.model.document import Document

class ConferenceTheme(Document):

	def after_insert(self):
		self.assign_panel_roles()


	def on_update(self):
		self.assign_panel_roles()
	

	def assign_panel_roles(self):
		"""
		Assign 'Panel Member' role to all users in the Panel Member child table
		"""
		for row in self.get("panel_member"):
			user = row.user 
			if user:
				self.add_panel_role(user)

	def add_panel_role(self, user):
		"""
		Assign 'Panel Member' role to a specific user if not already assigned
		"""
		if not user:
			return

		if not frappe.db.exists("Has Role", {"parent": user, "role": "Panel Member"}):
			frappe.get_doc({
				"doctype": "Has Role",
				"parent": user,
				"parenttype": "User",
				"parentfield": "roles",
				"role": "Panel Member"
			}).insert(ignore_permissions=True)
			frappe.db.commit()  # commit to save immediately
			frappe.log_error(f"'Panel Member' role assigned to {user}", "Panel Role Assignment")
	

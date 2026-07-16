# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Programme(Document):
	def validate(self):
		# self.validate_assessment()
		pass

	def autoname(self):
		year = str(self.from_date).split("-")[0]
		# from erpnext.accounts.utils import get_autoname_with_number
		from frappe.model.naming import make_autoname

		self.name = self.programme_name+" - "+str(year)

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)
	if "Administrator" in user_roles or "System Manager" in user_roles:
		return
	if "Student" in user_roles:
		college = frappe.db.get_value("Student", {"user":frappe.session.user}, "company")
		return """(
		EXISTS( select 1 from `tabColleges` where `tabColleges`.company = '{college}'
		and `tabColleges`.parent = `tabProgramme`.name)
		)""".format(college=college)
	else:
		college = frappe.db.get_value("Employee", {"user_id":frappe.session.user}, "company")
		return """(
		EXISTS( select 1 from `tabColleges` where `tabColleges`.company = '{college}'
		and `tabColleges`.parent = `tabProgramme`.name)
		)""".format(college=college)
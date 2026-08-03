# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.model.naming import make_autoname



class Module(Document):
	def autoname(self):
		self.name = str(self.module_code)+" - "+str(self.module_title)

	def validate(self):
		if len(self.colleges) > 1:
			self.multi_college_module = 1
		if self.multi_college_module == 1:
			self.validate_multi_college_module()

	def validate_multi_college_module(self):
		pass

	# @frappe.whitelist()
	# def validate_assessment(self):
	# 	total = 0
	# 	for a in self.assessment_item:
	# 		total += flt(a.weightage)
	# 	if flt(total) != 100:
	# 		# frappe.throw("Total Weightage must be 100%")
	# 		pass

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)
	if "Administrator" in user_roles or "System Manager" in user_roles:
		return
	if "Academic Dean" in user_roles:
		college = frappe.db.get_value("Employee", {"user_id":frappe.session.user}, "company")
		return """(
		EXISTS( select 1 from `tabModule College` where `tabModule College`.college = '{college}'
		and `tabModule College`.parent = `tabModule`.name)
		)""".format(college=college)
	if "Student" in user_roles:
		college = frappe.db.get_value("Student", {"user":frappe.session.user}, "company")
		return """(
		EXISTS( select 1 from `tabModule College` where `tabModule College`.college = '{college}'
		and `tabModule College`.parent = `tabModule`.name)
		)""".format(college=college)
	else:
		college = frappe.db.get_value("Employee", {"user_id":frappe.session.user}, "company")
		return """(
		EXISTS( select 1 from `tabModule College` where `tabModule College`.college = '{college}'
		and `tabModule College`.parent = `tabModule`.name)
		)""".format(college=college)

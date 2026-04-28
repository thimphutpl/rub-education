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
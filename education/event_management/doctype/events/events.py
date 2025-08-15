# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Events(Document):
	@frappe.whitelist()
	def has_attendance(self) -> dict[str, bool]:
		ea = frappe.qb.DocType("Event Attendance")
		event_attendance = (
			frappe.qb.from_(ea)
			.select(ea.name)
			.where(
				(ea.docstatus < 2)
				& (ea.event == self.name)
			)
		).run(as_dict=True)

		return {
			"has_attendance": bool(event_attendance)
		}



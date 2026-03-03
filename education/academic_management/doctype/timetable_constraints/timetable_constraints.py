# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_time


class TimetableConstraints(Document):
	def validate(self):
		self.validate_period_overlap()
		self.validate_hours()

	def validate_hours(self):
		if self.max_hours_tutor == 0:
			frappe.throw("Maximum Hours for Tutor in a Day cannot be 0")
		if self.max_hour_per_session == 0:
			frappe.throw("Maximum Teaching Hours Per Session cannot be 0")

	def validate_period_overlap(self):
		periods = []

		for row in self.periods:  # 👈 your child table fieldname
			if not row.from_time or not row.to_time:
				continue

			# --- time validation ---
			from_time = get_time(row.from_time)
			to_time = get_time(row.to_time)

			if from_time >= to_time:
				frappe.throw(
					f"Row {row.idx}: From Time must be before To Time"
				)

			# --- day validation ---
			row_days = get_row_days(row)

			if not row_days:
				frappe.throw(
					f"Row {row.idx}: Please select at least one day"
				)

			# --- overlap check ---
			for existing in periods:

				# ✅ only check if days intersect
				common_days = row_days.intersection(existing["days"])
				if not common_days:
					continue

				# ✅ time overlap logic
				if from_time < existing["to_time"] and to_time > existing["from_time"]:
					frappe.throw(
						f"Time overlap on {', '.join(sorted(common_days)).title()} "
						f"between rows {existing['idx']} and {row.idx}"
					)

			periods.append({
				"idx": row.idx,
				"from_time": from_time,
				"to_time": to_time,
				"days": row_days,
			})


def get_row_days(row):
	days = set()
	for d in [
		"monday",
		"tuesday",
		"wednesday",
		"thursday",
		"friday",
		"saturday",
		"sunday",
	]:
		if row.get(d):
			days.add(d)
	return days

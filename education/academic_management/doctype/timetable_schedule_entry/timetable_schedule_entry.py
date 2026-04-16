# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TimetableScheduleEntry(Document):

	def validate(self):
		self.validate_schedule_overlap()

	def validate_schedule_overlap(self):
		if frappe.db.exists("Timetable Schedule Entry", {"college": self.college, "academic_term": self.academic_term, "module": self.module, "day": self.day, "from_time": [">=", self.from_time],  "to_time": ["<=", self.to_time], "name": ["!=", self.name]}):
			frappe.throw("Timetable Schedule is overlapping with another schedule entry.")
		exists = frappe.db.sql("select 1, period_name from `tabTimetable Constraint Item` where parent = '{}' and {}=1 and from_time >= '{}' and to_time <= '{}'limit 1".format(self.constraint, self.day.lower(), self.from_time, self.to_time),as_dict=1)

		period = ""
		if len(exists) > 0:
			period = exists[0].period_name
			exists = 1
		else:
			exists = 0
		if exists == 1:
			frappe.throw("Your Timetable Schedule Entry cannot be allocated during {}".format(period))
		# 2. Check across other timetable schedules
		conflicts = frappe.db.sql("""
			SELECT name
			FROM `tabTimetable Schedule Entry`
			WHERE tutor = %s
			AND day = %s
			AND name != %s
			AND (
				(%s < to_time AND %s > from_time)
			)
		""", (
			self.tutor,
			self.day,
			self.name or "",   # exclude current doc (important during update)
			self.from_time,
			self.to_time
		),as_dict=1)
		for c in conflicts:
			if c.name:
				frappe.throw("Schedule entry is conflicting with another schedule entry. <a href='app/timetable-schedule-entry/{0}'>{0}</a>".format(c.name))
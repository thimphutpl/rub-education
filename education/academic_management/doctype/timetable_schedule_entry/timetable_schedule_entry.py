# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

from frappe import _
from datetime import timedelta
from frappe.model.document import Document


class TimetableScheduleEntry(Document):

	def validate(self):
		self.validate_schedule_overlap()
	
	
	def validate_schedule_overlap(self):
		if not self.day or not self.from_time or not self.to_time:
			return

		# Convert current schedule time to timedelta
		from_time = timedelta(
			hours=int(str(self.from_time).split(":")[0]),
			minutes=int(str(self.from_time).split(":")[1]),
			seconds=int(str(self.from_time).split(":")[2]),
		)

		to_time = timedelta(
			hours=int(str(self.to_time).split(":")[0]),
			minutes=int(str(self.to_time).split(":")[1]),
			seconds=int(str(self.to_time).split(":")[2]),
		)

		constraint = frappe.db.get_value(
			"Timetable Constraints",
			{
				"academic_term": self.academic_term,
				"college": self.college
			},
			"name"
		)

		if constraint:
			day_field = self.day.lower()

			constraint_items = frappe.get_all(
				"Timetable Constraint Item",
				filters={
					"parent": constraint,
					day_field: 1
				},
				fields=["period_name", "from_time", "to_time", "allow_overlap"]
			)

			for item in constraint_items:
				if item.allow_overlap:
					continue

				if (
					item.from_time < to_time
					and item.to_time > from_time
				):
					frappe.throw(
						_("Time overlaps with Period {0} ({1} - {2}) on {3}.")
						.format(
							item.period_name,
							item.from_time,
							item.to_time,
							self.day
						)
					)

		# Student Section
		if self.student_section:
			conflict = frappe.db.exists(
				"Timetable Schedule Entry",
				{
					"student_section": self.student_section,
					"day": self.day,
					"name": ["!=", self.name],
					"from_time": ["<", self.to_time],
					"to_time": [">", self.from_time],
				},
			)

			if conflict:
				frappe.throw(
					_("Time overlap for Student Section {0} on {1}.")
					.format(self.student_section, self.day)
				)

		# Class Room
		if self.class_room:
			conflict = frappe.db.exists(
				"Timetable Schedule Entry",
				{
					"class_room": self.class_room,
					"day": self.day,
					"name": ["!=", self.name],
					"from_time": ["<", self.to_time],
					"to_time": [">", self.from_time],
				},
			)

			if conflict:
				frappe.throw(
					_("Time overlap for Class Room {0} on {1}.")
					.format(self.class_room, self.day)
				)

		# Tutor
		if self.tutor:
			conflict = frappe.db.exists(
				"Timetable Schedule Entry",
				{
					"tutor": self.tutor,
					"day": self.day,
					"name": ["!=", self.name],
					"from_time": ["<", self.to_time],
					"to_time": [">", self.from_time],
				},
			)

			if conflict:
				frappe.throw(
					_("Time overlap for Tutor {0} on {1}.")
					.format(self.tutor, self.day)
				)
 
	# def validate_schedule_overlap(self):
	# 	if not self.day or not self.from_time or not self.to_time:
	# 		return
	# 	constraint = frappe.db.get_value(
	# 			"Timetable Constraints",
	# 			{
	# 				"academic_term": self.academic_term,
	# 				"college": self.college

	# 			},
	# 			"name"
	# 		)
	

	# 	if constraint:
	# 		constraint_items = frappe.get_all(
	# 			"Timetable Constraint Item",
	# 			filters={
	# 				"parent": constraint
	# 			},
	# 			fields=["*"]
	# 		)
	# 		frappe.throw(str(constraint_items))

	# 	# Student Section
	# 	if self.student_section:
	# 		conflict = frappe.db.exists(
	# 			"Timetable Schedule Entry",
	# 			{
	# 				"student_section": self.student_section,
	# 				"day": self.day,
	# 				"name": ["!=", self.name],
	# 				"from_time": ["<", self.to_time],
	# 				"to_time": [">", self.from_time],
	# 			},
	# 		)

	# 		if conflict:
	# 			frappe.throw(
	# 				_("Time overlap for Student Section {0} on {1}.")
	# 				.format(self.student_section, self.day)
	# 			)

	# 	# Class Room
	# 	if self.class_room:
	# 		conflict = frappe.db.exists(
	# 			"Timetable Schedule Entry",
	# 			{
	# 				"class_room": self.class_room,
	# 				"day": self.day,
	# 				"name": ["!=", self.name],
	# 				"from_time": ["<", self.to_time],
	# 				"to_time": [">", self.from_time],
	# 			},
	# 		)

	# 		if conflict:
	# 			frappe.throw(
	# 				_("Time overlap for Class Room {0} on {1}.")
	# 				.format(self.class_room, self.day)
	# 			)

	# 	# Tutor
	# 	if self.tutor:
	# 		conflict = frappe.db.exists(
	# 			"Timetable Schedule Entry",
	# 			{
	# 				"tutor": self.tutor,
	# 				"day": self.day,
	# 				"name": ["!=", self.name],
	# 				"from_time": ["<", self.to_time],
	# 				"to_time": [">", self.from_time],
	# 			},
	# 		)

	# 		if conflict:
	# 			frappe.throw(
	# 				_("Time overlap for Tutor {0} on {1}.")
	# 				.format(self.tutor, self.day)
	# 			)
	# def validate_schedule_overlap(self):
	# 	if frappe.db.exists("Timetable Schedule Entry", {"college": self.college, "academic_term": self.academic_term, "module": self.module, "day": self.day, "from_time": [">=", self.from_time],  "to_time": ["<=", self.to_time], "name": ["!=", self.name]}):
	# 		frappe.throw("Timetable Schedule is overlapping with another schedule entry.")
	# 	exists = frappe.db.sql("select 1, period_name, allow_overlap from `tabTimetable Constraint Item` where parent = '{}' and {}=1 and ((from_time>'{}' and from_time<'{}') or  (to_time > '{}' and to_time <'{}'))".format(self.constraint, self.day.lower(), self.from_time, self.to_time, self.from_time, self.to_time),as_dict=1)

	# 	period = ""
	# 	allow_overlap = 0
	# 	if len(exists) > 0:
	# 		for exist in exists:
	# 			if exist.allow_overlap == 0:
	# 				frappe.throw("Your Timetable Schedule Entry cannot be allocated during {}".format(exist.period_name))
	# 		exists = 1
	# 	else:
	# 		exists = 0

	# 	# 2. Check across other timetable schedules
	# 	conflicts = frappe.db.sql("""
	# 		SELECT name
	# 		FROM `tabTimetable Schedule Entry`
	# 		WHERE tutor = %s
	# 		AND day = %s
	# 		AND name != %s
	# 		AND (
	# 			(%s < to_time AND %s > from_time)
	# 		)
	# 	""", (
	# 		self.tutor,
	# 		self.day,
	# 		self.name or "",   # exclude current doc (important during update)
	# 		self.from_time,
	# 		self.to_time
	# 	),as_dict=1)
	# 	for c in conflicts:
	# 		if c.name:
	# 			frappe.throw("Schedule entry is conflicting with another schedule entry. <a href='app/timetable-schedule-entry/{0}'>{0}</a>".format(c.name))


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_programmes_by_college_and_tutor(doctype, txt, searchfield, start, page_len, filters):
	college = filters.get("college")
	tutor = filters.get("tutor")

	if not tutor:
		return []

	return frappe.db.sql("""
		SELECT DISTINCT
			mc.programme
		FROM `tabModule` m

		INNER JOIN `tabModule Tutor Item` mti
			ON mti.parent = m.name

		INNER JOIN `tabModule College` mc
			ON mc.parent = m.name

		WHERE
			mti.tutor = %(tutor)s
			AND mc.college = %(college)s
			AND mc.programme LIKE %(txt)s

		ORDER BY mc.programme
		LIMIT %(start)s, %(page_len)s
	""", {
		"college": college,
		"tutor": tutor,
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len
	})

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_tutor(doctype, txt, searchfield, start, page_len, filters):
	tutor = filters.get("tutor")

	if not tutor:
		return []

	return frappe.db.sql("""
		SELECT DISTINCT
			m.name
		FROM `tabModule` m
		INNER JOIN `tabModule Tutor Item` mti
			ON mti.parent = m.name
		WHERE
			mti.tutor = %(tutor)s
			AND m.name LIKE %(txt)s
		ORDER BY m.name
		LIMIT %(start)s, %(page_len)s
	""", {
		"tutor": tutor,
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len
	})


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_student_sections(doctype, txt, searchfield, start, page_len, filters):
	class_type = filters.get("class_type")
	college = filters.get("college")
	tutor = filters.get("tutor")

	if not class_type:
		return []
	if not college:
		return []
	if not tutor:
		return []

	return frappe.db.sql("""
		SELECT DISTINCT
			mti.student_group
		FROM `tabModule` m
		INNER JOIN `tabModule Tutor Item` mti
			ON mti.parent = m.name
		INNER JOIN `tabModule College` mc
			ON mc.parent = m.name
		WHERE
			mti.class_type = %(class_type)s
			AND mc.college = %(college)s
			AND mti.tutor = %(tutor)s
			AND m.name LIKE %(txt)s

		ORDER BY m.name
		LIMIT %(start)s, %(page_len)s
	""", {
		"class_type": class_type,
		"college": college,
		"tutor": tutor,
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len
	})

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_modules_programme_by_tutor(
	doctype, txt, searchfield, start, page_len, filters
):
	college = filters.get("college")
	tutor = filters.get("tutor")

	if not college or not tutor:
		return []

	return frappe.db.sql("""
		SELECT DISTINCT
			m.name
		FROM `tabModule` m

		INNER JOIN `tabModule Tutor Item` mti
			ON mti.parent = m.name

		INNER JOIN `tabModule College` mc
			ON mc.parent = m.name

		WHERE
			mti.tutor = %(tutor)s
			AND mc.college = %(college)s
			AND m.name LIKE %(txt)s

		ORDER BY m.name
		LIMIT %(start)s, %(page_len)s
	""", {
		"college": college,
		"tutor": tutor,
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len
	})
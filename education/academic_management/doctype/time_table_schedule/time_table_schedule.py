# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import random
from datetime import datetime, time, timedelta
from frappe.model.document import Document

class TimeTableSchedule(Document):
	@frappe.whitelist()
	def generate_timetable(self):
		# Get constraints
		constraint = frappe.get_doc("Timetable Constraints", self.constraint)

		# Clear existing schedule
		self.set("items", [])

		working_days = get_working_days(constraint)
		time_slots = get_time_slots(constraint)
		modules = build_module_workload(constraint)

		# Assign modules recursively
		success = assign_modules(self, constraint, modules, working_days, time_slots, 0)

		if not success:
			frappe.throw("Unable to generate timetable with given constraints")

		# self.save()
		return "Timetable Generated"

# -------------------------
# Helper functions
# -------------------------
def to_time_obj(t):
	"""Convert string or timedelta to time object"""
	if isinstance(t, str):
		return datetime.strptime(t, "%H:%M:%S").time()
	elif isinstance(t, timedelta):
		total_seconds = t.total_seconds()
		h = int(total_seconds // 3600)
		m = int((total_seconds % 3600) // 60)
		s = int(total_seconds % 60)
		return time(h, m, s)
	elif isinstance(t, time):
		return t
	else:
		raise ValueError(f"Unsupported time format: {t}")

def times_overlap(start1, end1, start2, end2):
	s1, e1 = to_time_obj(start1), to_time_obj(end1)
	s2, e2 = to_time_obj(start2), to_time_obj(end2)
	return max(s1, s2) < min(e1, e2)

def build_blocked_slots(constraint):
	blocked = {}
	for period in constraint.periods:
		days = []
		for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
			if getattr(period, d):
				days.append(d.capitalize())
		for day in days:
			blocked.setdefault(day, []).append({
				"from": period.from_time,
				"to": period.to_time
			})
	return blocked

def build_module_workload(constraint):
	modules = []
	for m in constraint.academic_periods:
		modules.append({
			"module": m.module,
			"class_type": m.class_type,
			"room": m.class_room,
			"max_per_week": m.max_hours_per_week,
			"max_per_day": m.max_hours_per_day,
		})
	return modules

def get_working_days(constraint):
	all_days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	off_days = [d.day for d in constraint.weekly_off_days]
	return [d for d in all_days if d not in off_days]

def get_time_slots(constraint):
	# Example slots; adapt if needed
	slots = [
		{"from": "09:00:00", "to": "10:00:00"},
		{"from": "10:00:00", "to": "11:00:00"},
		{"from": "11:00:00", "to": "12:00:00"},
		{"from": "13:00:00", "to": "14:00:00"},
		{"from": "14:00:00", "to": "15:00:00"},
		{"from": "15:00:00", "to": "16:00:00"},
		{"from": "16:00:00", "to": "17:00:00"},
	]
	# Remove non-academic periods
	blocked = [(p.from_time, p.to_time) for p in constraint.periods]
	return [s for s in slots if (s["from"], s["to"]) not in blocked]

def is_valid_slot(doc, constraint, module, day, slot):
	blocked_map = build_blocked_slots(constraint)
	# Block non-academic time
	if day in blocked_map:
		for b in blocked_map[day]:
			if times_overlap(slot["from"], slot["to"], b["from"], b["to"]):
				return False
	# # Block tutor conflicts
	# if count_tutor_day(doc, module["tutor"], day) >= module["max_per_day"]:
	#	 return False
	# Block room conflicts
	for r in doc.items:
		if r.day == day and r.from_time == slot["from"] and r.room == module["room"]:
			return False
	# Block same module adjacent day
	# if is_adjacent_day(doc, module["module"], day):
	#	 return False
	return True

def is_adjacent_day(doc, module_name, day):
	days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	placed_days = [r.day for r in doc.items if r.module == module_name]
	for pd in placed_days:
		if abs(days_order.index(pd) - days_order.index(day)) == 1:
			return True
	return False

def count_module_day(doc, module_name, day):
	return len([r for r in doc.items if r.module == module_name and r.day == day])

def count_tutor_day(doc, tutor, day):
	return len([r for r in doc.items if r.tutor == tutor and r.day == day])

def remove_module_entries(doc, module_name):
	doc.items = [r for r in doc.items if r.module != module_name]

def assign_modules(schedule_doc, constraint, modules, days, slots, index=0):
	"""
	Recursively assigns modules to timetable rows while respecting:
	- tutor allocation from Module -> Module Tutor Item
	- max hours per week/day per module
	- tutor max hours/day/week
	- blocked periods (non-academic)
	- adjacent day rules (optional)
	"""

	if index >= len(modules):
		return True  # All modules assigned

	module_info = modules[index]
	module_doc = frappe.get_doc("Module", module_info["module"])
	tutors = module_doc.get("tutors")  # Module Tutor Item child table
	hours_needed = module_info.get("max_per_week", 0)
	placed_hours = 0

	# Randomize days and slots to avoid patterns
	random_days = days.copy()
	random_slots = slots.copy()
	random.shuffle(random_days)
	random.shuffle(random_slots)

	for day in random_days:
		for slot in random_slots:

			if placed_hours >= hours_needed:
				break

			# Check if module max/day exceeded
			if count_module_day(schedule_doc, module_info["module"], day) >= module_info.get("max_per_day", hours_needed):
				# frappe.msgprint(f"Skipped {day} {slot} because module max/day reached")
				continue

			# Try assigning to any tutor available
			tutor_assigned = None
			for tutor_row in tutors:
				tutor = tutor_row.tutor
				tutor_type = tutor_row.tutor_type
				class_type = tutor_row.class_type

				# Check if tutor is available
				if count_tutor_day(schedule_doc, tutor, day) >= module_info.get("tutor_max_per_day", hours_needed):
					continue
				if count_tutor_total(schedule_doc, tutor) >= module_info.get("tutor_max_per_week", hours_needed):
					continue

				# Check blocked periods
				if not is_valid_slot(schedule_doc, constraint, module_info, day, slot):
					continue

				# Optional: prevent module on adjacent day
				# if is_adjacent_day(schedule_doc, module_info["module"], day):
				# 	continue

				tutor_assigned = tutor
				break  # Found a valid tutor

			if tutor_assigned:
				# Append row only if fully valid
				row = schedule_doc.append("items", {})
				row.day = day
				row.module = module_info["module"]
				row.class_type = class_type
				row.from_time = slot["from"]
				row.to_time = slot["to"]
				row.room = module_info["room"]
				row.tutor = tutor_assigned
				placed_hours += 1

		if placed_hours >= hours_needed:
			break

	# Fail & backtrack if not all hours placed
	if placed_hours < hours_needed:
		remove_module_entries(schedule_doc, module_info["module"])
		return False

	# Move to next module
	if assign_modules(schedule_doc, constraint, modules, days, slots, index + 1):
		return True

	# Backtrack
	# remove_module_entries(schedule_doc, module_info["module"])
	# return False


# ------------------------
# HELPER FUNCTIONS
# ------------------------

def count_module_day(doc, module, day):
	return len([r for r in doc.items if r.module == module and r.day == day])

def count_tutor_day(doc, tutor, day):
	return len([r for r in doc.items if r.tutor == tutor and r.day == day])

def count_tutor_total(doc, tutor):
	return len([r for r in doc.items if r.tutor == tutor])

def remove_module_entries(doc, module):
	doc.items = [r for r in doc.items if r.module != module]

def is_valid_slot(doc, constraint, module, day, slot):
	blocked_map = build_blocked_slots(constraint)
	if day in blocked_map:
		for b in blocked_map[day]:
			if times_overlap(slot["from"], slot["to"], b["from"], b["to"]):
				return False
	# Also check if slot already taken in timetable
	return is_slot_available(doc, day, slot)

def is_adjacent_day(doc, module, day):
	# Checks if same module was scheduled previous or next day
	days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	day_idx = days_order.index(day)
	adjacent_days = []
	if day_idx > 0:
		adjacent_days.append(days_order[day_idx-1])
	if day_idx < len(days_order)-1:
		adjacent_days.append(days_order[day_idx+1])
	for r in doc.items:
		if r.module == module and r.day in adjacent_days:
			return True
	return False

def times_overlap(start1, end1, start2, end2):
	"""
	start1, end1, start2, end2: strings "HH:MM:SS"
	"""
	fmt = "%H:%M:%S"
	if isinstance(start1, timedelta):
		start1 = (datetime.min + start1).strftime(fmt)
	if isinstance(end1, timedelta):
		end1 = (datetime.min + end1).strftime(fmt)
	if isinstance(start2, timedelta):
		start2 = (datetime.min + start2).strftime(fmt)
	if isinstance(end2, timedelta):
		end2 = (datetime.min + end2).strftime(fmt)

	s1 = datetime.strptime(start1, fmt)
	e1 = datetime.strptime(end1, fmt)
	s2 = datetime.strptime(start2, fmt)
	e2 = datetime.strptime(end2, fmt)
	return max(s1, s2) < min(e1, e2)

def is_slot_available(doc, day, slot):
	for r in doc.items:
		if r.day == day and r.from_time == slot["from"]:
			return False
	return True
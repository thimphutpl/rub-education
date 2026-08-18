# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import random
from datetime import datetime, time, timedelta
from frappe.model.document import Document

class TimeTableSchedule(Document):
    def on_submit(self):
        # self.validate_duplicate()
        self.make_tts_entry()

    # def on_cancel(self):
    #     # self.remove_tts_entry()

    def validate_duplicate(self):
        if frappe.db.exists("Time Table Schedule", {"college": self.college, "academic_term": self.academic_term, "programme": self.programme, "constraint": self.constraint, "docstatus": ["!=",2], "name": ["!=", self.name]}):
            frappe.throw("Time Table Schedule already exists for the selected filters.")

    # def make_tts_entry(self):
    #     for tts in self.items:
    #         doc = frappe.new_doc("Timetable Schedule Entry")
    #         doc.flags.ignore_permissions = 1
    #         doc.college = self.college
    #         doc.academic_term = self.academic_term
    #         doc.programme = self.programme
    #         doc.module = tts.module
    #         doc.constraint = self.constraint
    #         doc.class_type = tts.class_type
    #         doc.tutor = tts.tutor
    #         doc.tutor_name = tts.tutor_name
    #         doc.class_room = tts.class_room
    #         doc.room_name = tts.room_name
    #         doc.day = tts.day
    #         doc.from_time = tts.from_time
    #         doc.to_time = tts.to_time
    #         doc.timetable_schedule_id = self.name
    #         doc.insert()
    def make_tts_entry(self):
        for tts in self.items:
            doc = frappe.new_doc("Timetable Schedule Entry")
            doc.flags.ignore_permissions = 1

            doc.college = self.college
            doc.academic_term = self.academic_term
            doc.programme = self.programme
            doc.section = tts.student_section

            doc.module = tts.module
            doc.constraint = self.constraint
            doc.class_type = tts.class_type
            doc.tutor = tts.tutor
            doc.tutor_name = tts.tutor_name
            doc.class_room = tts.class_room
            doc.room_name = tts.room_name
            doc.day = tts.day
            doc.from_time = tts.from_time
            doc.to_time = tts.to_time
            doc.timetable_schedule_id = self.name
            doc.student_section = tts.student_section

            doc.insert()
    
    def remove_ttds_entry(self):
        frape.db.sql("delete from `tabTimetable Schedule Entry` where timetable_schdule_id = '{}'".format(self.name))
        frappe.msgprint("Removed Timetable Schedule Entries linked to this Time Table Schedule")

    # @frappe.whitelist()
    # def generate_timetable(self):
    #     # Get constraints
    #     constraint = frappe.get_doc("Timetable Constraints", self.constraint)

    #     # Clear existing schedule
    #     self.set("items", [])

    #     working_days = get_working_days(constraint)
    #     time_slots = get_time_slots(constraint)
    #     modules = build_module_workload(constraint)
    #     # frappe.throw(str(modules))
    #     # Assign modules recursively
    #     for idx, m in enumerate(modules):
    #         success = assign_modules(self, constraint, modules, working_days, time_slots, index = idx)

    #     if not success:
    #         frappe.throw("Unable to generate timetable with given constraints")

    #     # self.save()
    #     return "Timetable Generated"

    @frappe.whitelist()
    def generate_timetable(self):
        constraint = frappe.get_doc(
            "Timetable Constraints",
            self.constraint
        )
        # Clear existing schedule items
        self.set("items", [])

        working_days = get_working_days(constraint)
        time_slots = get_time_slots(constraint)
        modules = build_module_workload(constraint)
        
        # Get sections belonging to this College + Academic Term + Programme
        sections = get_available_sections(self)
        #frappe.throw(str(sections))
        for section in sections:

            for idx, module_info in enumerate(modules):
                success = assign_modules(
                    self,
                    constraint,
                    modules,
                    working_days,
                    time_slots,
                    index=idx,
                    section=section
                )

                if not success:
                    
                    # frappe.throw(
                    #     "Unable to generate timetable for "
                    #     "Section <b>{0}</b>, Module <b>{1}</b>, "
                    #     "Class Type <b>{2}</b>."
                    #     .format(
                    #         section,
                    #         module_info["module"],
                    #         module_info["class_type"]
                    #     )
                    # )
                    continue

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
    """
    Build non-academic periods by day.

    Example result:

    {
        "Monday": [
            {"from": "08:30:00", "to": "09:30:00"},
            {"from": "11:30:00", "to": "11:40:00"},
            {"from": "13:40:00", "to": "14:40:00"}
        ],
        "Tuesday": [
            ...
        ]
    }
    """

    blocked = {}

    days_map = {
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        "sunday": "Sunday"
    }

    for period in constraint.periods:

        if not period.from_time or not period.to_time:
            continue

        for fieldname, day in days_map.items():

            value = getattr(period, fieldname, 0)

            # Frappe Check fields normally return 0/1
            if value:

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
            "class_room": m.class_room,
            "max_per_week": m.max_hours_per_week,
            "max_per_day": m.max_hours_per_day,
            "max_per_session": constraint.max_hour_per_session,
        })

    return modules

def get_working_days(constraint):
    all_days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    off_days = [d.day for d in constraint.weekly_off_days]
    return [d for d in all_days if d not in off_days]

# def get_time_slots(constraint):
#     # Example slots; adapt if needed
#     slots = [
#         {"from": "09:00:00", "to": "10:00:00"},
#         {"from": "10:00:00", "to": "11:00:00"},
#         {"from": "11:00:00", "to": "12:00:00"},
#         {"from": "13:00:00", "to": "14:00:00"},
#         {"from": "14:00:00", "to": "15:00:00"},
#         {"from": "15:00:00", "to": "16:00:00"},
#         {"from": "16:00:00", "to": "17:00:00"},
#     ]
#     # Remove non-academic periods
#     blocked = [(p.from_time, p.to_time) for p in constraint.periods]
#     return [s for s in slots if (s["from"], s["to"]) not in blocked]

def get_time_slots(constraint):
    if not constraint.start_time:
        frappe.throw("Academic Start Time is not set")

    if not constraint.end_time:
        frappe.throw("Academic End Time is not set")

    start_time = datetime.combine(
        datetime.today(),
        to_time_obj(constraint.start_time)
    )

    end_time = datetime.combine(
        datetime.today(),
        to_time_obj(constraint.end_time)
    )

    # Base timetable slots = 1 hour
    slot_duration = timedelta(hours=1)

    slots = []

    current = start_time

    while current + slot_duration <= end_time:
        slots.append({
            "from": current.strftime("%H:%M:%S"),
            "to": (current + slot_duration).strftime("%H:%M:%S")
        })

        current += slot_duration

    return slots

def is_valid_slot(doc, constraint, module, day, slot):
    blocked_map = build_blocked_slots(constraint)
    # Block non-academic time
    if day in blocked_map:
        for b in blocked_map[day]:
            if times_overlap(slot["from"], slot["to"], b["from"], b["to"]):
                return False
    # # Block tutor conflicts
    # if count_tutor_day(doc, module["tutor"], day) >= module["max_per_day"]:
    #     return False
    # Block room conflicts
    for r in doc.items:
        if r.day == day and r.from_time == slot["from"] and r.room == module["class_room"]:
            return False
    # Block same module adjacent day
    # if is_adjacent_day(doc, module["module"], day):
    #     return False
    return True

def get_consecutive_slots(
    sorted_slots,
    start_slot,
    hours
):

    start_index = None

    for i, slot in enumerate(sorted_slots):

        if (
            slot["from"] == start_slot["from"]
            and slot["to"] == start_slot["to"]
        ):
            start_index = i
            break


    if start_index is None:
        return []


    result = [
        sorted_slots[start_index]
    ]


    current_end = to_time_obj(
        start_slot["to"]
    )


    for slot in sorted_slots[start_index + 1:]:

        if len(result) >= hours:
            break


        if to_time_obj(slot["from"]) == current_end:

            result.append(slot)

            current_end = to_time_obj(
                slot["to"]
            )

        else:
            break


    return result

def get_class_type_hours(constraint, class_type):

    for row in constraint.academic_periods:
        if row.class_type == class_type:
            return row.max_hours_per_day

    return 0

def is_adjacent_day(doc, module_name, day):
    days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    placed_days = [r.day for r in doc.items if r.module == module_name]
    for pd in placed_days:
        if abs(days_order.index(pd) - days_order.index(day)) == 1:
            return True
    return False

def count_tutor_day(doc, tutor, day):
    return len([r for r in doc.items if r.tutor == tutor and r.day == day])

def remove_module_entries(doc, module_name):
    doc.items = [r for r in doc.items if r.module != module_name]

# def assign_modules(schedule_doc, constraint, modules, days, slots, index=0):
#     """
#     Recursively assigns modules to timetable rows while respecting:
#     - tutor allocation from Module -> Module Tutor Item
#     - max hours per week/day per module
#     - tutor max hours/day/week
#     - blocked periods (non-academic)
#     - adjacent day rules (optional)
#     """

#     # if index >= len(modules):
#     #     return True  # All modules assigned

#     module_info = modules[index]
#     # frappe.msgprint(str(module_info))
#     module_doc = frappe.get_doc("Module", module_info["module"])
#     tutors = module_doc.get("tutors")  # Module Tutor Item child table
#     hours_needed = module_info.get("max_per_week", 0)
#     placed_hours = 0

#     # Randomize days and slots to avoid patterns
#     random_days = days.copy()
#     random_slots = slots.copy()
#     random.shuffle(random_days)
#     random.shuffle(random_slots)
#     # frappe.throw(str(random_slots))
#     for day in random_days:
#         for slot in random_slots:

#             if placed_hours >= hours_needed:
#                 break

#             # Check if module max/day exceeded
#             if count_module_day(schedule_doc, module_info["module"], day) >= module_info.get("max_per_day", hours_needed):
#                 # frappe.msgprint(f"Skipped {day} {slot} because module max/day reached")
#                 continue

#             # Try assigning to any tutor available
#             tutor_assigned = None
#             if not tutors or len(tutors) == 0:
#                 frappe.throw("""Tutor is not allocated for module <b><a href="/app/module/{0}">{0}</a></b>""".format(module_info.get("module")))
#             for tutor_row in tutors:
#                 if module_info['class_type'] == tutor_row.class_type:
#                     tutor = tutor_row.tutor
#                     tutor_type = tutor_row.tutor_type
#                     class_type = tutor_row.class_type

#                     # Check if tutor is available
#                     # if count_tutor_day(schedule_doc, tutor, day) >= module_info.get("tutor_max_per_day", hours_needed):
#                     #     continue
#                     # if count_tutor_total(schedule_doc, tutor) >= module_info.get("tutor_max_per_week", hours_needed):
#                     #     continue

#                     # # Check blocked periods
#                     if not is_valid_slot(schedule_doc, constraint, module_info, day, slot, tutor):
#                         continue

#                     # Optional: prevent module on adjacent day
#                     # if is_adjacent_day(schedule_doc, module_info["module"], day):
#                     #     continue

#                     tutor_assigned = tutor
#                     # break  # Found a valid tutor


#             if tutor_assigned:
#                 # Append row only if fully valid
#                 row = schedule_doc.append("items", {})
#                 row.day = day
#                 row.module = module_info.get("module")
#                 # row.class_type = class_type
#                 row.class_type = module_info.get("class_type")
#                 row.class_room = module_info.get("class_room")
#                 row.from_time = slot["from"]
#                 row.to_time = slot["to"]
#                 row.tutor = tutor_assigned
#                 row.tutor_name = frappe.db.get_value("Employee", tutor_assigned, "employee_name")
#                 placed_hours += 1
#             random.shuffle(random_slots)

#         # if placed_hours >= hours_needed:
#         #     break

#     # Fail & backtrack if not all hours placed
#     # if placed_hours < hours_needed:
#     #     remove_module_entries(schedule_doc, module_info["module"])
#     #     return False

#     # Move to next module
#     # if assign_modules(schedule_doc, constraint, modules, days, slots, index + 1):
#     return True

#     # Backtrack
#     # remove_module_entries(schedule_doc, module_info["module"])
#     # return False

def assign_modules(
    schedule_doc,
    constraint,
    modules,
    days,
    slots,
    index=0,
    section=None,
    section_index=0
):

    module_info = modules[index]

    section_class_type = frappe.db.get_value(
        "Student Section",
        section,
        "class_type"
    )

    if section_class_type != module_info["class_type"] or not frappe.db.exists("Module Tutor Item", {"parent": module_info["module"], "student_group": section}):
        return True


    module_doc = frappe.get_doc(
        "Module",
        module_info["module"]
    )

    tutors = module_doc.get("tutors")

    if not tutors:
        frappe.throw(
            "Tutor is not allocated for module {}".format(
                module_info["module"]
            )
        )


    hours_needed = int(
        module_info.get("max_per_week") or 0
    )

    max_per_day = int(
        module_info.get("max_per_day") or hours_needed
    )

    max_per_session = int(
        module_info.get("max_per_session") or 1
    )


    placed_hours = count_module_week(
        schedule_doc,
        module_info["module"],
        section,
        module_info["class_type"]
    )


    # Randomize days
    random_days = list(days)
    random.shuffle(random_days)


    # Keep slots chronological
    sorted_slots = sorted(
        slots,
        key=lambda x: to_time_obj(x["from"])
    )


    while placed_hours < hours_needed:

        allocated = False

        # Randomize days again for each session
        random.shuffle(random_days)

        for day in random_days:

            if placed_hours >= hours_needed:
                break


            # Hours already allocated on this day
            day_hours = count_module_day(
                schedule_doc,
                module_info["module"],
                day,
                section,
                module_info["class_type"]
            )


            remaining_day_hours = max_per_day - day_hours
            remaining_week_hours = hours_needed - placed_hours


            if remaining_day_hours <= 0:
                continue


            # Maximum possible session size
            allowed_session_hours = min(
                max_per_session,
                remaining_day_hours,
                remaining_week_hours
            )


            if allowed_session_hours <= 0:
                continue


            # -----------------------------------------
            # RANDOM SESSION LENGTH
            # -----------------------------------------

            session_hours = random.randint(
                1,
                allowed_session_hours
            )


            # Randomize starting positions
            possible_slots = list(sorted_slots)
            random.shuffle(possible_slots)


            for start_slot in possible_slots:

                consecutive_slots = get_consecutive_slots(
                    sorted_slots,
                    start_slot,
                    session_hours
                )


                # We need the complete requested session
                if len(consecutive_slots) != session_hours:
                    continue


                # -----------------------------------------
                # Find tutor who is available
                # for the ENTIRE session
                # -----------------------------------------

                random_tutors = list(tutors)
                random.shuffle(random_tutors)

                tutor_assigned = None


                for tutor_row in random_tutors:

                    if (
                        tutor_row.class_type
                        != module_info["class_type"]
                    ):
                        continue


                    tutor = tutor_row.tutor

                    session_valid = True


                    for session_slot in consecutive_slots:

                        if not is_valid_slot(
                            schedule_doc,
                            constraint,
                            module_info,
                            day,
                            session_slot,
                            tutor,
                            section
                        ):
                            session_valid = False
                            break


                    if session_valid:

                        tutor_assigned = tutor
                        break


                if not tutor_assigned:
                    continue


                # -----------------------------------------
                # Allocate the ENTIRE random session
                # -----------------------------------------

                for session_slot in consecutive_slots:

                    row = schedule_doc.append(
                        "items",
                        {}
                    )

                    row.student_section = section
                    row.day = day
                    row.module = module_info["module"]
                    row.class_type = module_info["class_type"]
                    row.class_room = module_info["class_room"]

                    row.from_time = session_slot["from"]
                    row.to_time = session_slot["to"]

                    row.tutor = tutor_assigned

                    row.tutor_name = frappe.db.get_value(
                        "Employee",
                        tutor_assigned,
                        "employee_name"
                    )

                    placed_hours += 1


                allocated = True
                break


        # No more possible allocation
        if not allocated:
            break


    return placed_hours >= hours_needed


# ------------------------
# HELPER FUNCTIONS
# ------------------------

# def count_module_day(doc, module, day):
#     return len([r for r in doc.items if r.module == module and r.day == day])
def count_module_day(doc, module, day, section, class_type):
    return len([
        r for r in doc.items
        if r.module == module
        and r.day == day
        and r.student_section == section
        and r.class_type == class_type
    ])

def count_module_week(
    doc,
    module,
    section,
    class_type
):
    return len([
        r for r in doc.items
        if r.module == module
        and r.student_section == section
        and r.class_type == class_type
    ])

def count_consecutive_module_hours(
    doc,
    module,
    day,
    section,
    class_type,
    slot
):
    """
    Count consecutive hours for the same module immediately
    connected to the candidate slot.
    """

    module_slots = [
        r for r in doc.items
        if r.module == module
        and r.day == day
        and r.student_section == section
        and r.class_type == class_type
    ]

    if not module_slots:
        return 1

    candidate_start = to_time_obj(slot["from"])
    candidate_end = to_time_obj(slot["to"])

    consecutive_hours = 1

    # Check backwards
    current_start = candidate_start

    while True:
        previous = None

        for r in module_slots:
            if to_time_obj(r.to_time) == current_start:
                previous = r
                break

        if not previous:
            break

        consecutive_hours += 1
        current_start = to_time_obj(previous.from_time)

    # Check forwards
    current_end = candidate_end

    while True:
        next_row = None

        for r in module_slots:
            if to_time_obj(r.from_time) == current_end:
                next_row = r
                break

        if not next_row:
            break

        consecutive_hours += 1
        current_end = to_time_obj(next_row.to_time)

    return consecutive_hours

def count_tutor_day(doc, tutor, day):
    return len([r for r in doc.items if r.tutor == tutor and r.day == day])

def count_tutor_total(doc, tutor):
    return len([r for r in doc.items if r.tutor == tutor])

def get_available_sections(schedule_doc):
    sections = frappe.get_all(
        "Student Section",
        filters={
            "college": schedule_doc.college,
            "academic_term": schedule_doc.academic_term,
            "program": schedule_doc.programme,
        },
        fields=["name"],
        order_by="name"
    )

    if not sections:
        frappe.throw(
            "No Student Section found for "
            "College <b>{0}</b>, "
            "Academic Term <b>{1}</b>, "
            "Programme <b>{2}</b>."
            .format(
                schedule_doc.college,
                schedule_doc.academic_term,
                schedule_doc.programme
            )
        )

    return [s.name for s in sections]

def remove_module_entries(doc, module):
    doc.items = [r for r in doc.items if r.module != module]

# def is_valid_slot(doc, constraint, module, day, slot):
#     blocked_map = build_blocked_slots(constraint)
#     if day in blocked_map:
#         for b in blocked_map[day]:
#             if times_overlap(slot["from"], slot["to"], b["from"], b["to"]):
#                 return False
#     # Also check if slot already taken in timetable
#     return is_slot_available(doc, day, slot)
# def is_valid_slot(doc, constraint, module, day, slot, tutor):
#     blocked_map = build_blocked_slots(constraint)

#     # Check blocked periods from constraints
#     if day in blocked_map:
#         for b in blocked_map[day]:
#             if times_overlap(slot["from"], slot["to"], b["from"], b["to"]):
#                 return False

#     # Skip slots already used by any module
#     if not is_slot_available(doc, day, slot, tutor):
#         return False

#     return True
def is_valid_slot(
    doc,
    constraint,
    module,
    day,
    slot,
    tutor,
    section
):
    blocked_map = build_blocked_slots(constraint)

    # 1. Check non-academic / blocked periods
    if day in blocked_map:
        for b in blocked_map[day]:
            if times_overlap(
                slot["from"],
                slot["to"],
                b["from"],
                b["to"]
            ):
                return False

    # 2. Check current timetable
    if not is_slot_available(
        doc,
        day,
        slot,
        tutor,
        section
    ):
        return False

    return True

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

# def is_slot_available(doc, day, slot):
#     for r in doc.items:
#         if r.day == day and r.from_time == slot["from"]:
#             return False
#     return True
# def is_slot_available(doc, day, slot, tutor):
#     """
#     Returns True if the given slot is free for the given day, i.e.,
#     it doesn't overlap with any previously assigned module/tutor/room.
#     """
#     for r in doc.items:
#         if r.day == day:
#             if times_overlap(slot["from"], slot["to"], r.from_time, r.to_time):
#                 return False

#     # 2. Check across other timetable schedules
#     conflicts = frappe.db.sql("""
#         SELECT tsi.name
#         FROM `tabTime Table Schedule Item` tsi
#         JOIN `tabTime Table Schedule` ts ON ts.name = tsi.parent
#         WHERE tsi.tutor = %s
#         AND tsi.day = %s
#         AND ts.name != %s
#         AND (
#             (%s < tsi.to_time AND %s > tsi.from_time)
#         )
#     """, (
#         tutor,
#         day,
#         doc.name or "",   # exclude current doc (important during update)
#         slot["from"],
#         slot["to"]
#     ))

#     if conflicts:
#         return False

#     return True

def is_slot_available(doc, day, slot, tutor, section):
    """
    Checks:
    1. Same section cannot have overlapping classes.
    2. Same tutor cannot teach two sections at the same time.
    """

    # --------------------------------------------------
    # Check items already generated in current document
    # --------------------------------------------------

    for r in doc.items:

        if r.day != day:
            continue

        if not times_overlap(
            slot["from"],
            slot["to"],
            r.from_time,
            r.to_time
        ):
            continue

        # Same section -> conflict
        if r.student_section == section:
            return False

        # Same tutor -> conflict
        if r.tutor == tutor:
            return False

    # --------------------------------------------------
    # Check previously submitted schedules
    # --------------------------------------------------

    conflicts = frappe.db.sql(
        """
        SELECT
            tsi.name,
            tsi.student_section as section,
            tsi.tutor
        FROM `tabTime Table Schedule Item` tsi
        INNER JOIN `tabTime Table Schedule` ts
            ON ts.name = tsi.parent
        WHERE
            ts.docstatus = 1
            AND tsi.day = %s
            AND ts.name != %s

            AND (
                %s < tsi.to_time
                AND %s > tsi.from_time
            )

            AND (
                tsi.tutor = %s
                OR (
                    tsi.student_section = %s
                    AND ts.college = %s
                    AND ts.academic_term = %s
                    AND ts.programme = %s
                )
            )
        """,
        (
            day,
            doc.name or "",
            slot["from"],
            slot["to"],
            tutor,
            section,
            doc.college,
            doc.academic_term,
            doc.programme,
        ),
        as_dict=True
    )

    if conflicts:
        return False

    return True
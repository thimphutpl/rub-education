import frappe

# @frappe.whitelist()
# def get_timetable(college, programme, academic_term):
#     timetable = frappe.get_all(
#         "Timetable Schedule Entry",
#         filters={"college": college, "programme": programme, "academic_term": academic_term},
#         fields=["day","from_time","to_time","module_code","tutor","class_type","tutor_name","room_name","called_off"],
#         order_by="from_time asc"
#     )

#     constraint = frappe.get_doc("Timetable Constraints", {"academic_term":academic_term, "college": college})
#     blocked = []
#     if timetable:
#         for p in constraint.periods:
#             period_name = p.period_name or "Non-Academic"
#             for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
#                 if getattr(p, d):
#                     blocked.append({
#                         "day": d.capitalize(),
#                         "from_time": p.from_time,
#                         "to_time": p.to_time,
#                         "period_name": period_name,
#                     })

#     return {
#         "timetable": timetable,
#         "blocked": blocked,
#         "start_time": constraint.start_time,   # NEW
#         "end_time": constraint.end_time, 
#     }


@frappe.whitelist()
def get_timetable(college, programme,academic_term):

	user = frappe.session.user 
	student = frappe.db.get_value( "Student", {"user": user}, "name" )

	enrollments = frappe.get_all( 
		"Module Enrolment", 
		filters={
			"student": student,
			"academic_term": academic_term
		}, 
		fields=[ "course", "student_section" ] 
	)
	enrolled = { 
		( 
			row.course, 
			row.student_section ) 
		for row in enrollments if row.course and row.student_section 
		}
	# frappe.throw(frappe.as_json(enrolled))

	entries = frappe.get_all(
		"Timetable Schedule Entry",
		filters={
			"college": college,
			"programme": programme,
			"academic_term":academic_term
		},
		fields=[
			"name",
			"module",
			"tutor",
			"class_type",
			"session_type",
			"tutor_name",
			"room_name",
			"student_section"
		],
		order_by="name asc"
	)
	# frappe.throw(frappe.as_json(entries))
   


	timetable = []

	for entry in entries:
		

		doc = frappe.get_doc(
			"Timetable Schedule Entry",
			entry.name
		)

		# ---------------------------------------------
		# Get Sections
		# ---------------------------------------------

		sections = []

		if doc.session_type == "Combined":
			

			# For Combined, get ALL sections
			# from Combined Class child table
			for row in doc.combined_class:
				if not row.section:
					continue

				if (
					row.module,
					row.section
				) not in enrolled:
					continue

				if row.section:
					sections.append({
						"module": row.module,
						"section": row.section
					})

		else:
			

			# For normal sessions, use student_section
			if entry.student_section:
			
				if (
					entry.module,
					entry.student_section
				) not in enrolled:
					continue
					# frappe.throw(frappe.as_json((entry.module, entry.student_section)))
				sections.append({
					"module": entry.module,
					"section": entry.student_section
				})

		# ---------------------------------------------
		# Get Academic Timing
		# ---------------------------------------------
		# frappe.throw(str(sections))
		for timing in doc.academic_timing:

			timetable.append({
				"name": entry.name,

				"day": timing.day,
				"from_time": timing.from_time,
				"to_time": timing.to_time,
				"called_off": timing.called_off,

				"module": entry.module,
				"tutor": entry.tutor,
				"class_type": entry.class_type,
				"session_type": entry.session_type,
				"tutor_name": entry.tutor_name,
				"room_name": entry.room_name,

				# Sections to display
				"sections": sections
			})

	# ---------------------------------------------
	# Timetable Constraints
	# ---------------------------------------------

	constraint = frappe.get_doc(
		"Timetable Constraints",
		{
			"academic_term": academic_term,
			"college": college
		}
	)

	# blocked = []

	# for p in constraint.periods:

	#     blocked.append({
	#         "period_name": p.period_name or "Non-Academic",
	#         "from_time": p.from_time,
	#         "to_time": p.to_time
	#     })

	blocked = []

	days = [
		"monday",
		"tuesday",
		"wednesday",
		"thursday",
		"friday",
		"saturday",
		"sunday"
	]

	for p in constraint.periods:

		for day in days:

			if getattr(p, day, 0):

				blocked.append({
					"day": day.capitalize(),
					"period_name": p.period_name or "Non-Academic",
					"from_time": p.from_time,
					"to_time": p.to_time
				})

	# ---------------------------------------------
	# Return
	# ---------------------------------------------
	# frappe.throw(str(timetable))
	return {
		"timetable": timetable,
		"blocked": blocked,
		"start_time": constraint.start_time,
		"end_time": constraint.end_time
	}




# @frappe.whitelist()
# def get_timetable_tutor(college, tutor, academic_term):
#     timetable = frappe.get_all(
#         "Timetable Schedule Entry",
#         filters={"college": college, "tutor": tutor, "academic_term": academic_term},
#         fields=["day","from_time","to_time","module_code","tutor","class_type","tutor_name","room_name","called_off"],
#         order_by="from_time asc"
#     )

#     constraint = frappe.get_doc("Timetable Constraints", {"academic_term":academic_term, "college": college})
#     blocked = []
#     if timetable:
#         for p in constraint.periods:
#             period_name = p.period_name or "Non-Academic"
#             for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
#                 if getattr(p, d):
#                     blocked.append({
#                         "day": d.capitalize(),
#                         "from_time": p.from_time,
#                         "to_time": p.to_time,
#                         "period_name": period_name
#                     })

#     return {
#         "timetable": timetable,
#         "blocked": blocked,
#         "start_time": constraint.start_time,   # NEW
#         "end_time": constraint.end_time, 
#     }

# @frappe.whitelist()
# def get_timetable_tutor(college, tutor, academic_term):

#     entries = frappe.get_all(
#         "Timetable Schedule Entry",
#         filters={
#             "college": college,
#             "tutor": tutor,
#             "academic_term": academic_term
#         },
#         fields=[
#             "name",
#             "module_code",
#             "tutor",
#             "class_type",
#             "session_type",
#             "tutor_name",
#             "room_name"
#         ],
#         order_by="name asc"
#     )

#     timetable = []

#     for entry in entries:

#         doc = frappe.get_doc(
#             "Timetable Schedule Entry",
#             entry.name
#         )

#         # ---------------------------------------------
#         # Get Combined Class
#         # ---------------------------------------------

#         combined_class = []

#         if doc.session_type == "Combined":

#             for row in doc.combined_class:

#                 combined_class.append({
#                     "module": row.module,
#                     "section": row.section
#                 })

#         # ---------------------------------------------
#         # Get Academic Timing
#         # ---------------------------------------------

#         for timing in doc.academic_timing:

#             timetable.append({
#                 "name": entry.name,
#                 "day": timing.day,
#                 "from_time": timing.from_time,
#                 "to_time": timing.to_time,
#                 "called_off": timing.called_off,
#                 "module_code": entry.module_code,
#                 "tutor": entry.tutor,
#                 "class_type": entry.class_type,
#                 "session_type": entry.session_type,
#                 "tutor_name": entry.tutor_name,
#                 "room_name": entry.room_name,
#                 "combined_class": combined_class
#             })


#     # ---------------------------------------------
#     # Timetable Constraints
#     # ---------------------------------------------

#     constraint = frappe.get_doc(
#         "Timetable Constraints",
#         {
#             "academic_term": academic_term,
#             "college": college
#         }
#     )

#     blocked = []

#     if timetable:

#         for p in constraint.periods:

#             period_name = p.period_name or "Non-Academic"

#             blocked.append({
#                 "period_name": period_name,
#                 "from_time": p.from_time,
#                 "to_time": p.to_time
#             })


#     return {
#         "timetable": timetable,
#         "blocked": blocked,
#         "start_time": constraint.start_time,
#         "end_time": constraint.end_time
#     }

@frappe.whitelist()
def get_timetable_tutor(college, tutor, academic_term):

	entries = frappe.get_all(
		"Timetable Schedule Entry",
		filters={
			"college": college,
			"tutor": tutor,
			"academic_term": academic_term
		},
		fields=[
			"name",
			"module_code",
			"tutor",
			"class_type",
			"session_type",
			"tutor_name",
			"room_name",
			"student_section"
		],
		order_by="name asc"
	)

	timetable = []

	for entry in entries:

		doc = frappe.get_doc(
			"Timetable Schedule Entry",
			entry.name
		)

		# ---------------------------------------------
		# Get Sections
		# ---------------------------------------------

		sections = []

		if doc.session_type == "Combined":

			# For Combined, get ALL sections
			# from Combined Class child table
			for row in doc.combined_class:

				if row.section:
					sections.append({
						"module": row.module,
						"section": row.section
					})

		else:

			# For normal sessions, use student_section
			if entry.student_section:
				sections.append({
					"module": entry.module_code,
					"section": entry.student_section
				})

		# ---------------------------------------------
		# Get Academic Timing
		# ---------------------------------------------

		for timing in doc.academic_timing:

			timetable.append({
				"wname": entry.name,

				"day": timing.day,
				"from_time": timing.from_time,
				"to_time": timing.to_time,
				"called_off": timing.called_off,

				"module_code": entry.module_code,
				"tutor": entry.tutor,
				"class_type": entry.class_type,
				"session_type": entry.session_type,
				"tutor_name": entry.tutor_name,
				"room_name": entry.room_name,

				# Sections to display
				"sections": sections
			})

	# ---------------------------------------------
	# Timetable Constraints
	# ---------------------------------------------

	constraint = frappe.get_doc(
		"Timetable Constraints",
		{
			"academic_term": academic_term,
			"college": college
		}
	)

	# blocked = []

	# for p in constraint.periods:

	#     blocked.append({
	#         "period_name": p.period_name or "Non-Academic",
	#         "from_time": p.from_time,
	#         "to_time": p.to_time
	#     })

	blocked = []

	days = [
		"monday",
		"tuesday",
		"wednesday",
		"thursday",
		"friday",
		"saturday",
		"sunday"
	]

	for p in constraint.periods:

		for day in days:

			if getattr(p, day, 0):

				blocked.append({
					"day": day.capitalize(),
					"period_name": p.period_name or "Non-Academic",
					"from_time": p.from_time,
					"to_time": p.to_time
				})

	# ---------------------------------------------
	# Return
	# ---------------------------------------------
	return {
		"timetable": timetable,
		"blocked": blocked,
		"start_time": constraint.start_time,
		"end_time": constraint.end_time
	}


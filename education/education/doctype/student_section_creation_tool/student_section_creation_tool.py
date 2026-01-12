# Copyright (c) 2015, Frappe and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document

from education.education.doctype.student_section.student_section import get_students


class StudentSectionCreationTool(Document):
	def validate(self):
		self.validate_existing()

	def validate_existing(self):
		if self.batch:
			if frappe.exists("Student Section Creation Tool", {"college": self.college, "academic_term": self.academic_term, "batch": self.batch, "name": ["!=", self.name]}):
				frappe.throw("Student Section Creation Tool alraedy exists for: Student Batch: {}\nAcademic Term: {}\nCollege: {}\nExisting Doc: {}".format(self.student_batch, self.academic_term, self.college, frappe.db.get_value("Student Section Creation Tool", {"college": self.college, "academic_term": self.academic_term, "batch": self.batch, "name": ["!=", self.name]}, "name")))


	@frappe.whitelist()
	def get_courses(self):
		group_list = []

		batches = frappe.db.sql(
			"""select name as batch from `tabStudent Batch Name`""", as_dict=1
		)
		for batch in batches:
			group_list.append({"group_based_on": "Batch", "batch": batch.batch})

		courses = frappe.db.sql(
			"""select course, course_name from `tabProgram Course` where parent=%s""",
			(self.program),
			as_dict=1,
		)
		if self.separate_groups:
			from itertools import product

			course_list = product(courses, batches)
			for course in course_list:
				temp_dict = {}
				temp_dict.update({"group_based_on": "Course"})
				temp_dict.update(course[0])
				temp_dict.update(course[1])
				group_list.append(temp_dict)
		else:
			for course in courses:
				course.update({"group_based_on": "Course"})
				group_list.append(course)

		for group in group_list:
			if group.get("group_based_on") == "Batch":
				student_group_name = (
					self.program
					+ "/"
					+ group.get("batch")
					+ "/"
					+ (self.academic_term if self.academic_term else self.academic_year)
				)
				group.update({"student_group_name": student_group_name})
			elif group.get("group_based_on") == "Course":
				student_group_name = (
					group.get("course")
					+ "/"
					+ self.program
					+ ("/" + group.get("batch") if group.get("batch") else "")
					+ "/"
					+ (self.academic_term if self.academic_term else self.academic_year)
				)
				group.update({"student_group_name": student_group_name})

		return group_list

	@frappe.whitelist()
	def get_students(self, programme, college, batch=None):
		self.set("students", [])
		if not (programme and college):
			frappe.throw(_("Please select all the mandatory fields"))

		# frappe.throw(str(programme)+" "+str(college)+" "+str(batch))
		students = frappe.get_all(
			"Student",
			filters={
				"programme": programme,
				"company": college,
				# "semester": semester,
				"student_batch": batch,
				"status": 'Active',
			},
			order_by="student_name",
			fields=["name", "student_name"],
		 )
		return students

	@frappe.whitelist()
	def create_student_groups(self):
		# if not self.courses:
		# 	frappe.throw(_("""No Student Section created."""))

		# l = len(self.courses)
		# for d in self.courses:
		# 	if not d.student_group_name:
		# 		frappe.throw(_("Student Group Name is mandatory in row {0}").format(d.idx))

		# 	if d.group_based_on == "Course" and not d.course:
		# 		frappe.throw(_("Course is mandatory in row {0}").format(d.idx))

		# 	if d.group_based_on == "Batch" and not d.batch:
		# 		frappe.throw(_("Batch is mandatory in row {0}").format(d.idx))

		# 	frappe.publish_realtime(
		# 		"student_group_creation_progress",
		# 		{"progress": [d.idx, l]},
		# 		user=frappe.session.user,
		# 	)

		# 	student_group = frappe.new_doc("Student Group")
		# 	student_group.student_group_name = d.student_group_name
		# 	student_group.group_based_on = d.group_based_on
		# 	student_group.program = self.program
		# 	student_group.course = d.course
		# 	student_group.batch = d.batch
		# 	student_group.max_strength = d.max_strength
		# 	student_group.academic_term = self.academic_term
		# 	student_group.academic_year = self.academic_year
		# 	# student_list = get_students(
		# 	# 	self.academic_year,
		# 	# 	d.group_based_on,
		# 	# 	self.academic_term,
		# 	# 	self.program,
		# 	# 	d.batch,
		# 	# 	d.course,
		# 	# )
		# 	student_list = []

		# 	for student in student_list:
		# 		student_group.append("students", student)
		# 	student_group.save()

		# frappe.msgprint(_("{0} Student Groups created.").format(l))
	
		# if not self.courses:
		# 	frappe.throw(_("""No Student Section created."""))

		l = len(self.courses)
		sections = {}
		for d in self.students:
			if d.section_name not in sections:
				sections.update(d.section_name)
		for d in sections:
			student_group = frappe.new_doc("Student Section")
			student_group.student_group_name = d
			student_group.group_based_on = self.group_based_on
			student_group.program = self.program
			student_group.course = self.course
			student_group.batch = self.batch
			student_group.max_strength = self.max_strength
			student_group.academic_term = self.academic_term
			student_group.academic_year = self.academic_year
			student_list = []
			for student in self.students:
				if student.section_name == d:
					student_group.append("students", student)
			student_group.save()

		frappe.msgprint(_("{0} Student Sections created.").format(l))

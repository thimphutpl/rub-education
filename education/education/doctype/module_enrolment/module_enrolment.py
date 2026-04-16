# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from functools import reduce

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form
from datetime import datetime

class ModuleEnrolment(Document):
	def validate(self):
		self.validate_duplication()
		self.validate_deadline()

	def validate_deadline(self):
		deadline = frappe.db.get_value("Module Enrolment Key", self.module_enrollment_key, "deadline")
		if datetime.strptime(str(self.enrollment_date), "%Y-%m-%d").date() > datetime.strptime(str(deadline), "%Y-%m-%d").date():
			frappe.throw("Module Enrolment for this Module Enrolement Key has expired. Please contact your module tutor if extension is required.", title="Deadline Exceeded")

	def get_progress(self, student):
		"""
		Returns Progress of given student for a particular course enrollment

		        :param self: Course Enrollment Object
		        :param student: Student Object
		"""
		course = frappe.get_doc("Course", self.course)
		topics = course.get_topics()
		progress = []
		for topic in topics:
			progress.append(student.get_topic_progress(self.name, topic))
		if progress:
			return reduce(lambda x, y: x + y, progress)  # Flatten out the List
		else:
			return []

	def validate_duplication(self):
		enrollment = frappe.db.exists(
			"Module Enrolment",
			{
				"student": self.student,
				"course": self.course,
				"academic_term": self.academic_term,
				"docstatus": ["!=", 2],
				"name": ("!=", self.name),
			},
		)
		if enrollment:
			frappe.throw(
				_("Student is already enrolled via Module Enrolment {0}").format(
					get_link_to_form("Module Enrolment", enrollment)
				),
				title=_("Duplicate Entry"),
			)

	@frappe.whitelist()
	def get_module_tutor(self):
		self.set("tutors", [])
		if not self.module_enrollment_key:
			frappe.throw("Please select Module Enrolment Key")
		for t in frappe.get_all("Module Tutor Item", {"parent": self.course, "student_group": self.student_section}, ["tutor", "tutor_name", "class_type"]):
			row = self.append("tutors",{})
			row.tutor = t.tutor
			row.tutor_name = t.tutor_name
			row.class_type = t.class_type

	def add_quiz_activity(
		self, quiz_name, quiz_response, answers, score, status, time_taken
	):
		result = {k: ("Correct" if v else "Wrong") for k, v in answers.items()}
		result_data = []
		for key in answers:
			item = {}
			item["question"] = key
			item["quiz_result"] = result[key]
			try:
				if not quiz_response[key]:
					item["selected_option"] = "Unattempted"
				elif isinstance(quiz_response[key], list):
					item["selected_option"] = ", ".join(
						frappe.get_value("Options", res, "option") for res in quiz_response[key]
					)
				else:
					item["selected_option"] = frappe.get_value("Options", quiz_response[key], "option")
			except KeyError:
				item["selected_option"] = "Unattempted"
			result_data.append(item)

		quiz_activity = frappe.get_doc(
			{
				"doctype": "Quiz Activity",
				"enrollment": self.name,
				"quiz": quiz_name,
				"activity_date": frappe.utils.datetime.datetime.now(),
				"result": result_data,
				"score": score,
				"status": status,
				"time_taken": time_taken,
			}
		).insert(ignore_permissions=True)

	def add_activity(self, content_type, content):
		activity = check_activity_exists(self.name, content_type, content)
		if activity:
			return activity
		else:
			activity = frappe.get_doc(
				{
					"doctype": "Course Activity",
					"enrollment": self.name,
					"content_type": content_type,
					"content": content,
					"activity_date": frappe.utils.datetime.datetime.now(),
				}
			)

			activity.insert(ignore_permissions=True)
			return activity.name


def check_activity_exists(enrollment, content_type, content):
	activity = frappe.get_all(
		"Course Activity",
		filters={"enrollment": enrollment, "content_type": content_type, "content": content},
	)
	if activity:
		return activity[0].name
	else:
		return None

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)
	if "Administrator" in user_roles:
		return
	if "Academic Dean" in user_roles:
		return
	if "Student" in user_roles:
		return """(
			name in (select s.name
				from `tabStudent` as s
				where s.name = `tabModule Enrolment`.student
				and s.user= '{user}')
		)""".format(user=user)
	else:
		return """(
		`tabModule Enrolment`.owner = '{user}'
		)""".format(user=user)
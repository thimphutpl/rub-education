# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.desk.form.linked_with import get_linked_doctypes
from frappe.model.document import Document
from frappe.utils import getdate, today
from erpnext import get_default_currency
from frappe.utils.nestedset import get_root_of
from frappe.permissions import (
	add_user_permission,
	get_doc_permissions,
	has_permission,
	remove_user_permission,
)

from education.education.utils import check_content_completion, check_quiz_completion


class Student(Document):
	def autoname(self):
		year = str(self.joining_date).split("-")[0][2:]
		from frappe.model.naming import make_autoname
		college_code = frappe.db.get_value("Company", self.company, "college_code")
		if not college_code:
			frappe.throw(_("College Code is not set in Company {}".format(self.company)))
		if self.is_existing_student == 0:
			self.name = make_autoname(college_code + year + ".####")
		else:
			self.name = self.old_student_id

	def before_validate(self):
		"""Generate email BEFORE validation occurs"""
		# Generate student ID if it's a new record
		if self.is_new() and not self.name and not self.is_existing_student:
			self.autoname()
		
		# Generate email using the student ID (name) as the prefix
		if self.name and self.company:
			if not self.student_email_id or '@' not in self.student_email_id:
				self.generate_student_email()

	def validate(self):
		self.set_title()
		self.validate_dates()
		
		# Ensure email is set and valid
		if not self.student_email_id or '@' not in self.student_email_id:
			self.generate_student_email()
		
		self.validate_identification()
		
		# Create user with the generated email
		if self.student_email_id and '@' in self.student_email_id:
			self.validate_user()
		
		if self.student_applicant:
			self.check_unique()
			self.update_applicant_status()
		

	def generate_student_email(self):
		"""Generate student email using Student ID as prefix: StudentID.CollegeAbbreviation@rub.edu.bt"""
		if not self.name:
			frappe.throw(_("Student ID must be generated before email creation"))
		
		if not self.company:
			frappe.throw(_("Please select a College first"))
		
		# Get college abbreviation from Company
		college_abbr = frappe.db.get_value("Company", self.company, "abbr")
		if not college_abbr:
			frappe.throw(_("College Abbreviation is not set in Company {0}").format(self.company))
		
		# Use the student ID (name) as the email prefix
		# Clean it to ensure it's email-safe (replace dots, dashes, spaces with underscores)
		student_id = self.name.replace('.', '_').replace('-', '_').replace(' ', '_')
		
		# Generate email: StudentID.CollegeAbbreviation@rub.edu.bt
		self.student_email_id = f"{student_id}.{college_abbr}@rub.edu.bt"
		
		# Log for debugging
		frappe.log_error(
			f"Student ID: {self.name} -> Email: {self.student_email_id}", 
			"Student Email Generated"
		)

	def on_update(self):
		if self.status:
			frappe.db.sql("""
				UPDATE `tabHostel Allocation Item`
				SET status = %s
				WHERE student_code = %s
			""", (self.status, self.name))

			frappe.db.commit() 
			frappe.msgprint(
				_("Hostel Allocation Item status updated for Student {0} to {1}")
				.format(self.name, self.status),
				alert=True
			)
		if self.user and self.status:
			self.update_user_permissions()

	def update_user_permissions(self):
		if not self.create_user_permission:
			return
		if not has_permission("User Permission", ptype="write", raise_exception=False):
			return
		user = frappe.get_doc("User", self.user)
		user.flags.ignore_permissions = True
		if "Student" not in user.get("roles"):
			user.append_roles("Student")
		student_user_permission_exists = frappe.db.exists(
			"User Permission", {"allow": "Student", "for_value": self.name, "user": self.user}
		)
		disable_user = frappe.db.exists(
			"User", {"name": self.user, "enabled": 0}
		)
		if disable_user:
			return

		if student_user_permission_exists:
			return
		if not self.programme:
			frappe.throw("set programme")
		add_user_permission("Student", self.name, self.user)
		add_user_permission("Company", self.company, self.user)
		add_user_permission("Programme", self.programme, self.user)

	def validate_identification(self):
		if self.identification_type == "CID":
			if not self.is_numeric_string(self.cid):
				frappe.throw(str(self.identification_type) + " can only contain numeric values.")
			if len(self.cid) != 11:
				frappe.throw("CID should be 11 digits.")

	def set_missing_customer_details(self):
		self.set_customer_group()
		if self.customer:
			self.update_linked_customer()
		else:
			self.create_customer()

	def set_customer_group(self):
		if not self.customer_group:
			self.customer_group = "Student"
			frappe.db.set_value("Student", self.name, "customer_group", "Student")

	def is_numeric_string(self, value):
		try:
			float(value)
			return True
		except (ValueError, TypeError):
			return False

	# Validate Functions
	def set_title(self):
		self.student_name = " ".join(
			filter(None, [self.first_name, self.middle_name, self.last_name])
		)

	def validate_dates(self):
		for sibling in self.siblings:
			if sibling.date_of_birth and getdate(sibling.date_of_birth) > getdate():
				frappe.throw(
					_("Row {0}:Sibling Date of Birth cannot be greater than today.").format(
						sibling.idx
					)
				)

		if self.date_of_birth and getdate(self.date_of_birth) >= getdate():
			frappe.throw(_("Date of Birth cannot be greater than today."))

		if self.date_of_birth and getdate(self.date_of_birth) >= getdate(self.joining_date):
			frappe.throw(_("Date of Birth cannot be greater than Joining Date."))

		if (
			self.joining_date
			and self.date_of_leaving
			and getdate(self.joining_date) > getdate(self.date_of_leaving)
		):
			frappe.throw(_("Joining Date can not be greater than Leaving Date"))

	def validate_user(self):
		"""Create a website user for student creation if not already exists"""
		# Check if user creation should be skipped
		if frappe.db.get_single_value("Education Settings", "user_creation_skip"):
			return
		
		# Ensure email is valid before checking user existence
		if not self.student_email_id or '@' not in self.student_email_id:
			self.generate_student_email()
		
		# Check if user already exists with this email
		if frappe.db.exists("User", self.student_email_id):
			# Get the existing user
			existing_user = frappe.db.get_value("User", self.student_email_id, "name")
			if existing_user:
				self.user = existing_user
			return
		
		# Create user with the proper email
		try:
			student_user = frappe.get_doc(
				{
					"doctype": "User",
					"first_name": self.first_name or "Student",
					"last_name": self.last_name or "",
					"email": self.student_email_id,  # This uses the student ID as prefix
					"gender": self.gender or "",
					"send_welcome_email": 1,
					"enabled":1,
					"user_type": "Website User",
				}
			)
			student_user.insert(ignore_permissions=True)
			student_user.add_roles("Student")
			self.user = student_user.name
			
		except frappe.exceptions.InvalidEmailAddressError as e:
			frappe.log_error(
				f"Failed to create user for {self.name}: {str(e)}", 
				"Student User Creation"
			)
			frappe.msgprint(
				_("Warning: Could not create user. Email {0} might be invalid.").format(
					self.student_email_id
				),
				alert=True
			)
		except Exception as e:
			frappe.log_error(
				f"Failed to create user for {self.name}: {str(e)}", 
				"Student User Creation"
			)

	def check_unique(self):
		"""Validates if the Student Applicant is Unique"""
		student = frappe.get_all(
			"Student",
			{"student_applicant": self.student_applicant, "name": ["!=", self.name]},
			pluck="name",
		)
		if len(student):
			frappe.throw(
				_("Student {0} exist against student applicant {1}").format(
					student[0], self.student_applicant
				)
			)

	def update_applicant_status(self):
		"""Updates Student Applicant status to Admitted"""
		if self.student_applicant:
			frappe.db.set_value(
				"Student Applicant", self.student_applicant, "application_status", "Admitted"
			)

	# End of Validate Functions

	# On Update Functions
	def update_linked_customer(self):
		customer = frappe.get_doc("Customer", self.customer)
		if self.customer_group:
			customer.customer_group = self.customer_group
		customer.customer_name = self.student_name
		customer.image = self.image
		customer.save()

		frappe.msgprint(_("Customer {0} updated").format(customer.name), alert=True)

	def create_customer(self):
		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": self.student_name,
				"customer_group": self.customer_group
				or frappe.db.get_single_value("Selling Settings", "customer_group"),
				"customer_type": "Individual",
				"image": self.image,
			}
		).insert()

		frappe.db.set_value("Student", self.name, "customer", customer.name)
		frappe.msgprint(
			_("Customer {0} created and linked to Student").format(customer.name), alert=True
		)

	def get_all_course_enrollments(self):
		"""Returns a list of course enrollments linked with the current student"""
		course_enrollments = frappe.get_all(
			"Course Enrollment", filters={"student": self.name}, fields=["course", "name"]
		)
		if not course_enrollments:
			return None
		else:
			enrollments = {item["course"]: item["name"] for item in course_enrollments}
			return enrollments

	def get_program_enrollments(self):
		"""Returns a list of course enrollments linked with the current student"""
		program_enrollments = frappe.get_all(
			"Program Enrolment", filters={"student": self.name}, fields=["program"]
		)
		if not program_enrollments:
			return None
		else:
			enrollments = [item["program"] for item in program_enrollments]
			return enrollments

	def get_topic_progress(self, course_enrollment_name, topic):
		"""
		Get Progress Dictionary of a student for a particular topic
		        :param self: Student Object
		        :param course_enrollment_name: Name of the Course Enrollment
		        :param topic: Topic DocType Object
		"""
		contents = topic.get_contents()
		progress = []
		if contents:
			for content in contents:
				if content.doctype in ("Article", "Video"):
					status = check_content_completion(
						content.name, content.doctype, course_enrollment_name
					)
					progress.append(
						{"content": content.name, "content_type": content.doctype, "is_complete": status}
					)
				elif content.doctype == "Quiz":
					status, score, result, time_taken = check_quiz_completion(
						content, course_enrollment_name
					)
					progress.append(
						{
							"content": content.name,
							"content_type": content.doctype,
							"is_complete": status,
							"score": score,
							"result": result,
						}
					)
		return progress

	def enroll_in_program(self, program_name):
		try:
			enrollment = frappe.get_doc(
				{
					"doctype": "Program Enrolment",
					"student": self.name,
					"academic_year": frappe.get_last_doc("Academic Year").name,
					"program": program_name,
					"enrollment_date": frappe.utils.datetime.datetime.now(),
				}
			)
			enrollment.save(ignore_permissions=True)
		except frappe.exceptions.ValidationError:
			enrollment_name = frappe.get_list(
				"Program Enrolment", filters={"student": self.name, "Program": program_name}
			)[0].name
			return frappe.get_doc("Program Enrolment", enrollment_name)
		else:
			enrollment.submit()
			return enrollment

	def enroll_in_course(self, course_name, program_enrollment, enrollment_date=None):
		if enrollment_date is None:
			enrollment_date = frappe.utils.datetime.datetime.now()
		try:
			enrollment = frappe.get_doc(
				{
					"doctype": "Course Enrollment",
					"student": self.name,
					"course": course_name,
					"program_enrollment": program_enrollment,
					"enrollment_date": enrollment_date,
				}
			)
			enrollment.save(ignore_permissions=True)
		except frappe.exceptions.ValidationError:
			enrollment_name = frappe.get_list(
				"Course Enrollment",
				filters={
					"student": self.name,
					"course": course_name,
					"program_enrollment": program_enrollment,
				},
			)[0].name
			return frappe.get_doc("Course Enrollment", enrollment_name)
		else:
			return enrollment


def get_timeline_data(doctype, name):
	"""Return timeline for attendance"""
	return dict(
		frappe.db.sql(
			"""select unix_timestamp(`date`), count(*)
		from `tabStudent Attendance` where
			student=%s
			and `date` > date_sub(curdate(), interval 1 year)
			and docstatus = 1 and status = 'Present'
			group by date""",
			name,
		)
	)

def get_permission_query_conditions(user):
	
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)
	if "Administrator" in user_roles or "System Manager" in user_roles:
		return
	if "Academic Dean" in user_roles  or "ICT Admin" in user_roles:
		college = frappe.db.get_value("Employee", {"user_id":user}, "company")
		
		return """(
			`tabStudent`.company = '{college}'
		)""".format(college=frappe.db.escape(college))
	if "Student" in user_roles:
		return """(
			`tabStudent`.user = '{user}'
		)""".format(user=user)
	else:
		college = frappe.db.get_value("Employee", {"user_id":user}, "company")
		return """(
			`tabStudent`.company = '{college}'
		)""".format(college=frappe.db.escape(college))
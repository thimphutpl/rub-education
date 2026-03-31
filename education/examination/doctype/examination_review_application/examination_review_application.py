# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ExaminationReviewApplication(Document):
	def validate(self):
		self.fetch_exam_marks()
		self.check_duplicate()
		
	def on_submit(self):
		self.check_if_student_failed()

	def check_duplicate(self):
		if self.exam_review_type != 'Exam Re-Assessment':
			duplicate = frappe.db.get_value(
					"Examination Review Application",
					{
						"student": self.student,
						"exam_review_type": ["in", ["Exam Recheck", "Exam Re-Evaluation"]],
						"docstatus": 1,
						"assessment_component": self.assessment_component,
						"module": self.module
					},
					"name"
				)
			if duplicate:
				frappe.throw(
							"Review Application already registered for <b>{}</b> - <b>{}</b>. "
							"The Registered Number is <a href='/app/examination-review-application/{}' target='_blank'>{}</a>".format(
								self.module, self.assessment_component, duplicate, duplicate
							),
							title="Duplicate Review Application Found"
						)
		else:
			duplicate = frappe.db.get_value(
				"Examination Review Application",
				{
					"student": self.student,
					"assessment_component": self.assessment_component,
					"module": self.module,
					"exam_review_type": "Exam Re-Assessment",
					"docstatus": 1
				},
				"name"
			)
			if duplicate:
				frappe.throw(
							"Re-assessment Application already registered for <b>{}</b> - <b>{}</b>. "
							"The Registered Number is <a href='/app/examination-review-application/{}' target='_blank'>{}</a>".format(
								self.module, self.assessment_component, duplicate, duplicate
							),
							title="Duplicate Review Application Found"
						)

	def check_if_student_failed(self):
		if self.exam_review_type == "Exam Re-Assessment":
			# Get assessment component role to determine if tutor filter is needed
			assessment_role = frappe.db.get_value(
				"Assessment Component", 
				self.assessment_component, 
				"assessment_role"
			)
			
			# Build query based on assessment role
			if assessment_role == "Exam Cell":
				# Exam Cell - no tutor filter
				failed_exam = frappe.db.sql("""
					SELECT 
						em.name,
						em.student,
						em.marks_verified,
						eme.passing_marks
					FROM `tabExam Marks` em 
					INNER JOIN `tabExamination Marks Entry` eme 
						ON em.parent = eme.name 
					WHERE 
						em.student = %s
						AND eme.assessment_component = %s
						AND eme.module = %s
						AND eme.semester = %s
						AND eme.academic_term = %s
						AND eme.college = %s
						AND em.marks_verified < eme.passing_marks
				""", 
				(
					self.student, 
					self.assessment_component,
					self.module,
					self.semester,
					self.academic_term,
					self.college
				),
				as_dict=True)
			else:
				# Tutor role - include tutor filter
				failed_exam = frappe.db.sql("""
					SELECT 
						em.name,
						em.student,
						em.marks_verified,
						eme.passing_marks
					FROM `tabExam Marks` em 
					INNER JOIN `tabExamination Marks Entry` eme 
						ON em.parent = eme.name 
					WHERE 
						em.student = %s
						AND eme.assessment_component = %s
						AND eme.module = %s
						AND eme.semester = %s
						AND eme.academic_term = %s
						AND eme.college = %s
						AND eme.tutor = %s
						AND em.marks_verified < eme.passing_marks
				""", 
				(
					self.student, 
					self.assessment_component,
					self.module,
					self.semester,
					self.academic_term,
					self.college,
					self.tutor
				),
				as_dict=True)

			if not failed_exam:
				frappe.throw(
					"Application not needed as you passed for {} module {}".format(
						self.assessment_component, self.module
					)
				)

	def fetch_exam_marks(self):
		# Get assessment component role to determine if tutor filter is needed
		assessment_role = frappe.db.get_value(
			"Assessment Component", 
			self.assessment_component, 
			"assessment_role"
		)
		
		# Build query based on assessment role
		if assessment_role == "Exam Cell":
			# Exam Cell - no tutor filter
			exam_marks = frappe.db.sql("""
				SELECT 
					em.name as exam_mark_id,
					em.marks_verified,
					eme.passing_marks,
					eme.name as examination_marks_entry
				FROM `tabExam Marks` em 
				INNER JOIN `tabExamination Marks Entry` eme 
					ON em.parent = eme.name 
				WHERE 
					em.student = %s
					AND eme.assessment_component = %s
					AND eme.module = %s
					AND eme.semester = %s
					AND eme.academic_term = %s
					AND eme.college = %s
			""", 
			(
				self.student,
				self.assessment_component, 
				self.module, 
				self.semester, 
				self.academic_term, 
				self.college
			),
			as_dict=True)
		else:
			# Tutor role - include tutor filter
			exam_marks = frappe.db.sql("""
				SELECT 
					em.name as exam_mark_id,
					em.marks_verified,
					eme.passing_marks,
					eme.name as examination_marks_entry
				FROM `tabExam Marks` em 
				INNER JOIN `tabExamination Marks Entry` eme 
					ON em.parent = eme.name 
				WHERE 
					em.student = %s
					AND eme.assessment_component = %s
					AND eme.module = %s
					AND eme.semester = %s
					AND eme.academic_term = %s
					AND eme.college = %s
					AND eme.tutor = %s
			""", 
			(
				self.student,
				self.assessment_component, 
				self.module, 
				self.semester, 
				self.academic_term, 
				self.college, 
				self.tutor
			),
			as_dict=True)

		if exam_marks:
			# Set the fetched data to fields
			self.exam_mark_id = exam_marks[0].get('exam_mark_id')
			self.marks_obtained = exam_marks[0].get('marks_verified')
			self.passing_marks = exam_marks[0].get('passing_marks')
			self.examination_marks_entry = exam_marks[0].get('examination_marks_entry')
		else:
			frappe.throw(
				"No Exam Marks found for Student {0} in {1} - {2}".format(
					self.student, self.module, self.assessment_component
				)
			)
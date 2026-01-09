# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ExaminationReviewApplication(Document):
	def validate(self):
		self.fetch_exam_registration()
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
						"docstatus": 1
					},
					"name"
				)
			if duplicate:
					# frappe.throw("Reassement Already registered for for the regualr exam {}. The Registered Number is {}".format(self.examination_registration,duplicate))
				frappe.throw(
							"Review Application already registered for the regular exam <b>{}</b>. "
							"The Registered Number is <a href='/app/examination-registration/{}' target='_blank'>{}</a>".format(
								self.examination_registration, duplicate, duplicate
							),
							title="Duplicate Review Application Found"
						)
		else:
			duplicate = frappe.db.get_value("Examination Review Application",{"student":self.student,"examination_registration":self.examination_registration,"docstatus":1},"name")
			if duplicate:
					# frappe.throw("Reassement Already registered for for the regualr exam {}. The Registered Number is {}".format(self.examination_registration,duplicate))
				frappe.throw(
							"Review Application already registered for the regular exam <b>{}</b>. "
							"The Registered Number is <a href='/app/examination-registration/{}' target='_blank'>{}</a>".format(
								self.examination_registration, duplicate, duplicate
							),
							title="Duplicate Review Application Found"
						)
	def check_if_student_failed(self):
		if self.exam_review_type=="Exam Re-Assessment":
			failed_exam = frappe.db.sql("""
				SELECT  em.student FROM      
				`tabExam Marks` em INNER JOIN      
				`tabExamination Marks Entry` eme      
				ON em.parent = eme.name WHERE      
				em.marks_verified < eme.passing_marks 
				and em.student=%s
				and examination_registration=%s;
			""", 
			(self.student,self.examination_registration),
			as_dict=True)
			if not failed_exam:
				frappe.throw(
					"Application not needed as you passed for {} module {}".format(self.assessment_component,self.module)
				)

	def fetch_exam_registration(self):
		exam_registration = frappe.db.sql("""
			SELECT name 
			FROM `tabExamination Registration`
			WHERE module = %s
			AND semester = %s
			AND academic_term = %s
			AND company = %s
			AND assessment_component = %s
			AND tutor = %s
		""", 
		(self.module, self.semester, self.academic_term, self.college, self.assessment_component, self.tutor),
		as_dict=True)

		if exam_registration:
			self.examination_registration = exam_registration[0].get('name')
		else:
			frappe.throw(_("No Regular Examination Registration found for {0}").format(self.assessment_component))

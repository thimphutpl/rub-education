# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

from hrms.hr.utils import update_student_promotion_history, validate_active_employee


class StudentPromotion(Document):
	# def validate(self):
	# 	validate_active_student(self.employee)

	def before_submit(self):
		if getdate(self.promotion_date) > getdate():
			frappe.throw(
				_("Student Promotion cannot be submitted before Promotion Date"),
				frappe.DocstatusTransitionError,
			)

	def on_submit(self):
		student = frappe.get_doc("Student", self.student)
		student = update_student_promotion_history(student, self.academic_term, self.promotion_details, date=self.promotion_date)

		# if self.revised_ctc:
		# 	employee.ctc = self.revised_ctc

		student.save()

	def on_cancel(self):
		student = frappe.get_doc("Student", self.student)
		student = update_student_work_history(student, self.promotion_details, cancel=True)

		# if self.revised_ctc:
		# 	student.ctc = self.current_ctc

		student.save()

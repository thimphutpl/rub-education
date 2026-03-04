# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class ContinuousAssessmentEntry(Document):
	def validate(self):
		self.fetch_weightage()
		self.check_assesment_component()
		self.check_duplicate_marks_entry()
		self.calculate_weightage_achieved()

	def on_submit(self):
		# self.check_earlier_assesment()
		self.create_assessment_ledger()

	def on_cancel(self):
		self.ignore_linked_doctypes = (
			"Assessment Ledger",
		)
		super().on_cancel()
		self.cancel_assessment_entry()

	def cancel_assessment_entry(self):
		for i in self.items:
			assessment_ledger = frappe.db.get_value(
				"Assessment Ledger",
				{
					"reference_name": self.name,
					
				},
				"name"
			)

			if assessment_ledger:
				frappe.db.sql(
					'''
					UPDATE `tabAssessment Ledger`
					SET is_cancelled = 1
					WHERE name = %s
					''',
					(assessment_ledger,)
				)

		frappe.db.commit()

	def fetch_exam_registration(self):
		if self.exam_type in ('Regular Assessment','Exam Re-Assessment'):
			if self.exam_type=='Regular Assessment':
				exam_registration = frappe.db.sql("""
					SELECT name 
					FROM `tabExamination Registration`
					WHERE module = %s
					AND semester = %s
					AND academic_term = %s
					AND company = %s
					AND assessment_component = %s
					AND tutor = %s
					AND reassesment=0
				""", 
				(self.module, self.semester, self.academic_term, self.college, self.assessment_component, self.tutor),
				as_dict=True)
			elif self.exam_type=='Exam Re-Assessment':
				exam_registration = frappe.db.sql("""
					SELECT name 
					FROM `tabExamination Registration`
					WHERE module = %s
					AND semester = %s
					AND academic_term = %s
					AND company = %s
					AND assessment_component = %s
					AND tutor = %s
					AND reassesment=1 
					order by posting_date DESC limit 1
				""", 
				(self.module, self.semester, self.academic_term, self.college, self.assessment_component, self.tutor),
				as_dict=True)
			else:
				exam_registration = frappe.db.sql("""
					SELECT name 
					FROM `tabExamination Registration`
					WHERE module = %s
					AND semester = %s
					AND academic_term = %s
					AND company = %s
					AND assessment_component = %s
					AND tutor = %s
					order by posting_date DESC limit 1
				""", 
				(self.module, self.semester, self.academic_term, self.college, self.assessment_component, self.tutor),
				as_dict=True)
			


			if exam_registration:
				self.examination_registration = exam_registration[0].get('name')
			else:
				frappe.throw("Examination Registration not found for {}".format(self.assessment_component))
	def check_duplicate_marks_entry(self):
		duplicate = frappe.db.exists("Continuous Assessment Entry",{"college":self.college, "programme":self.programme, "module": self.module, "academic_term":self.academic_term,"tutor":self.tutor,"docstatus":["!=", 2], "assessment_component": self.assessment_component})
		if duplicate:
			frappe.throw("CA Entry already exists.<br> Existing Entry: {}".format(", ".join(str(idx+1)+". "+a for idx, a in enumerate(frappe.get_all("Continuous Assessment Entry",{"college":self.college, "programme":self.programme, "module": self.module, "academic_term":self.academic_term,"tutor":self.tutor,"docstatus":["!=", 2], "assessment_component": self.assessment_component})))))
	def check_assesment_component(self):
		ass_com = frappe.db.exists("Module Assessment Item",{"parent":self.module,"assessment_name":self.assessment_component})
		if not ass_com:
			frappe.throw("The component {} dont exist for module {}".format(self.assessment_component,self.module))


	# def check_earlier_assesment(self):
	# 	for i in self.items:
	# 		assessment_ledger = frappe.db.get_value(
	# 			"Assessment Ledger",
	# 			{
	# 				"student": i.student,
	# 				"assessment_component": self.assessment_component,
	# 				"module": self.module,
	# 				"has_reassessment":0
	# 			},
	# 			"name"
	# 		)

	# 		if assessment_ledger:
	# 			frappe.db.sql(
	# 				'''
	# 				UPDATE `tabAssessment Ledger`
	# 				SET has_reassessment = 1
	# 				WHERE name = %s
	# 				''',
	# 				(assessment_ledger,)
	# 			)

	# 	frappe.db.commit()
			


	def calculate_weightage_achieved(self):
		for i in self.items:
			if i.marks_verified and self.total_marks and self.weightage:
				i.weightage_achieved = float(float(i.marks_verified/self.total_marks)*self.weightage)

	def fetch_weightage(self):
		if self.assessment_component:
			weightage= frappe.get_value("Module Assessment Item",{"assessment_name":self.assessment_component,"parent":self.module},"weightage")
	
		self.weightage = weightage

	def create_assessment_ledger(self):
		for i in self.items:
			programme= frappe.get_value("Student",{"name":i.student},"programme")
			
			doc = frappe.get_doc({
				"doctype": "Assessment Ledger",
				"student": i.student,
				"posting_date":self.posting_date,
				"student_name": i.student_name,
				"academic_year": self.academic_year,
				"academic_term": self.academic_term,
				"marks_obtained": i.marks_verified,
				"semester":self.semester,
				"passing_marks": self.passing_marks,
				"total_marks": self.total_marks,
				"reference_type": self.doctype,
				"reference_name": self.name,
				"has_reassessment": 0,
				"college": self.college,
				"programme": programme,
				"module": self.module,
				"assessment_component": self.assessment_component,
				"tutor": self.tutor,
				"tutor_name": self.tutor_name,
				"assessment_weightage": self.weightage,
				"weightage_achieved": i.weightage_achieved,
			})

			# Insert into database
			# frappe.throw(frappe.as_json(doc))
			doc.insert(ignore_permissions=True)

			# Optionally submit if needed
			doc.submit()

		frappe.msgprint(f"Assessment Ledger created and submitted for {self.examination_registration}")

		

@frappe.whitelist()
def get_students(doc, module_enrolment_key):
	# Step 1: Get students enrolled in the given term & module
	if not module_enrolment_key:
		frappe.throw("Please select Module Enrolment Key")
	doc = json.loads(doc)
	# frappe.throw(frappe.as_json(doc['college']))

	data = frappe.db.sql(
		"""
		select student, student_name
		from `tabModule Enrolment` where module_enrollment_key=%s
		""",
		(module_enrolment_key),
		as_dict=True
	)

	# Step 2: For each student, calculate attendance percentage
	
	# frappe.throw(str(data))
	return data



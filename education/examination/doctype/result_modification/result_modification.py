# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ResultModification(Document):
	def validate(self):
		self.fetch_total_marks()
		self.calculate_weightage_obtained()
		self.calculate_marks()
		self.check_remarks()
		

	def on_submit(self):
		self.update_assessment_ledger()

	def on_cancel(self):
		self.update_assessment_ledger(cancelled=True)

	def calculate_weightage_obtained(self):
		for i in self.items:
			i.new_weightage_obtained = (i.new_marks_obtained/i.total_marks)*i.assessment_weightage

	def update_assessment_ledger(self, cancelled=False):
		
		for i in self.items:

			if i.marks_obtained != i.new_marks_obtained:
				if cancelled:
					frappe.db.set_value(
					"Assessment Ledger",
					i.assessment_ledger,
					{
						"marks_obtained": i.marks_obtained or 0,
						"weightage_achieved": i.weightage_achieved or 0
					}
				)
				else:
					frappe.db.set_value(
						"Assessment Ledger",
						i.assessment_ledger,
						{
							"marks_obtained": i.new_marks_obtained or 0,
							"weightage_achieved": i.new_weightage_obtained or 0
						}
					)

	def check_remarks(self):
		# self.ca_status = if flt(self.ca/self.total_ca) >= 40 then "Pass" else "Fail"
		pass_criteria = frappe.db.get_value(
			"Pass Criteria",
			{"college": self.college},
			[
				"ca_passing_citeria",
				"se_passing_citeria",
				"total_passing_citeria",
				"failed_module"
			],
			as_dict=1
			)
		ca_pass_percentage = pass_criteria.get("ca_passing_citeria", 0) if pass_criteria else 0
		se_pass_percentage = pass_criteria.get("se_passing_citeria", 0) if pass_criteria else 0
		tl_pass_percentage = pass_criteria.get("total_passing_citeria", 0) if pass_criteria else 0
		if self.total_ca and self.total_ca != 0:  # avoid division by zero
			self.ca_status = "Pass" if (frappe.utils.flt(self.ca) / frappe.utils.flt(self.total_ca)) * 100 >= ca_pass_percentage else "Fail"
		else:
			self.ca_status = "Fail"

		if self.total_se and self.total_se != 0:  # avoid division by zero
			self.semester_exam_status = "Pass" if (frappe.utils.flt(self.semester_exam) / frappe.utils.flt(self.total_se)) * 100 >= se_pass_percentage else "Fail"
		else:
			self.semester_exam_status = "Fail"

		self.overall = self.semester_exam + self.ca

		self.overall_status = "Fail"

		if self.ca_status == "Fail":
			self.overall_status = "Fail"
		elif self.semester_exam_status == "Fail":
			self.overall_status = "Fail"
		elif (
			self.ca_status == "Pass" and 
			self.semester_exam_status == "Pass" and 
			self.overall >= tl_pass_percentage
		):
			self.overall_status = "Pass"

	def fetch_total_marks(self):
		# Total Continuous Assessment
		total_ca = frappe.db.sql('''
			SELECT SUM(mai.weightage)
			FROM `tabModule Assessment Item` mai
			INNER JOIN `tabModule Assessment Criteria` mac 
				ON mai.parent = mac.name
			WHERE mac.college = %(college)s
			AND mac.academic_term = %(academic_term)s
			AND mac.programme = %(programme)s
			AND mac.module = %(module)s
			AND mai.assessment_component_type IN ('Continuous Assessment','Continuous Assessment (Theory)')
		''', {
			"college": self.college,
			"academic_term": self.academic_term,
			"programme": self.programme,
			"module":self.module
		})
		# frappe.throw(str(total_ca))

		# Total Semester Exam
		total_se = frappe.db.sql('''
			SELECT SUM(mai.weightage)
			FROM `tabModule Assessment Item` mai
			INNER JOIN `tabModule Assessment Criteria` mac 
				ON mai.parent = mac.name
			WHERE mac.college = %(college)s
			AND mac.academic_term = %(academic_term)s
			AND mac.programme = %(programme)s
			AND mac.module = %(module)s
			AND mai.assessment_component_type = 'Semester Exam'
		''', {
			"college": self.college,
			"academic_term": self.academic_term,
			"programme": self.programme,
			"module":self.module
		})

		# frappe.db.sql returns a list of tuples like [(sum_value,)]
		self.total_ca = total_ca[0][0] if total_ca and total_ca[0][0] else 0
		self.total_se = total_se[0][0] if total_se and total_se[0][0] else 0

	def calculate_marks(self):
		ca_total = 0
		sem_total = 0

		for item in self.items:
			marks = item.new_marks_obtained or 0  # handles None
			weightage = item.assessment_weightage or 0
			total_marks = item.total_marks or 0
			if item.assessment_component_type in ['Continuous Assessment']:
				# ca_total += ((marks/total_marks) * (weightage))
				ca_total += item.new_weightage_obtained
			elif item.assessment_component_type == 'Semester Exam':
				# sem_total += ((marks/total_marks) * (weightage))
				sem_total += item.new_weightage_obtained

		self.ca = ca_total
		self.semester_exam = sem_total

@frappe.whitelist()
def get_students(doc):
    doc = json.loads(doc)

    # Validations
    if not doc.get('module'):
        frappe.throw("Please select Module")
    if not doc.get('academic_term'):
        frappe.throw("Please select Academic Term")
    if not doc.get('college'):
        frappe.throw("Please select College")
    if not doc.get('semester'):
        frappe.throw("Please select Semester")
    if not doc.get('student'):
        frappe.throw("Please select Student")

    data = frappe.db.sql(
        """
        SELECT 
		al.name,
		al.module,
		al.programme,
		al.total_marks,
		al.passing_marks,
		al.marks_obtained,
		al.assessment_weightage,
		al.weightage_achieved,
		al.assessment_component,
		ac.assessment_component_type
		FROM `tabAssessment Ledger` al
		INNER JOIN `tabAssessment Component` ac 
    	ON al.assessment_component = ac.name
		WHERE 
		al.college = %(college)s
		AND al.student = %(student)s
		AND al.academic_term = %(academic_term)s
		AND al.semester = %(semester)s
		AND al.module = %(module)s
		AND al.is_cancelled = 0
		order by ac.assessment_component_type
		
		;

        """,
        {
            "college": doc["college"],
            "student": doc["student"],
            "academic_term": doc["academic_term"],
            "semester": doc["semester"],
            "module": doc["module"]
        },
        as_dict=True
    )

    return data
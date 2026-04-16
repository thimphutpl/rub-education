# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ResultModification(Document):
	def validate(self):
		self.fetch_total_marks()
		self.calculate_marks()
		self.check_remarks()

	def check_remarks(self):
		# self.ca_status = if flt(self.ca/self.total_ca) >= 40 then "Pass" else "Fail"
		if self.total_ca and self.total_ca != 0:  # avoid division by zero
			self.ca_status = "Pass" if (frappe.utils.flt(self.ca) / frappe.utils.flt(self.total_ca)) * 100 >= 40 else "Fail"
		else:
			self.ca_status = "Fail"

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
			if item.assessment_component_type in ['Continuous Assessment']:
				ca_total += marks
			elif item.assessment_component_type == 'Semester Exam':
				sem_total += marks

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
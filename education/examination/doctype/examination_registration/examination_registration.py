# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class ExaminationRegistration(Document):
	def validate(self):
		self.check_assessment_component()
		self.check_duplicate_ass_component()
		self.check_duplicate_ra()
		self.fetch_exam_registration()
		
	def on_submit(self):
		self.check_exam_marks_entry()
	def check_duplicate_ra(self):
		duplicate = frappe.db.get_value("Examination Registration",{"reassesment":1,"examination_registration":self.examination_registration,"docstatus":1},"name")
		if duplicate:
			# frappe.throw("Reassement Already registered for for the regualr exam {}. The Registered Number is {}".format(self.examination_registration,duplicate))
			frappe.throw(
					"Reassessment already registered for the regular exam <b>{}</b>. "
					"The Registered Number is <a href='/app/examination-registration/{}' target='_blank'>{}</a>".format(
						self.examination_registration, duplicate, duplicate
					),
					title="Duplicate Reassessment Found"
				)
	def fetch_exam_registration(self):
		
		if self.reassesment:
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
			(self.module, self.semester, self.academic_term, self.company, self.assessment_component, self.tutor),
			as_dict=True)


			if exam_registration:
				self.examination_registration = exam_registration[0].get('name')
			else:
				frappe.throw("Examination Registration not found for {}".format(self.assessment_component))
	def check_exam_marks_entry(self):
		if int(self.reassesment) == 1 : 
			exam_registration = frappe.db.exists(
			"Examination Marks Entry",
			{

				"examination_registration": self.examination_registration,
				"docstatus":1
			}
			)
			if not exam_registration:
				if not exam_registration:
					frappe.throw(f"You cannot create the reassessment for '{self.examination_registration}' unless you create an examination entry for it first")

	def check_assessment_component(self):
		# Check if the assessment component exists in Module Assessment Item
		ass_com = frappe.db.exists(
			"Module Assessment Item",
			{
				"parent": self.module,
				"assessment_name": self.assessment_component
			}
		)

		if not ass_com:
			frappe.throw(
				"The Assessment Component '{}' does not exist for module '{}'".format(
					self.assessment_component,
					self.module
				)
			)

	def check_duplicate_ass_component(self):
		if int(self.reassesment) == 0 :  # fixed spelling
			duplicate = frappe.db.exists(
				"Examination Registration",
				{
					"company": self.company,
					"assessment_component": self.assessment_component,  # fixed spelling
					"module": self.module,
					"academic_term": self.academic_term,
					"tutor": self.tutor,
					"docstatus":1
				}
			)
			if duplicate:
				frappe.throw(f"""
						The Examination Registration for Assessment Component '{self.assessment_component}'
						already exists for academic term '{self.academic_term}' for tutor '{self.tutor}'.
						You can create registration only for reassessment.
						""")

# @frappe.whitelist()
# def get_students(academic_year,academic_term,module,company):
# 	# frappe.throw("""
# 	# 	SELECT student 
# 	# 	FROM `tabModule Enrollment` 
# 	# 	WHERE academic_term=%s
# 	# 	and course = %s
# 	# 	""",
# 	# 	(academic_term,module))  # <-- parameters must be a tuple

# 	data = frappe.db.sql(
#         """
#         SELECT student, student_name
#         FROM `tabModule Enrollment`
#         WHERE academic_term=%s
#         AND course=%s
#         """,
#         (academic_term, module),  # <-- tuple of parameters
#         as_dict=True
#     )

# 	for student in data:
# 		attendance_percentage = frappe.db.sql(
#         """
#         SELECT     student,    
# 		ROUND(         (SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100,2) AS attendance_percentage 
# 		FROM `tabStudent Attendance` where student=%s;

#         """,
#         (student.student),  
#         as_dict=True
#     	)
# 		student.append({'attendance_percentage':attendance_percentage.attendance_percentage})

	

# 	return data

@frappe.whitelist()
def get_students(academic_year, academic_term, module, company, tutor, reassesment,assesment_component):
	# Step 1: Get students enrolled in the given term & module
	if not assesment_component:
		frappe.throw("Add Assessment Component")
	if not academic_year:
		frappe.throw("Add Academic Year First")
	if not academic_term:
		frappe.throw("Please select Academic Year")
	if not module:
		frappe.throw("Please select Academic Term")
	if not company:
		frappe.throw("Please select College")
	if not tutor:
		frappe.throw("Please select Tutor")
	if not reassesment:
		frappe.throw("Please select reassesment")
	
	if int(reassesment) == 1:
		# frappe.throw("""
		# 	select student, student_name,
		# 	"Review" as datatype from 
		# 	`tabExamination Review Application`
		# 	WHERE academic_term='{}'
		# 	AND module='{}'
		# 	AND college='{}'
		# 	AND tutor='{}'
		# 	AND assesment_component = '{}'
		# 	AND exam_review_type="Exam Re-Assessment"
		# 	""".format(academic_term, module, company, tutor,assesment_component))
		data = frappe.db.sql(
			"""
			select student, student_name,
			"Review" as datatype from 
			`tabExamination Review Application`
			WHERE academic_term=%s
			AND module=%s
			AND college=%s
			AND tutor=%s
			AND assessment_component = %s
			AND exam_review_type="Exam Re-Assessment"
			AND docstatus=1
			""",
			(academic_term, module, company, tutor,assesment_component),
			as_dict=True
		)
	else:
		data = frappe.db.sql(
			"""
			SELECT student, student_name,
			"Course Enrollment" as datatype
			FROM `tabModule Enrollment`
			WHERE academic_term=%s
			AND course=%s
			AND academic_year=%s
			AND college=%s
			AND tutor=%s
			""",
			(academic_term, module, academic_year, company, tutor),
			as_dict=True
		)

		# Step 2: For each student, calculate attendance percentage
		for student in data:
			attendance = frappe.db.sql(
				"""
				SELECT
					ROUND(
						(SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100,
						2
					) AS attendance_percentage
				FROM `tabStudent Attendance`
				WHERE student=%s
				""",
				(student["student"],),
				as_dict=True
			)

			# Handle case where attendance query returns empty result
			student["attendance_percentage"] = attendance[0]["attendance_percentage"] if attendance and attendance[0]["attendance_percentage"] else 0

	return data


# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from education.academic_management.page.semester_result_decl.semester_result_decl import get_results


class ResultDeclaration(Document):
	def on_submit(self):
		self.post_result_entry()

	def validate(self):
		self.check_doc_duplicate()
		self.check_duplicate()
		self.fetch_previous_marks()
		self.calculate_total()
		
		
		# self.fetch_review_type()

	# def fetch_review_type():
	# 	for i in self.items:
	def check_doc_duplicate(self):
		if frappe.db.exists(
			"Result Declaration",
			{
				"exam_type": self.exam_type,
				"college": self.college,
				"academic_term": self.academic_term,
				"semester": self.semester,
				"programme": self.programme,
				"student_section": self.student_section,
				"name": ["!=", self.name]  # exclude current doc
			}
		):
			frappe.throw("Duplicate Result Declaration already exists.")
	def fetch_previous_marks(self):
		for i in self.items:
			if i.result_declaration:
				result_dcl_item = frappe.db.sql("""
					SELECT rei.name, rei.ca, rei.se, rei.weightage_obtained
					FROM `tabResult Entry Item` rei
					INNER JOIN `tabResult Entry` re ON rei.parent = re.name
					WHERE re.student = %s
					AND rei.module = %s
					LIMIT 1
				""", (i.student, i.module), as_dict=True)
				# frappe.throw(str(result_dcl_item))

				# safety check
				if not result_dcl_item:
					continue

				previous_ca = result_dcl_item[0].ca
				previous_se = result_dcl_item[0].se
				previous_total = result_dcl_item[0].weightage_obtained

				i.previous_ca = previous_ca
				i.previous_se = previous_se
				i.previous_total = previous_total


	def calculate_total(self):
		for i in self.items:
			if i.ca_passed and i.se_passed and i.tl_passed:
				i.remark = "Pass"
				i.overall_passed = 1
				if i.review_type in ('Regular Assessment','Exam Recheck'):
					i.total = i.total_achieved
				if i.review_type =='Exam Re-Assessment':
					i.total = 50
				if i.review_type =='Exam Re-Evaluation':
					i.total = (i.previous_total+i.total_achieved)/2
			else:
				i.remark = "Fail"
				i.total = i.total_achieved
				i.overall_passed = 0
				


			

	def post_result_entry(self):
		self.create_result_entries(
			college=self.college,
			programme=self.programme,
			academic_term=self.academic_term  # or self.semester if you have
		)


	def check_duplicate(self):
		
		for i in self.items:
			result = frappe.db.sql("""
				SELECT rei.parent
				FROM `tabResult Entry Item` rei
				INNER JOIN `tabResult Entry` re 
					ON rei.parent = re.name
				WHERE 
					re.student = %s 
					AND rei.module = %s
				ORDER BY re.creation DESC
				LIMIT 1
			""", (i.student, i.module), as_dict=True)

			

			if result:
				i.result_declaration = result[0].parent

	def create_result_entries(self, college, programme, academic_term):

		

		student_map = {}

		# 🔹 Step 1: group by student
		for i in self.items: 
			if not i.student:
				continue
			
			if i.result_declaration:

				result_dcl_item = frappe.db.sql("""
					SELECT rei.name
					FROM `tabResult Entry Item` rei
					INNER JOIN `tabResult Entry` re ON rei.parent = re.name
					WHERE re.student = %s
					AND rei.module = %s
					LIMIT 1
				""", (i.student, i.module), as_dict=True)

				# safety check
				if not result_dcl_item:
					continue

				row_name = result_dcl_item[0].name

				# 🔹 update fields properly
				frappe.db.set_value("Result Entry Item", row_name, {
					"se": i.se,
					"ca": i.ca,
					"passed": i.overall_passed,   # adjust field name if different
					"ca_passed":i.ca_passed,
					"se_passed":i.se_passed,
					"weightage_obtained": i.total,
					"academic_year": self.academic_year
				})

				continue


			if i.student not in student_map:
				student_map[i.student] = []

			student_map[i.student].append(i)

		# 🔹 Step 2: create one doc per student
		for student_id, rows in student_map.items():

			# جلوگیری duplicates
			if frappe.db.exists("Result Entry", {
				"student": student_id,
				"academic_term": academic_term,
				"programme": programme
			}):
				continue

			doc = frappe.new_doc("Result Entry")
			doc.student = student_id
			doc.semester = self.semester
			doc.academic_term = academic_term
			doc.programme = programme
			doc.college = college

			# optional: take from first row
			doc.no_of_modules_failed = rows[0].total_modules_failed

			# 🔹 Step 3: append ALL modules for that student
			for i in rows:
				row = doc.append("table_amrk", {})
				row.module = i.module
				row.ca = i.ca
				row.se = i.se
				row.weightage_obtained = i.total
				row.passed = i.overall_passed
				row.tl_passed = i.tl_passed
				row.ca_passed = i.ca_passed
				row.se_passed = i.se_passed
				row.year_of_passing = self.academic_year

			# 🔹 insert once per student
			doc.insert(ignore_permissions=True)

		frappe.db.commit()


@frappe.whitelist()
def get_results(college, programme, academic_term, student_section, exam_type):

	# ---------------- MODULE ENROLLMENT KEY ----------------
	module_enrollment_key = frappe.db.sql("""
		SELECT name, module
		FROM `tabModule Enrolment Key`
		WHERE college=%s
		AND programme=%s
		AND academic_term=%s
		AND student_section=%s 
		AND docstatus = 1
	""", (college, programme, academic_term, student_section), as_dict=1)

	module_key_list = [m.name for m in module_enrollment_key]
	module_list = list(set([m.module for m in module_enrollment_key]))

	# ---------------- ENROLLED STUDENTS ----------------
	enrolled_students = frappe.db.sql("""
		SELECT student, course as module, student_name
		FROM `tabModule Enrolment`
		WHERE module_enrollment_key IN %s
		ORDER BY student
	""", (tuple(module_key_list),), as_dict=1)

	result = {}

	# frappe.throw(str(enrolled_students))

	# ---------------- MAIN LOOP ----------------
	for i in enrolled_students:

		student = i.student
		student_name = i.student_name
		module = i.module

		# ---------------- CA ----------------
		ca_data = frappe.db.sql("""
			SELECT COALESCE(SUM(al.weightage_achieved), 0) AS total
			FROM `tabAssessment Ledger` al
			INNER JOIN `tabAssessment Component` ac
				ON al.assessment_component = ac.name
			WHERE ac.assessment_component_type IN (
				'Continuous Assessment',
				'Continuous Assessment (Theory)'
			)
			AND al.student = %s
			AND al.module = %s
		""", (student, module), as_dict=1)

		ca = ca_data[0].total if ca_data else 0

		

		# ---------------- SE ----------------
		se_data = frappe.db.sql("""
			SELECT 
				COALESCE(SUM(al.weightage_achieved), 0) AS total,
				eme.exam_type AS exam_type,
				al.name as assessment_ledger
			FROM `tabAssessment Ledger` al
			INNER JOIN `tabAssessment Component` ac
				ON al.assessment_component = ac.name
			INNER JOIN `tabExamination Marks Entry` eme
				ON al.reference_name = eme.name
			WHERE ac.assessment_component_type IN (
				'Semester Exam'
				
			)
			AND al.student = %s
			AND al.module = %s
			AND al.has_reassessment = 0
			AND NOT EXISTS (
			SELECT 1 
			FROM `tabResult Declaration Item` rdi
			WHERE 
				rdi.student = al.student
				AND rdi.module = al.module
				AND rdi.docstatus != 2
				AND rdi.assessment_ledger= al.name
		)
		""", (student, module), as_dict=1)

		

		se = se_data[0].total if se_data else 0
		se_exam_type = se_data[0].exam_type if se_data else None
		assessment_ledger = se_data[0].assessment_ledger if se_data else None
		# ---------------- INITIALIZE STUDENT ----------------
		if student not in result:
			result[student] = {
				"student": student,
				"student_name": student_name,
				"results": {}
			}

		# ---------------- FILTER BY EXAM TYPE ----------------
		if exam_type == "Regular":
			result[student]["results"][module] = {
				"ca": ca,
				"se": se,
				"se_exam_type": se_exam_type,
				"se_assessment_ledger": assessment_ledger
			}

		else:
			# only include if SE exists
			if se > 0:
				result[student]["results"][module] = {
					"ca": ca,
					"se": se,
					"se_exam_type": se_exam_type,
					"se_assessment_ledger": assessment_ledger
				}

	# ---------------- PASS CRITERIA ----------------
	pass_criteria = frappe.db.get_value(
		"Pass Criteria",
		{"college": college},
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
	failed_module_for_repeat = pass_criteria.get("failed_module", 0) if pass_criteria else 0

	# ---------------- WEIGHTAGE MAP ----------------
	weightage_data = frappe.db.sql("""
		SELECT 
			ma.module,

			COALESCE(SUM(CASE 
				WHEN mai.assessment_component_type IN 
					('Continuous Assessment', 'Continuous Assessment (Theory)')
				THEN mai.weightage ELSE 0 
			END), 0) AS ca_total,

			COALESCE(SUM(CASE 
				WHEN mai.assessment_component_type IN 
					('Semester Exam', 'Semester Exam (Theory)')
				THEN mai.weightage ELSE 0 
			END), 0) AS se_total

		FROM `tabModule Assessment Item` mai
		INNER JOIN `tabModule Assessment Criteria` ma
			ON mai.parent = ma.name

		WHERE ma.college = %s
		AND ma.academic_term = %s
		AND ma.module IN %s

		GROUP BY ma.module
	""", (college, academic_term, tuple(module_list)), as_dict=1)

	weightage_map = {d.module: d for d in weightage_data}

	# ---------------- FINAL PASS/FAIL CALC ----------------
	for student, sdata in result.items():

		for module, r in sdata["results"].items():

			w = weightage_map.get(module, {})
			ca_total = w.get("ca_total", 0)
			se_total = w.get("se_total", 0)

			ca_perc = (r["ca"] / ca_total * 100) if ca_total else 0
			se_perc = (r["se"] / se_total * 100) if se_total else 0
			total_perc = ((r["ca"] + r["se"]) / (ca_total + se_total) * 100) if (ca_total + se_total) else 0

			r["ca_pass"] = ca_perc >= ca_pass_percentage
			r["se_pass"] = se_perc >= se_pass_percentage
			r["tl_pass"] = total_perc >= tl_pass_percentage

			r["total"] = r["ca"] + r["se"]

	# frappe.throw(frappe.as_json(result))

	return result

	


	

	


   

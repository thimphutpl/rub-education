# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from education.academic_management.page.semester_result_decl.semester_result_decl import get_results


class ResultDeclaration(Document):
	def on_submit(self):
		self.post_result_entry()

	def post_result_entry(self):
		data = get_results(
			self.college,
			self.programme,
			self.academic_term,
			self.student_section
		)
		# frappe.throw(frappe.as_json(data))

		self.create_result_entries(
			data=data,
			college=self.college,
			programme=self.programme,
			academic_term=self.academic_term  # or self.semester if you have
		)



	def create_result_entries(self,data, college, programme, academic_term):

		for student in data.get("students", []):

			student_id = student.get("student_no")
			no_of_modules_failed = student.get("no_failed_modules")

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
			doc.no_of_modules_failed = no_of_modules_failed

			results = student.get("results", {})

			for module_name, marks in results.items():

				# module_doc = frappe.db.get_value(
				# 	"Module",
				# 	{"name": module_name},
				# 	"name"
				# )

				# if not module_doc:
				# 	frappe.log_error(f"Module not found: {module_name}")
				# 	continue

				row = doc.append("table_amrk", {})
				row.module = module_name
				row.ca = marks.get("ca", 0)
				row.se = marks.get("se", 0)
				row.weightage_obtained = marks.get("tl", 0)
				row.passed = marks.get("tl_pass")
				row.ca_passed = marks.get("ca_pass")
				row.se_passed = marks.get("se_pass")
				# if row.passed == 1:
				row.year_of_passing = self.academic_year

				# # Pass logic
				# row.passed = 1 if row.weightage_obtained >= 50 else 0

			doc.insert(ignore_permissions=True)

		frappe.db.commit()

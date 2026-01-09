from frappe.model.document import Document
import frappe
import pandas as pd
from frappe.utils.file_manager import get_file

class ExamTimetable(Document):
    def validate(self):
        self.validate_capacity()

    def validate_capacity(self):
        """
        Validates that the number of students in the child table
        does not exceed the defined capacity.
        """
        if self.capacity:
            try:
                capacity = int(self.capacity)  # convert to integer
            except ValueError:
                frappe.throw(f"Capacity value '{self.capacity}' is not a valid number.")

            total_students = len(self.get("exam_timetable_student"))
            if total_students > capacity:
                frappe.throw(
                    f"Number of students {total_students} exceeds the capacity {capacity}."
                )


# File Upload Function
@frappe.whitelist()
def upload_excel(file_url, docname):
	"""
	Uploads an Excel file and adds students to the ExamTimetable child table.
	Validates that the total students do not exceed capacity.
	"""
	file_doc = get_file(file_url)
	file_path = file_doc[1]

	df = pd.read_excel(file_path)
	expected_columns = ["Student", "Examination Registration", "Module"]

	for col in expected_columns:
		if col not in df.columns:
			frappe.throw(f"Missing column '{col}' in Excel file.")

	doc = frappe.get_doc("Exam Timetable", docname)
	doc.set("exam_timetable_student", [])  

	for _, row in df.iterrows():
		doc.append("exam_timetable_student", {
			"student": row["Student"],
			"examination_registration": row["Examination Registration"],
			"module": row["Module"]
		})

	doc.validate_capacity()
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return "Success"


# Get Students Function
@frappe.whitelist()
def get_students(academic_year, academic_term, module, company, docname=None):
	"""
	Fetches students from Examination Registration and refreshes
	the ExamTimetable child table (no duplicates).
	"""
	if not academic_year:
		frappe.throw("Please select Academic Year")
	if not academic_term:
		frappe.throw("Please select Academic Term")
	if not module:
		frappe.throw("Please select Module")
	if not company:
		frappe.throw("Please select College")

	exam_regs = frappe.get_all(
		"Examination Registration",
		filters={
			"company": company,
			"academic_year": academic_year,
			"academic_term": academic_term,
			"module": module,
			"docstatus": 1
		},
		fields=["name", "module"]
	)

	data = []
	for reg in exam_regs:
		child_students = frappe.get_all(
			"Exam Students",
			filters={"parent": reg.name},
			fields=["student", "student_name"]
		)
		for s in child_students:
			s["module"] = reg.module
			s["examination_registration"] = reg.name
			data.append(s)

	if docname:
		doc = frappe.get_doc("Exam Timetable", docname)
		doc.set("exam_timetable_student", [])

		for s in data:
			doc.append("exam_timetable_student", {
				"student": s["student"],
				"student_name": s["student_name"],
				"examination_registration": s["examination_registration"],
				"module": s["module"]
			})

		doc.validate_capacity()
		doc.save(ignore_permissions=True)
		frappe.db.commit()

	return data

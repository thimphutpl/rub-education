# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.desk.reportview import get_match_cond


class ModuleEnrollmentTool(Document):
	def validate(self):
		pass

	def on_submit(self):
		if not self.students:
			frappe.throw(_("Please add students to enroll"))

		for d in self.students:
			if not d.student:
				continue
			if frappe.db.exists(
				"Module Enrollment",
				{
					"student": d.student,
					"student_name": d.student_name,
					"module": self.course,
					"academic_term": self.academic_term,
					"college": self.college,
					"student_section": self.student_section,
					"docstatus": 1,
				},
			):
				frappe.msgprint(
					_("{0} is already enrolled in {1}").format(d.student_name, self.course)
				)
				continue

			module_enrollment = frappe.get_doc(
				{
					"doctype": "Module Enrollment",
					"student": d.student,
					"student_name": d.student_name,
					"course": self.course,
					"academic_term": self.academic_term,
					"college": self.college,
					"enrollment_date": self.enrollment_date,
					"semester": self.semester,
					"academic_year": self.academic_year,
					"programme": self.programme,
					"batch": self.batch,
					"tutor": self.tutor,
					"tutor_name": self.tutor_name,
					"student_section": self.student_section
				}
			)
			module_enrollment.insert()
			frappe.msgprint(
				_("{0} enrolled successfully in {1}").format(d.student_name, self.course)
			)

	@frappe.whitelist()
	def get_students(self, programme, course, college, semester, student_section=None, batch=None):
		self.set("students", [])
		if not (programme and course and college and semester):
			frappe.throw(_("Please select all the mandatory fields"))

		enrolled_students = frappe.get_all(
			"Module Enrollment",
			filters={
				"module": course,
				"academic_term": semester,
				"college": college,
				"docstatus": 1
			},
			fields=["student"],
		)
		section_student_list = []
		if student_section:
			section_students = frappe.db.sql("""
				select sss.student from `tabStudent Section Student` sss, `tabStudent Section` ss
				where sss.parent = ss.name
				and ss.name = '{}'
			""".format(student_section), as_dict = 1)
			enrolled_student_list = [d.student for d in enrolled_students]
		else:
			section_students = ""
		if section_students:
			for a in section_students:
				section_student_list.append(a.student)

		if self.student_section:
			students = frappe.get_all(
				"Student",
				filters={
					"programme": programme,
					"company": college,
					"semester": semester,
					"student_batch": batch,
					"status": 'Active',
					"name": ["not in", enrolled_student_list],
					"name": ["in", section_student_list]
				},
				fields=["name", "student_name"],
			)
		else:
			students = frappe.get_all(
				"Student",
				filters={
					"programme": programme,
					"company": college,
					"semester": semester,
					"student_batch": batch,
					"status": 'Active',
					"name": ["not in", enrolled_student_list],
				},
				fields=["name", "student_name"],
			)
		return students

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_programme(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("date"):
		frappe.msgprint(_("Please set <strong>Enrollement Date</strong> or <strong>Posting Date</strong> first."))
		return []
	if filters.get("validate") == 1:
		if not filters.get("college"):
			frappe.msgprint(_("Please select a College first."))
			return []


	doctype = "Programme"
	return frappe.db.sql(
		"""select m.name, m.abbreviation, mc.company as college from `tabProgramme` m, `tabColleges` mc
        where  m.name = mc.parent and mc.company = %(college)s and m.name like %(txt)s
		and %(date)s >= mc.from_date and %(date)s <= mc.to_date
        order by
            if(locate(%(_txt)s, m.name), locate(%(_txt)s, m.name), 99999),
            m.name asc
        limit {start}, {page_len}""".format(
			start=start, page_len=page_len
		),
		{
			"txt": "%{0}%".format(txt),
			"_txt": txt.replace("%", ""),
			"college": filters.get("college"),
			"date": filters.get("date"),
		},
	)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def filter_student_section(doctype, txt, searchfield, start, page_len, filters):
	if filters.get("validate") == 1:
		if not filters.get("college"):
			frappe.msgprint(_("Please select a College."))
			return []
		if not filters.get("academic_term"):
			frappe.msgprint(_("Please select a Academic Term."))
			return []
		if not filters.get("programme"):
			frappe.msgprint(_("Please select a Programme"))
			return []


	doctype = "Student Section"
	return frappe.db.sql(
		"""select ss.name, ss.program, ss.college from `tabStudent Section` ss
        where ss.college = %(college)s and ss.academic_term = %(academic_term)s
		and ss.program = %(programme)s
		and ss.name like %(txt)s
        order by
            if(locate(%(_txt)s, ss.name), locate(%(_txt)s, ss.name), 99999),
            ss.name asc
        limit {start}, {page_len}""".format(
			start=start, page_len=page_len
		),
		{
			"txt": "%{0}%".format(txt),
			"_txt": txt.replace("%", ""),
			"college": filters.get("college"),
			"academic_term": filters.get("academic_term"),
			"programme": filters.get("programme"),
		},
	)

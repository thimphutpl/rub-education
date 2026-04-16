# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ResearchCenterReportingItems(Document):

	def on_submit(self):
		self.update_employee_journals()
		self.update_student_journals()

	def on_cancel(self):
		self.remove_records("Employee", self.employee)
		self.remove_records("Student", self.student)	

	# UPDATE EMPLOYEE
	def update_employee_journals(self):
		if not self.employee:
			return

		if self.sub_reporting_type == "Research Articles":	

			employees = (
				(self.first_author_employee or []) +
				(self.second_author_employee or []) +
				(self.third_author_employee or [])
			)
			for row in employees:
				emp_doc = frappe.get_doc("Employee", row.employee)
				emp_doc.append("research_articles", {
					"research_reference": self.name,
					"fiscal_year": self.year,
					"title": self.research_articles_title,
					"publisher": self.publisher,
					"website_link": self.website_link_articles
				})

				emp_doc.flags.ignore_permissions = True
				emp_doc.save()

		elif self.sub_reporting_type == "Journals":
			for row in employees:
				emp_doc = frappe.get_doc("Employee", row.employee)
				emp_doc.append("journals", {
					"research_reference": self.name,
					"year": self.year,
					"name_of_the_journal": self.name_of_the_journal,
					"vol_no_journal": self.vol_no_journal,
					"issue_no_journal": self.issue_no_journal,
					"website_links_journal": self.website_links_journal
				})

				emp_doc.flags.ignore_permissions = True
				emp_doc.save()

		elif self.sub_reporting_type == "Conference Seminar Paper":
			for row in employees:
				emp_doc = frappe.get_doc("Employee", row.employee)
				emp_doc.append("conference_seminar_paper", {
					"research_reference": self.name,
					"year": self.year,
					"conference_seminar_paper_title": self.title,
					"conferenceseminar_title": self.conferenceseminar_title,
					"date": self.date,
					"nationalinternational": self.nationalinternational
				})

				emp_doc.flags.ignore_permissions = True
				emp_doc.save()

		elif self.sub_reporting_type == "Book Chapters":
			for row in employees:
				emp_doc = frappe.get_doc("Employee", row.employee)
				emp_doc.append("conference_seminar_paper", {
					"research_reference": self.name,
					"year": self.year,
					"book_chapter_title": self.book_chapter_title,
					"book_title": self.book_title,
					"publisher": self.publishers,
					"website_link_books": self.website_link_books
				})

				emp_doc.flags.ignore_permissions = True
				emp_doc.save()	

		elif self.sub_reporting_type == "Training and workshop":
			for row in employees:
				emp_doc = frappe.get_doc("Employee", row.employee)
				emp_doc.append("conference_seminar_paper", {
					"research_reference": self.name,
					"year": self.year,
					"trainings_organized_title": self.trainings_organized_title,
					"no_of_staffs_engaged": self.no_of_staffs_engaged,
					"no_of_student_engaged": self.no_of_student_engaged,
					"no_of_external_participants": self.no_of_external_participants,
					"venue": self.venues,
					"funding_source": self.funding_source
				})

				emp_doc.flags.ignore_permissions = True
				emp_doc.save()			

		else:	
			for row in employees:
				emp_doc = frappe.get_doc("Employee", row.employee)
				emp_doc.append("journals", {
					"research_reference": self.name,
					"year": self.year,
					"research_event_organized_title": self.research_event_organized_title,
					"no_of_staffs_engageds": self.no_of_staffs_engageds,
					"no_of_student_engageds": self.no_of_student_engageds,
					"no_of_external_participants": self.no_of_external_participants,
					"venues": self.venues,
					"funding_sources": self.funding_sources,
				})

				emp_doc.flags.ignore_permissions = True
				emp_doc.save()
	

	# UPDATE STUDENT
	def update_student_journals(self):
		if not self.student:
			return

		if self.sub_reporting_type == "Research Articles":	

			students = (
				(self.first_author_student or []) +
				(self.second_author_student or []) +
				(self.third_author_student or [])
			)
			for row in students:
				stu_doc = frappe.get_doc("Student", row.student)
				stu_doc.append("research_articles", {
					"research_reference": self.name,
					"fiscal_year": self.year,
					"title": self.research_articles_title,
					"publisher": self.publisher,
					"website_link": self.website_link_articles
				})

				stu_doc.flags.ignore_permissions = True
				stu_doc.save()

		elif self.sub_reporting_type == "Journals":
			for row in students:
				stu_doc = frappe.get_doc("Student", row.student)
				stu_doc.append("journals", {
					"research_reference": self.name,
					"year": self.year,
					"name_of_the_journal": self.name_of_the_journal,
					"vol_no_journal": self.vol_no_journal,
					"issue_no_journal": self.issue_no_journal,
					"website_links_journal": self.website_links_journal
				})

				stu_doc.flags.ignore_permissions = True
				stu_doc.save()

		elif self.sub_reporting_type == "Conference Seminar Paper":
			for row in students:
				stu_doc = frappe.get_doc("Student", row.student)
				stu_doc.append("conference_seminar_paper", {
					"research_reference": self.name,
					"year": self.year,
					"conference_seminar_paper_title": self.title,
					"conferenceseminar_title": self.conferenceseminar_title,
					"date": self.date,
					"nationalinternational": self.nationalinternational
				})

				stu_doc.flags.ignore_permissions = True
				stu_doc.save()

		elif self.sub_reporting_type == "Book Chapters":
			for row in students:
				stu_doc = frappe.get_doc("Student", row.student)
				stu_doc.append("conference_seminar_paper", {
					"research_reference": self.name,
					"year": self.year,
					"book_chapter_title": self.book_chapter_title,
					"book_title": self.book_title,
					"publisher": self.publishers,
					"website_link_books": self.website_link_books
				})

				stu_doc.flags.ignore_permissions = True
				stu_doc.save()	

		elif self.sub_reporting_type == "Training and workshop":
			for row in students:
				stu_doc = frappe.get_doc("Student", row.student)
				stu_doc.append("conference_seminar_paper", {
					"research_reference": self.name,
					"year": self.year,
					"trainings_organized_title": self.trainings_organized_title,
					"no_of_staffs_engaged": self.no_of_staffs_engaged,
					"no_of_student_engaged": self.no_of_student_engaged,
					"no_of_external_participants": self.no_of_external_participants,
					"venue": self.venues,
					"funding_source": self.funding_source
				})

				stu_doc.flags.ignore_permissions = True
				stu_doc.save()			

		else:	
			for row in students:
				stu_doc = frappe.get_doc("Student", row.student)
				stu_doc.append("journals", {
					"research_reference": self.name,
					"year": self.year,
					"research_event_organized_title": self.research_event_organized_title,
					"no_of_staffs_engageds": self.no_of_staffs_engageds,
					"no_of_student_engageds": self.no_of_student_engageds,
					"no_of_external_participants": self.no_of_external_participants,
					"venues": self.venues,
					"funding_sources": self.funding_sources,
				})

				stu_doc.flags.ignore_permissions = True
				stu_doc.save()	

	def remove_records(self, doctype, table_rows):
		if not table_rows:
			return

		mapping = self.get_mapping()
		if not mapping:
			return

		for row in table_rows:
			doc = frappe.get_doc(doctype, row.employee if doctype == "Employee" else row.student)

			remaining = []
			for d in doc.get(mapping["table"], []):
				if d.research_reference != self.name:
					remaining.append(d)

			doc.set(mapping["table"], remaining)

			doc.flags.ignore_permissions = True
			doc.save()

	def get_mapping(self):
		return {
			"Research Articles": {
				"table": "research_articles",
				"data": {
					"research_reference": self.name,
					"fiscal_year": self.year,
					"title": self.research_articles_title,
					"publisher": self.publisher,
					"website_link": self.website_link_articles
				}
			},
			"Journals": {
				"table": "journals",
				"data": {
					"research_reference": self.name,
					"year": self.year,
					"name_of_the_journal": self.name_of_the_journal,
					"vol_no_journal": self.vol_no_journal,
					"issue_no_journal": self.issue_no_journal,
					"website_links_journal": self.website_links_journal
				}
			},
			"Conference Seminar Paper": {
				"table": "conference_seminar_paper",
				"data": {
					"research_reference": self.name,
					"year": self.year,
					"conference_seminar_paper_title": self.title,
					"conferenceseminar_title": self.conferenceseminar_title,
					"date": self.date,
					"nationalinternational": self.nationalinternational
				}
			},
			"Book Chapters": {
				"table": "conference_seminar_paper",
				"data": {
					"research_reference": self.name,
					"year": self.year,
					"book_chapter_title": self.book_chapter_title,
					"book_title": self.book_title,
					"publisher": self.publishers,
					"website_link_books": self.website_link_books
				}
			},
			"Knowledge Transfer and Community Service": {
				"table": "conference_seminar_paper",
				"data": {
					"research_reference": self.name,
					"year": self.year,
					"trainings_organized_title": self.trainings_organized_title,
					"no_of_staffs_engaged": self.no_of_staffs_engaged,
					"no_of_student_engaged": self.no_of_student_engaged,
					"no_of_external_participants": self.no_of_external_participants,
					"venue": self.venues,
					"funding_source": self.funding_source
				}
			},
			"Research Event Organized": {
				"table": "journals",
				"data": {
					"research_reference": self.name,
					"year": self.year,
					"research_event_organized_title": self.research_event_organized_title,
					"no_of_staffs_engageds": self.no_of_staffs_engageds,
					"no_of_student_engageds": self.no_of_student_engageds,
					"no_of_external_participants": self.no_of_external_participants,
					"venues": self.venues,
					"funding_sources": self.funding_sources
				}
			}
		}.get(self.reporting_type)		
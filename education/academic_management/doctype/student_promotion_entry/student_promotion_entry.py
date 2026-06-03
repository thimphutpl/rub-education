# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


# import frappe
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
from frappe.utils import cint, flt, nowdate, add_days, getdate, fmt_money, add_to_date, DATE_FORMAT, date_diff, get_last_day
from frappe import _
from erpnext.accounts.utils import get_fiscal_year
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
# from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
import math

class StudentPromotionEntry(Document):
	def onload(self):
		if not self.docstatus==1 or self.promotions_submitted:
				return

		# check if salary increments were manually submitted
		entries = frappe.db.count("Student Promotion", {'promotion_entry': self.name, 'docstatus': 1}, ['name'])
		if cint(entries) == len(self.students):
				self.set_onload("submitted_sp", True)

	def validate(self):
		# self.set_month_dates()
		self.check_duplicates()

	def on_submit(self):
		self.create_student_promotions()


	def on_cancel(self):
		# if self.promotions_submitted == 1:
		# 	frappe.throw("Please cancel employee promotions first.")
		self.remove_employee_promotions()

	def check_duplicates(self):
		pass

	def get_std_list(self, process_type=None):
		# self.set_month_dates()

		cond = self.get_filter_condition()
		# cond += self.get_joining_relieving_condition()

		if not self.academic_term:
			frappe.throw("Please select Academic Term")

		# if self.month_name == "January":
		# 	pe_date = self.fiscal_year+"-01-01"
		# elif self.month_name == "July":
		# 	pe_date = self.fiscal_year+"-07-01"

		query = """select t1.name as student, t1.student_name, t1.company as college, t1.programme, t1.year, t1.semester
					from `tabStudent` t1 
					where t1.status = 'Active'
					{} 
					order by t1.programme, t1.name """.format(cond)


		std_list = frappe.db.sql(query, as_dict=True)
		std = []

		for s in std_list:
			is_eligible = frappe.db.sql("""
				select 1
				from `tabResult Entry`
				where student = %s
				and status = "Passed"
				and academic_term = %s
				""", (s.student, self.academic_term))
			if len(is_eligible) > 0:
				is_eligible = 1
			else:
				is_eligible = 0
			# frappe.msgprint(str(is_eligible))
			# frappe.msgprint(str(e.employee)+" "+str(is_eligible)+" grade:"+str(e.employee_grade))
			if is_eligible == 1:
				new_semester = frappe.db.get_value("Semester", s.semester, "promote_to_semester")
				new_year = frappe.db.get_value("Semester", new_semester, "year")
				programme_year = frappe.db.get_value("Programme", s.programme, "programme_year")
				if flt(new_year) > flt(programme_year):
					new_status = "Graduated"
				else:
					new_status = "Promoted"
				std.append({"student":s.student, "student_name": s.student_name, "college": s.college, "current_programme": s.programme, "new_programme": s.programme,  "current_year": s.year, "current_semester": s.semester, "new_year": new_year, "new_semester": new_semester, "status": new_status})
		return std

	def get_additional_details(self, employee, basic_pay):
		emp = frappe.get_doc("Employee", employee)
		current_increment = frappe.db.get_value("Employee Grade", emp.grade, "increment_value")
		new_grade = frappe.db.get_value("Employee Grade", emp.grade, "promotion_grade")
		#frappe.throw(str(emp))
		years_to_add = flt(frappe.db.get_value("Employee Grade", new_grade, "promotion_eligibility_years"))
		old_promo_date = emp.promotion_due_date
		new_promot_date = add_to_date(old_promo_date, years=years_to_add)
		if not new_grade:
			frappe.throw("Promote to Grade not set for Employee {} in Employee Grade".format(employee))
		new_lower_limit = frappe.db.get_value("Employee Grade", new_grade, "lower_limit")
		new_increment = frappe.db.get_value("Employee Grade", new_grade, "increment_value")
		new_upper_limit = frappe.db.get_value("Employee Grade", new_grade, "upper_limit")
		# if personal_pay > 0:
		# 	ratio = ((flt(basic_pay) + flt(personal_pay))-flt(new_lower_limit))/flt(new_increment)
		# else:

		new_basic_increment = flt(basic_pay)+flt(new_increment)
		# frappe.throw(str(new_basic_increment))
		if flt(new_basic_increment) < flt(new_lower_limit):
			new_basic_increment = flt(new_lower_limit)
		elif flt(new_basic_increment) > flt(new_upper_limit):
			new_basic_increment = flt(new_upper_limit) 
		
		'''
		ratio = ((flt(basic_pay) + flt(new_increment))-flt(new_lower_limit))/flt(new_increment)
		if flt(str(ratio).split(".")[1]) >= 0.01 and ratio > 0:				
			ratio = math.ceil(ratio)
		elif flt(str(ratio).split(".")[1]) == 0 and ratio > 0:
			ratio += 1
		else:
			ratio = 0		
		new_basic_increment = (ratio*flt(new_increment))+flt(new_lower_limit)
		if new_basic_increment > new_upper_limit:
			new_basic_increment = new_upper_limit

		
		'''
		amount = new_basic_increment
		return new_grade, new_increment, amount, new_promot_date


	@frappe.whitelist()
	def fill_student_details(self):
		self.set('students', [])
		students = self.get_std_list()
		if not students:
			frappe.throw(_("No students for the mentioned criteria"))

		for d in students:
			self.append('students', d)

		self.number_of_students = len(students)

	def get_filter_condition(self):
		self.check_mandatory()

		cond = ''
		semesters = []
		if not self.academic_session:
			frappe.throw("Academic Session cannot be blank.")

		for s in frappe.db.sql("select name from `tabSemester` where session = %s", (self.academic_session), as_dict=1):
			semesters.append(s.name)
		for f in ['college']:
			if self.get(f):
				cond += " and t1.company = '" + self.get(f).replace("'", "\'") + "'"
		if self.get("academic_term") and semesters:
			semester_list = ", ".join(f"'{s}'" for s in semesters)
			cond += f""" and t1.semester in ({semester_list})"""
		# frappe.throw(str(cond))
		return cond

	# following method created by SHIV on 2020/10/20
	
	def set_month_dates(self):
		months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		month = str(int(months.index(self.month_name))+1).rjust(2,"0")

		month_start_date = "-".join([str(self.fiscal_year), month, "01"])
		month_end_date   = get_last_day(month_start_date)

		self.start_date = month_start_date
		self.end_date = month_end_date
		# self.month_name = month

	def check_mandatory(self):
		# following line is replaced by subsequent by SHIV on 2020/10/20
		for fieldname in ['college', 'academic_term']:
			if not self.get(fieldname):
				frappe.throw(_("Please set {0}").format(self.meta.get_label(fieldname)))

	@frappe.whitelist()
	def create_student_promotions(self):
		"""
			Creates promotion for selected employees if already not created
		"""
		self.check_permission('write')
		self.created = 1
		std_list = [d['student'] for d in self.get_std_list()]

		if std_list:
			args = frappe._dict({
				"college": self.college,
				"posting_date": self.posting_date,
				"academic_term": self.academic_term,
				"promotion_entry": self.name
			})
			if len(std_list) > 500:
				frappe.enqueue(create_student_promotion_for_students, timeout=600, employees=std_list, args=args)
			else:
				create_student_promotion_for_students(std_list, args=args, publish_progress=False)
				# since this method is called via frm.call this doc needs to be updated manually
				self.reload()

	@frappe.whitelist()
	def get_student_promotion_list(self, sp_status, as_dict=False):
		"""
			Returns list of employee promotions based on selected criteria
		"""
		cond = self.get_filter_condition()
		# query = """
		# 	select t1.name from `tabEmployee Promotion` t1, `tabEmployee` t2
		# 	where t1.employee = t2.name and t2.promotion_cycle = '{}' t1.docstatus = '{}' {}
		# 	and t1.promotion_entry = '{}'
		# """.format(self.month_name, ep_status, cond, self.name)
		# frappe.throw(query)
		sp_list = frappe.db.sql("""
			select t2.name from `tabStudent Promotion` t2, `tabStudent` t1
			where t2.student = t1.name and  t2.docstatus = 0 %s
			and t2.promotion_entry = %s
		""" % (cond, '%s'), (self.name), as_dict=as_dict)
		return sp_list

	@frappe.whitelist()
	def remove_studnet_promotions(self):
		self.check_permission('write')
		sp_list = self.get_student_promotion_list(sp_status=0)
		if len(sp_list) > 500:
			frappe.enqueue(remove_student_promotions_for_students, timeout=600, promotion_entry=self, student_promotions=sp_list)
		else:
			remove_student_promotions_for_students(self, sp_list, publish_progress=False)

	@frappe.whitelist()
	def submit_student_promotions(self):
		self.check_permission('write')
		sp_list = self.get_student_promotion_list(sp_status=0)
		if len(sp_list) > 500:
			frappe.enqueue(submit_student_promotions_for_students, timeout=600, promotion_entry=self, student_promotions=sp_list)
		else:
			submit_student_promotions_for_students(self, sp_list, publish_progress=False)

	# def email_salary_slip(self, submitted_ss):
	# 	if frappe.db.get_single_value("HR Settings", "email_salary_slip_to_employee"):
	# 		for ss in submitted_ss:
	# 			ss.email_salary_slip()

def remove_student_promotions_for_employees(promotion_entry, employee_promotions, publish_progress=True):
	deleted_sp = []
	not_deleted_sp = []
	frappe.flags.via_promotion_entry = True

	count = 0
	for sp in student_promotions:
		try:
			frappe.delete_doc("Student Promotion",ep[0])
			deleted_sp.append(sp[0])
		except frappe.ValidationError:
			not_deleted_sp.append(sp[0])

		count += 1
		# if publish_progress:
		# 	frappe.publish_progress(count*100/len(employee_promotions), title = _("Removing Employee Promotions..."))
	# if deleted_ep:
	# 	frappe.msgprint(_("Employee Promotions Removed Successfully"))

	# if not deleted_ep and not not_deleted_ep:
	# 	frappe.msgprint(_("No Employee Promotions found to remove for the above selected criteria OR employee promotion already submitted"))

	# if not_deleted_ep:
	# 	frappe.msgprint(_("Could not submit some Employee Promotions. List: "+str(not_deleted_ep)))

def create_student_promotion_for_students(students, args, publish_progress=True):
	student_promotion_exists_for = get_existing_student_promotions(students, args)
	count=0
	promotion_entry = frappe.get_doc("Student Promotion Entry", args.promotion_entry)
	# frappe.msgprint(str(args.promotion_entry)+" "+str(frappe.get_doc("Promotion Entry", str(args.promotion_entry))))

	for std in promotion_entry.get("students"):
		if std.student not in student_promotion_exists_for:
			args.update({
				"doctype": "Student Promotion",
				"student": std.student
			})
			sp = frappe.get_doc(args)
			#update paramters-------------
			current_semester = frappe.db.get_value("Student", std.student, "semester")
			new_semester = frappe.db.get_value("Semester", frappe.db.get_value("Student", std.student, "semester"), "promote_to_semester")
			current_status = frappe.db.get_value("Student", std.student, "status")
			current_year = frappe.db.get_value("Student", std.student, "year")
			new_year = frappe.db.get_value("Semester", new_semester, "year")
			programme_year = frappe.db.get_value("Programme", frappe.db.get_value("Student", std.student, "programme"), "programme_year")
			#update paramters end---------
			rows = [
					{
						'property': 'Semester',
						'current': frappe.db.get_value("Student", std.student, "semester"),
						'new': std.new_semester if programme_year >= std.new_year else std.current_semester,
						'fieldname': 'semester'
					},
					{
						'property': 'Status',
						'current': current_status,
						'new': "Graduated" if flt(std.new_year) > flt(programme_year) else current_status,
						'fieldname': 'status'
					},
					{
						'property': 'Year',
						'current': std.current_year,
						'new': std.new_year if programme_year >= std.new_year else std.cuurent_year,
						'fieldname': 'grade'
					}
				]
			for row in rows:
				sp.append("promotion_details", row)

			sp.current_programme = std.current_programme
			sp.new_programme = std.new_programme
			sp.semester = std.current_semester
			sp.new_semester = std.new_semester
			sp.year = std.current_year
			sp.new_year = std.new_year
			sp.status = std.status
			#----------------------------------End--------------------------------------------------------#

			sp.promotion_date = promotion_entry.posting_date
			sp.insert()
			count+=1

			ied = frappe.get_doc("Student Promotion Detail", std.name)
			ied.db_set("student_promotion", sp.name)
			if publish_progress:
				description = " Processing {}: ".format(ss[0]) + "["+str(count)+"/"+str(len(students))+"]"
				frappe.publish_progress(count*100/len(set(students) - set(student_promotion_exists_for)),
					title = _("Creating Student Promotions..."), description=description)

	promotion_entry.db_set("promotions_created", 1)
	promotion_entry.notify_update()

def get_existing_student_promotions(students, args):
	return frappe.db.sql_list("""
		select distinct student from `tabStudent Promotion`
		where docstatus!= 2 and college = %s
			and academic_term = %s
			and student in (%s)
	""" % ('%s', '%s', ', '.join(['%s']*len(students))),
		[args.company, args.academic_term] + students)

def submit_student_promotions_for_students(promotion_entry, student_promotions, publish_progress=True):
	submitted_sp = []
	not_submitted_sp = []
	frappe.flags.via_promotion_entry = True

	count = 0
	for sp in student_promotions:
		sp_obj = frappe.get_doc("Student Promotion",sp[0])
		# if not sp_obj.promotion_details or sp_obj.promotion_details == None or sp_obj.promotion_details == "":
		# 	not_submitted_sp.append(sp[0])
		# else:
		try:
			sp_obj.submit()
			submitted_sp.append(sp_obj)
		except frappe.ValidationError:
			not_submitted_sp.append(sp[0])

		count += 1
		if publish_progress:
			frappe.publish_progress(count*100/len(student_promotions), title = _("Submitting Student Promotions..."))
	if submitted_sp:
		frappe.msgprint(_("Student Promotions submitted for Academic Term {0}")
			.format(sp_obj.academic_term))

		promotion_entry.db_set("promotions_submitted", 1)
		promotion_entry.notify_update()

	if not submitted_sp and not not_submitted_sp:
		frappe.msgprint(_("No Student Promotions found to submit for the above selected criteria OR Student Promotion already submitted"))

	if not_submitted_sp:
		frappe.msgprint(_("Could not submit some Student Promotions. List of not submitted promotions: "+str(not_submitted_sp)))

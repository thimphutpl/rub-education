# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.custom_utils import prepare_gl
from frappe.utils import flt
class HallPayment(Document):

	def on_submit(self):
		self.update_general_ledger()
		self.post_journal_entry()
		self.update_hall_booking_payment_status() 
	def update_general_ledger(self):
		gl_entries = []
		default_bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")
		default_income_hall = frappe.db.get_value("Company", self.company,"default_income_hall")
		if not default_bank_account or not default_income_hall:
			frappe.throw("Please set Default Bank Account and Default Income Account for Hall in Company settings.")
			return
		gl_entries.append(
			prepare_gl(self, {
				"account":default_income_hall,
				"credit": flt(self.total_amount),
				"credit_in_account_currency": flt(self.total_amount),
				"cost_center": self.cost_center,
			
			})
		)
		gl_entries.append(
			prepare_gl(self, {
				"account": default_bank_account,
				"debit": flt(self.total_amount),
				"debit_in_account_currency": flt(self.total_amount),
				"cost_center": self.cost_center,
			
			})
		)
		if gl_entries:
			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), merge_entries=False)	

	def post_journal_entry(self):
		default_bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")
		default_income_hall = frappe.db.get_value("Company", self.company,"default_income_hall")
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.mode_of_payment = self.mode_of_payment
		je.title = self.name
		je.voucher_type = 'Journal Entry'
		je.naming_series = 'Journal Voucher'
		je.remark = 'Payment against : ' + self.name
		je.cheque_no = self.cheque_no
		je.cheque_date = self.cheque_date
		je.posting_date = self.posting_date
		je.company = self.company
		je.branch = self.branch
		if self.total_amount > 0:
			je.append("accounts", {
				"account": default_income_hall,
				"reference_type": "Hall Payment",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.total_amount),
				"credit": flt(self.total_amount),
			
			})
			je.append("accounts", {
				"account": default_bank_account,
				"reference_type": "Hall Payment",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.total_amount),
				"debit": flt(self.total_amount),
			})
			
		je.save()
		frappe.db.commit()	

	# def update_hall_booking_payment_status(self):
	# 	if self.hall_booking:
	# 		hall_booking = frappe.get_doc("Hall Booking", self.hall_booking)
	# 		hall_payemnt = frappe.ge_doc("Hall Payment",self.name)
	# 		hall_payemnt.workflow_state="Payment Completed"
	# 		hall_booking.workflow_state= "Payment Completed"
	# 		hall_booking.flags.ignore_permissions = True
	# 		hall_booking.save()
	# 		frappe.db.commit()
	# 		frappe.msgprint(
	# 			f"Hall Booking {self.hall_booking} payment status updated to 'Completed'",
	# 			alert=True
	# 		)	
	def update_hall_booking_payment_status(self):
		if not self.hall_booking:
			return
		
		if not frappe.db.exists("Hall Booking", self.hall_booking):
			return
		
		frappe.db.set_value("Hall Booking", self.hall_booking, "workflow_state", "Payment Completed")
		frappe.db.set_value("Hall Payment", self.name, "workflow_state", "Payment Completed")
		frappe.db.commit()
		
		frappe.msgprint(f"✅ Booking {self.hall_booking} payment completed", alert=True)	

# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ConferencePayment(Document):
	def on_submit(self):
		self.post_journal_entry()
		self.update_hall_booking_payment_status()


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
					"reference_type": "Conference Payment",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"credit_in_account_currency": flt(self.total_amount),
					"credit": flt(self.total_amount),
				
				})
				je.append("accounts", {
					"account": default_bank_account,
					"reference_type": "Conference Payment",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.total_amount),
					"debit": flt(self.total_amount),
				})
				
			je.save()
			frappe.db.commit()	
	def update_hall_booking_payment_status(self):
		if not self.full_paper:
			return
		
		if not frappe.db.exists("Full Paper", self.full_paper):
			return
		
		frappe.db.set_value("Full Paper", self.full_paper, "workflow_state", "Payment Completed")
		frappe.db.set_value("Conference Payment", self.name, "workflow_state", "Payment Completed")
		frappe.db.commit()
		
		frappe.msgprint(f"✅ Booking {self.full_paper} payment completed", alert=True)	
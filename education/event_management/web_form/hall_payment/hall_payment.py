import frappe

def get_context(context):
	context.allowed_file_types = ["png", "jpg", "jpeg"]

@frappe.whitelist(allow_guest=True)
def get_hall_payment_data(name):
	try:
		if not frappe.db.exists("Hall Booking", name):
			return {"error": f"Hall Booking {name} not found"}

		doc = frappe.get_doc("Hall Booking", name)
        
		return {
			"name":doc.name,
			"venue": doc.venue,
			"company": doc.company,
			"branch": doc.branch,
			"cost_center": doc.cost_center,
			"email": doc.email,
			"name1": doc.name1,
			"dzongkhag": doc.dzongkhag,
			"country": doc.country,
			"organization": doc.organization,
			"designation": doc.designation,
			"amount": doc.amount,
			"total_days": doc.total_days,
			"total_amount": doc.total_amount,
			"account_number": doc.account_number,
			"qr_code": doc.qr_code
		}
	  

	except Exception as e:
		frappe.log_error(str(e), "Hall Payment Web Form")
		return {"error": str(e)}
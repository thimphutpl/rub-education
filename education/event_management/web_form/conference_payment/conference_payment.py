import frappe

def get_context(context):
	# do your magic here
	pass


@frappe.whitelist(allow_guest=True)
def get_conference_payment_data(name):
	try:
		if not frappe.db.exists("Full Paper", name):
			return {"error": f"Full Paper {name} not found"}

		doc = frappe.get_doc("Full Paper", name)
	
		
		result = {
			"full_paper":doc.name,
			
			
		}
		frappe.errprint(result)
		return result
	  
	
	except Exception as e:
		frappe.log_error(str(e), "Conference Payment Web Form")
		return {"error": str(e)}
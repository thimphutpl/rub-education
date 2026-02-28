import frappe

def get_context(context):
	# do your magic here
	pass

@frappe.whitelist(allow_guest=True)
def check_duplicate_registration(full_paper=None, email=None):

	if not full_paper or not email:
		return None

	exists=frappe.db.exists(
		"Audience Registration",
		{
			"full_paper": full_paper,
			"email_address": email,
			"docstatus": ["!=", 2] 
		}
	)
	if exists:
		return {
			"status": "duplicate",
			"message": f"{email} is already registered for this event."
		}

	return {"status": "ok"}
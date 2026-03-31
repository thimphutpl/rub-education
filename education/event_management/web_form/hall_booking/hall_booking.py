import frappe

def get_context(context):
	# do your magic here
	pass
def validate(self):
    self.check_duplicate_registration()

@frappe.whitelist(allow_guest=True)
def check_duplicate_venue(email,venue):
	if not email:
		return {"exists": False}

	exists = frappe.db.exists(
		"Hall Booking",
		{"email": email, "venue": venue}
	)

	return {
		"exists": bool(exists)
	}

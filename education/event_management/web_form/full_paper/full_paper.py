import frappe

def get_context(context):
	# do your magic here
	pass
def validate(self):
    self.check_duplicate_registration()

@frappe.whitelist(allow_guest=True)
def check_duplicate_registration(email,theme):
	if not email:
		return {"exists": False}

	exists = frappe.db.exists(
		"Full Paper",
		{"email": email, "theme": theme}
	)

	return {
		"exists": bool(exists)
	}

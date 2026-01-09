import frappe

def get_context(context):
	# do your magic here
	pass
def validate(self):
    self.check_duplicate_registration()
# @frappe.whitelist(allow_guest=True)
# def check_duplicate_registration(name=None,email=None):
#     existing = frappe.db.exists(
#         "Full Paper", 
#         {
#             "email": email,
#         }
        
#     )    
#     if existing:
#         frappe.throw(_("You are already registered for this Full Paper."))
@frappe.whitelist(allow_guest=True)
def check_duplicate_registration(email):
	if not email:
		return {"exists": False}

	exists = frappe.db.exists(
		"Full Paper",
		{"email": email}
	)

	return {
		"exists": bool(exists)
	}

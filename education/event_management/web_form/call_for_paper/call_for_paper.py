# conference_registration.py
import frappe
from frappe import _

# --------------------------------------
# Required by Web Form
# --------------------------------------
def get_context(context):
	"""
	This is required by the Web Form.
	You can add extra context here if needed.
	"""
	pass


def validate(self):
	self.check_duplicate_registration()

@frappe.whitelist(allow_guest=True)
def check_duplicate_registration(email, conference, name=None):
    if not email:
        return {"exists": False}

    existing = frappe.db.exists(
        "Call For Paper",
        {
            "email": email,
            "conference": conference
        }
    )

    return {"exists": bool(existing)}

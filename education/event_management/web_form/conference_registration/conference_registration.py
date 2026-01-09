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

def check_duplicate_registration(self):
    # Check if this email is already registered for this conference
    existing = frappe.db.exists(
        "Conference Registration", 
        {
            "email": self.email,
            "conference": self.conference,
            "name": ["!=", self.name]  # Exclude current document if updating
        }
    )
    
    if existing:
        frappe.throw(_("You are already registered for this conference."))
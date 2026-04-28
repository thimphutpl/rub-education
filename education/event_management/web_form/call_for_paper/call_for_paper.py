# conference_registration.py
import frappe
import requests
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



@frappe.whitelist(allow_guest=True)
def verify_captcha(response):
    """Verify Google reCAPTCHA v2"""
    
    if not response:
        return {"verified": False}
    
    secret_key = "6Lery8osAAAAAI7iEn06SKmWSVoldHA-KraVV5Xl"
    
    try:
        # Call Google's verification API
        verification = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': secret_key,
                'response': response
            },
            timeout=10
        )
        
        result = verification.json()
        
        if result.get('success'):
            return {"verified": True}
        else:
            frappe.log_error(f"reCAPTCHA failed: {result.get('error-codes', [])}", "Captcha")
            return {"verified": False}
            
    except Exception as e:
        frappe.log_error(f"reCAPTCHA exception: {str(e)}", "Captcha")
        return {"verified": False}
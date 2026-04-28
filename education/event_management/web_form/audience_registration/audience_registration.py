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
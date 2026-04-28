import frappe
import requests

def get_context(context):
	# do your magic here
	pass
def validate(self):
	self.check_duplicate_registration()

# @frappe.whitelist(allow_guest=True)
# def check_duplicate_venue(email,venue):
# 	if not email:
# 		return {"exists": False}

# 	exists = frappe.db.exists(
# 		"Hall Booking",
# 		{"email": email, "venue": venue}
# 	)

# 	return {
# 		"exists": bool(exists)
# 	}

@frappe.whitelist(allow_guest=True)
def check_duplicate_venue(email,venue, from_date, to_date):
	if not (venue and from_date and to_date):
		return {"conflict": False}

	bookings = frappe.get_all(
		"Hall Booking",
		filters={
			"venue": venue,
			"email":email,
			"docstatus": ["!=", 2]  # ignore cancelled
		},
		fields=["from_date", "to_date"]
	)

	for b in bookings:
		# Convert to date (important!)
		existing_from = frappe.utils.getdate(b.from_date)
		existing_to = frappe.utils.getdate(b.to_date)
		new_from = frappe.utils.getdate(from_date)
		new_to = frappe.utils.getdate(to_date)

		# Overlap condition
		if not (new_to < existing_from or new_from > existing_to):
			return {"conflict": True,
					"booked_from": str(existing_from),
				"booked_to": str(existing_to)}

	return {"conflict": False}


@frappe.whitelist(allow_guest=True)
def get_hall_data(name):
	try:
		if not frappe.db.exists("Room", name):
			return {"error": f"Hall  {name} not found"}

		doc = frappe.get_doc("Room", name)
	

		data= {     
			"venue": doc.name,
			"company": doc.company,
			"branch": doc.branch,
			"cost_center": doc.cost_center,
			"amount":doc.amount
		}
		return data
	

	except Exception as e:
		frappe.log_error(str(e), "Room")
		return {"error": str(e)}
	

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
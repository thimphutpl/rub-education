import frappe
import requests
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
@frappe.whitelist(allow_guest=True)
def get_data(name):
    data = frappe.db.sql("""
        SELECT 
            cp.*, 
            an.name1,
            an.brief_bio_of_the_author
        FROM `tabCall For Paper` cp
        LEFT JOIN `tabAuthor Name` an 
            ON cp.name = an.parent
        WHERE cp.name = %s
    """, (name), as_dict=True)

    if not data:
        return {}

    # Separate parent + child table
    parent = data[0]
    authors = []

    for row in data:
        if row.get("name1"):
            authors.append({
                "name1": row.get("name1"),
                "brief_bio_of_the_author": row.get("brief_bio_of_the_author")
            })

    parent["author_name"] = authors

    return parent
     

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
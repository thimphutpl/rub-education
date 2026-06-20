
import frappe
import requests
from datetime import datetime
from frappe.utils import getdate, get_time


def get_context(context):
	pass


def make_datetime(date_value, time_value):
	return datetime.combine(
		getdate(date_value),
		get_time(time_value)
	)


@frappe.whitelist(allow_guest=True)
def check_duplicate_venue(email, venue, from_date, from_time, to_date, to_time):
	if not (venue and from_date and from_time and to_date and to_time):
		return {
			"conflict": False,
			"message": "Required booking details are missing"
		}

	try:
		new_from = make_datetime(from_date, from_time)
		new_to = make_datetime(to_date, to_time)

		if new_from >= new_to:
			return {
				"conflict": True,
				"message": "To Date/Time must be greater than From Date/Time"
			}

		bookings = frappe.get_all(
			"Hall Booking",
			filters={
				"venue": venue,
				"docstatus": ["!=", 2]
			},
			fields=[
				"name",
				"email",
				"from_date",
				"from_time",
				"to_date",
				"to_time"
			]
		)

		for b in bookings:
			if not (b.from_date and b.from_time and b.to_date and b.to_time):
				continue

			existing_from = make_datetime(b.from_date, b.from_time)
			existing_to = make_datetime(b.to_date, b.to_time)

			if new_from < existing_to and new_to > existing_from:
				return {
					"conflict": True,
					"booking_id": b.name,
					"booked_email": b.email,
					"booked_from": existing_from.strftime("%d-%m-%Y %I:%M %p"),
					"booked_to": existing_to.strftime("%d-%m-%Y %I:%M %p"),
					"message": "This venue is already booked during this time"
				}

		return {
			"conflict": False,
			"message": "No duplicate booking found"
		}

	except Exception as e:
		frappe.log_error(
			frappe.get_traceback(),
			"Hall Booking Duplicate Check Error"
		)
		return {
			"conflict": True,
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def get_hall_data(name):
	try:
		if not frappe.db.exists("Room", name):
			return {"error": f"Hall {name} not found"}

		doc = frappe.get_doc("Room", name)

		data = {
			"venue": doc.name,
			"company": doc.company,
			"branch": doc.branch,
			"cost_center": doc.cost_center,
			"amount": doc.amount,
			"account_number": doc.account_number,
			"qr_code": doc.qr_code
		}

		return data

	except Exception as e:
		frappe.log_error(str(e), "Room")
		return {"error": str(e)}


@frappe.whitelist(allow_guest=True)
def verify_captcha(response):
	if not response:
		return {"verified": False}

	secret_key = "6Lery8osAAAAAI7iEn06SKmWSVoldHA-KraVV5Xl"

	try:
		verification = requests.post(
			"https://www.google.com/recaptcha/api/siteverify",
			data={
				"secret": secret_key,
				"response": response
			},
			timeout=10
		)

		result = verification.json()

		if result.get("success"):
			return {"verified": True}

		frappe.log_error(
			f"reCAPTCHA failed: {result.get('error-codes', [])}",
			"Captcha"
		)
		return {"verified": False}

	except Exception as e:
		frappe.log_error(f"reCAPTCHA exception: {str(e)}", "Captcha")
		return {"verified": False}


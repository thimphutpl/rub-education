from frappe import _

def get_data():
    return {
        "non_standard_fieldnames": {
            "Hall Booking": "venue",
        },
        "transactions": [
            {
                "label": _("Room"),
                "items": ["Room"]
            }
        ],
    }
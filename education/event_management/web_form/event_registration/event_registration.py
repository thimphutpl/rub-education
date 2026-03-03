import frappe
from frappe import _

def get_context(context):
	# do your magic here
	pass
@frappe.whitelist(allow_guest=True)
def get_upcoming_events():
    return frappe.get_all(
        "Events",
        filters={"docstatus": 1},
        fields=["name", "event_title", "start_date", "end_date", "room", "college"],
        order_by="start_date asc"
    )
@frappe.whitelist(allow_guest=True)
def get_user_full_name(email):
    user = frappe.get_all(
        "User",
        filters={"email": email},
        fields=["full_name"],
        limit_page_length=1
    )
    if user:
        return user[0].full_name
    return ""

@frappe.whitelist(allow_guest=True)
def check_already_registered(event, faculty_email):
    """
    Check if email already registered for the event
    """

    if not event or not faculty_email:
        return {"status": "error", "message": "Missing event or email"}

    exists = frappe.db.exists(
        "Event Registration",
        {
            "event": event,
            "faculty_email": faculty_email,
            "docstatus": ["!=", 2] 
        }
    )

    if exists:
        return {
            "status": "duplicate",
            "message": f"{faculty_email} is already registered for this event."
        }

    return {"status": "ok"}

def after_insert(doc, method=None):
    """
    Auto-submit Event Registration after insert and check duplicate email
    """
    if not doc.event:
        frappe.throw(_("Please select an Event before submitting."))
    event_doc = frappe.get_doc("Events", doc.event)
    event_doc.append("faculty_register", {
        "faculty_email": doc.faculty_email,
        "faculty_name": doc.faculty_name
    })

    # Save Event doc
    event_doc.save(ignore_permissions=True)
    # frappe.db.commit()

    # Auto-submit the Event Registration if still draft
    # if doc.docstatus == 0:
    #     doc.submit()

    frappe.msgprint(_("✅ {0} has successfully registered to the event.").format(doc.faculty_email))
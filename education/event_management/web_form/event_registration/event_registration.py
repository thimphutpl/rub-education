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
def after_insert(doc, method=None):
    """
    Auto-submit Event Registration after insert and check duplicate email
    """
    if not doc.event:
        frappe.throw(_("Please select an Event before submitting."))

    # Fetch the Event document
    event_doc = frappe.get_doc("Events", doc.event)

    # Check if the email is already registered
    already_registered = any(
        row.faculty_email == doc.faculty_email
        for row in getattr(event_doc, "faculty_register", [])
    )

    if already_registered:
        frappe.throw(_("⚠️ {0} is already registered for this event.").format(doc.faculty_email))

    # Add the user to the Event's child table
    event_doc.append("faculty_register", {
        "faculty_email": doc.faculty_email,
        "faculty_name": doc.faculty_name
    })

    # Save Event doc
    event_doc.save(ignore_permissions=True)
    frappe.db.commit()

    # Auto-submit the Event Registration if still draft
    if doc.docstatus == 0:
        doc.submit()

    frappe.msgprint(_("✅ {0} has successfully registered to the event.").format(doc.faculty_name))
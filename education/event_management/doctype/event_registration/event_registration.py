import frappe
from frappe.model.document import Document

class EventRegistration(Document):
    def on_submit(self):
        # Ensure the user selected an Event
        if not self.event:
            frappe.throw("Please select an Event before submitting.")

        # Fetch the linked Event (use correct doctype name)
        event_doc = frappe.get_doc("Events", self.event)

        # Check if this email is already registered
        already_registered = any(row.faculty_email == self.faculty_email for row in event_doc.faculty_register)

        if already_registered:
            frappe.throw(f"⚠️ {self.faculty_email} is already registered for this event.")
            return

        # Append the user to the faculty_register child table
        event_doc.append("faculty_register", {
            "faculty_email": self.faculty_email,
            "faculty_name": self.faculty_name
        })

        # Save the updated Event
        event_doc.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.msgprint(f"✅ {self.faculty_name} has successfully registered to the event. Thank you!")


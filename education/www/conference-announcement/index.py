# apps/education/education/education/www/conference-announcement/index.py
import frappe
from frappe import _

no_cache = 1

@frappe.whitelist(allow_guest=True)
def get_conference_info():
    from frappe.utils import now_datetime
    now = now_datetime()

    conferences = frappe.db.sql(
        """
        SELECT 
            name,theme,title, start_date, end_date, location,image,deadline
        FROM `tabConference Announcement`
        WHERE deadline > %s
    
        ORDER BY start_date DESC
        """,
        (now),
        as_dict=True
    )
    return {"conferences": conferences}

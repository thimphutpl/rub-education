import frappe
from frappe.utils.data import today

no_cache = 1
@frappe.whitelist(allow_guest=True)
def get_college():
    college = frappe.db.sql("""
        SELECT 
            name
        FROM `tabCompany`
        ORDER BY name ASC
    """, as_dict=True)
    
    return {"college": college}
@frappe.whitelist(allow_guest=True)
def get_events_info(college=None):
    """
    Returns events info, optionally filtered by college.
    Only includes events starting today or in the future (start_date >= today)
    and docstatus = 1 (submitted).
    """
    filters = ["docstatus = 1", "start_date >= %s"]  # list of conditions
    values = [today()]  # first parameter for start_date >= today

    if college:
        filters.append("college = %s")
        values.append(college)

    where_clause = "WHERE " + " AND ".join(filters)

    events_info = frappe.db.sql(
        f"""
        SELECT
            name,
            event_title,
            start_date,
            end_date,
            room,
            college,
            event_type,
            event_banner,
            capacity
        FROM `tabEvents`
        {where_clause}
        ORDER BY start_date ASC
        """,
        tuple(values),
        as_dict=True
    )

    return {"events_info": events_info}
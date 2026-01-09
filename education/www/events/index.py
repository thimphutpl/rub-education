import frappe

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
    Returns events info, optionally filtered by college
    """
    filters = "WHERE docstatus = 1"
    values = []

    if college:
        filters += " AND college = %s"
        values.append(college)

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
        {filters}
        ORDER BY start_date DESC
        """,
        tuple(values),
        as_dict=True
    )

    return {"events_info": events_info}

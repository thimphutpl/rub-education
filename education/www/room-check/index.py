# import frappe
# from frappe.utils.data import today

# no_cache = 1
# @frappe.whitelist(allow_guest=True)
# def get_college():
#     college = frappe.db.sql("""
#         SELECT 
#             name
#         FROM `tabCompany`
#         ORDER BY name ASC
#     """, as_dict=True)
#     return {"college": college}

# @frappe.whitelist(allow_guest=True)
# def get_room_info(college=None):

#     filters = []  # list of conditions
#     values = []  # first parameter for start_date >= today

#     if college:
#         filters.append("college = %s")
#         values.append(college)

#     where_clause = "WHERE " + " AND ".join(filters)

#     room_info = frappe.db.sql(
#         f"""
#         SELECT
#             name,
#             room_name,
#             company,
#             seating_capacity,
#             cost_center
#         FROM `tabRoom`
#         {where_clause}
#         """,
#         tuple(values),
#         as_dict=True
#     )
#     return {"room_info": room_info}

import frappe

no_cache = 1

@frappe.whitelist(allow_guest=True)
def get_college():
    colleges = frappe.db.sql("""
        SELECT name
        FROM `tabCompany`
        ORDER BY name ASC
    """, as_dict=True)
    return {"college": colleges}


# @frappe.whitelist(allow_guest=True)
# def get_room_info(college=None):
#     filters = []
#     values = []

#     # Correct field name is 'company', not 'college'
#     if college:
#         filters.append("company = %s")
#         values.append(college)

#     # Only add WHERE if filters exist
#     # where_clause = ""
#     if filters:
#         where_clause = "WHERE " + " AND ".join(filters)

#     rooms = frappe.db.sql(
#         f"""
#         SELECT
#             r.name,
#             r.room_name,
#             r.room_number,
#             r.seating_capacity,
#             r.company,
#             r.cost_center,
#             CASE 
#                 WHEN hb.venue IS NOT NULL THEN 'Not Available'
#                 ELSE 'Available'
#             END AS status
#         FROM `tabRoom` r
#         LEFT JOIN `tabHall Booking` hb
#             ON r.name = hb.venue
            
#         {where_clause}
#         ORDER BY room_name ASC
#         """,
#         tuple(values),
#         as_dict=True
#     )

#     return {"room_info": rooms}

@frappe.whitelist(allow_guest=True)
def get_room_info(college=None):
    filters = []
    values = []

    if college:
        filters.append("r.company = %s")
        values.append(college)

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    rooms = frappe.db.sql(
        f"""
        SELECT
            r.name,
            r.room_name,
            r.room_number,
            r.seating_capacity,
            r.company,
            r.branch,
            r.cost_center,
            r.amount,
            r.company,
            r.account_number,
            r.qr_code,
            hb.from_date,
            hb.to_date,
            hb.from_time,
            hb.to_time
        FROM `tabRoom` r
        LEFT JOIN `tabHall Booking` hb
            ON r.name = hb.venue
 
        {where_clause}
        ORDER BY r.room_name ASC
        """,
        tuple(values),
        as_dict=True
    )

    return {"room_info": rooms}

    
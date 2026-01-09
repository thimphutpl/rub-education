# # # # import frappe
# # # # from frappe import _

# # # # @frappe.whitelist(allow_guest=True)
# # # # def get_conference_info(email):
# # # #     if not email:
# # # #         return {"conferences_info": []}
    
# # # #     conferences_info = frappe.db.sql(
# # # #         """
# # # #         SELECT 
# # # #             name,
# # # #             conference
# # # #         FROM `tabConference Registration` 
# # # #         WHERE email = %s
# # # #         ORDER BY creation DESC
# # # #         """,
# # # #         (email,),
# # # #         as_dict=True
# # # #     )
    
# # # #     return {"conferences_info": conferences_info}

# # # # import frappe
# # # # from frappe import _

# # # # @frappe.whitelist(allow_guest=True)
# # # # def get_conference_info(email):
# # # #     if not email:
# # # #         return {"conferences": []}
    
# # # #     # Get only registration data (no conference details)
# # # #     conferences = frappe.db.sql(
# # # #         """
# # # #         SELECT 
# # # #             name as registration_id,
# # # #             conference as conference_id
            
# # # #         FROM `tabConference Registration` 
# # # #         WHERE email = %s
# # # #         ORDER BY creation DESC
# # # #         """,
# # # #         (email,),
# # # #         as_dict=True
# # # #     )
    
# # # #     return {"conferences": conferences}

# # # import frappe
# # # from frappe import _

# # # @frappe.whitelist(allow_guest=True)
# # # def get_conference(email):
# # #     if not email:
# # #         return {"conferences_info": []}
    
# # #     # Get only registration data (no conference details)
# # #     conferences_info = frappe.db.sql(
# # #         """
# # #         SELECT 
# # #             name,
# # #             name1,
# # #             conference,
# # #             workflow_state
            
# # #         FROM `tabConference Registration` 
# # #         WHERE email = %s
# # #         AND workflow_state IN ('Waiting for Review', 'Approved', 'Rejected')
# # #         ORDER BY creation DESC
# # #         """,
# # #         (email,),
# # #         as_dict=True
# # #     )
# # #     full_paper_submissions = frappe.db.sql(
# # #         """
# # #         SELECT DISTINCT conference
# # #         FROM `tabFull Paper`
# # #         """,
# # #         as_dict=True
# # #     )

# # #     applied_conferences = [f['conference'] for f in full_paper_submissions]

# # #     # 3. Filter out conferences that already have Full Paper submitted
# # #      eligible_conferences = [
# # #         c for c in conferences_info if c['conference'] not in applied_conferences
# # #     ]
# # #     return {"conferences_info": eligible_conferences}

# # import frappe

# # @frappe.whitelist(allow_guest=True)
# # def get_conference(email):
# #     if not email:
# #         return {"conferences_info": []}

# #     # 1. Get all conferences that already have Full Paper applied
# #     applied_conferences = frappe.get_all(
# #         "Full Paper",
# #         fields=["conference","theme","prefix"]
# #     )
# #     applied_list = [f['conference'] for f in applied_conferences]

# #     # 2. Get registrations for this email that are NOT in applied_list
# #     conferences_info = frappe.get_all(
# #         "Call For Paper",
# #         filters={
# #             "email": email,
# #             "workflow_state": ["in", ["Waiting for Review", "Approved", "Rejected"]],
# #             "name": ["not in", applied_list]
# #         },
# #         fields=[
# #             "name","theme", "conference", "prefix", "first_name", "middle_name", "last_name",
# #             "nationality", "passport__cid_number", "country_of_your_current_location",
# #             "organisation", "current_position", "email", "mobile_number",
# #             "name1", "contact_number", "relationship", "title", "affiliation",
# #             "brief_bio_of_the_authors", "abstract", "workflow_state"
# #         ],
# #         order_by="creation desc"
# #     )

# #     return {"conferences_info": conferences_info}
# import frappe

# @frappe.whitelist(allow_guest=True)
# def get_conference(email):
#     if not email:
#         return {"conferences_info": []}

#     # Conferences already applied for Full Paper
#     applied_conferences = frappe.get_all(
#         "Full Paper",
#         fields=["conference"]
#     )
#     applied_list = [d.conference for d in applied_conferences]

#     call_for_papers = frappe.get_all(
#         "Call For Paper",
#         filters={
#             "email": email,
#             "workflow_state": ["in", ["Waiting for Review", "Approved", "Rejected"]],
#             "name": ["not in", applied_list]
#         },
#         fields=[
#             "name", "theme", "conference", "prefix",
#             "first_name", "middle_name", "last_name",
#             "nationality", "passport__cid_number",
#             "country_of_your_current_location",
#             "organisation", "current_position",
#             "email", "mobile_number",
#             "name1", "contact_number", "relationship",
#             "title", "affiliation",
#             "brief_bio_of_the_authors",
#             "abstract", "workflow_state"
#         ],
#         order_by="creation desc"
#     )

#     conferences_info = []

#     for paper in call_for_papers:
#         doc = frappe.get_doc("Call For Paper", paper.name)

#         # ✅ Fetch child table rows
#         authors = []
#         for row in doc.author_name:
#             authors.append({
#                 "name1": row.name1
#             })

#         paper_dict = paper.copy()
#         paper_dict["author_name"] = authors
#         conferences_info.append(paper_dict)


#     return {"conferences_info": conferences_info}
import frappe

@frappe.whitelist(allow_guest=True)
def get_conference(email):
    if not email:
        return {"conferences_info": []}

    applied_conferences = frappe.get_all(
        "Full Paper",
        fields=["conference"]
    )
    applied_list = [d.conference for d in applied_conferences]

    call_for_papers = frappe.get_all(
        "Call For Paper",
        filters={
            "email": email,
            "workflow_state": ["in", ["Waiting for Review", "Approved", "Rejected"]],
            "name": ["not in", applied_list]
        },
        fields=[
            "name", "theme", "conference", "prefix",
            "first_name", "middle_name", "last_name",
            "nationality", "passport__cid_number",
            "country_of_your_current_location",
            "organisation", "current_position",
            "email", "mobile_number",
            "name1", "contact_number", "relationship",
            "title", "affiliation",
            "abstract", "workflow_state",
			
        ],
        order_by="creation desc"
    )

    conferences_info = []

    for paper in call_for_papers:
        doc = frappe.get_doc("Call For Paper", paper.name)

        # ✅ Author Name child table
        author_names = [
            {"name1": row.name1}
            for row in getattr(doc, "author_name", [])
        ]

        # ✅ Author Details child table
        author_details = [
            {"brief_bio_of_the_authors": row.brief_bio_of_the_authors}
            for row in getattr(doc, "brief_bio", [])
        ]

        paper_dict = paper.copy()
        paper_dict["author_name"] = author_names
        paper_dict["author_details"] = author_details

        conferences_info.append(paper_dict)

    return {"conferences_info": conferences_info}

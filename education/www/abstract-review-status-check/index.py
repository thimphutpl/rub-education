import frappe

@frappe.whitelist(allow_guest=True)
def get_conference(email,cid):
    if not email  or not cid:
        return{"conferences_info":[]}


    applied_conferences = frappe.get_all(
        "Full Paper",
        fields=["conference"]
    )
    applied_list = [d.conference for d in applied_conferences]

    call_for_papers = frappe.get_all(
        "Call For Paper",
        filters={
            "email": email,
            "passport__cid_number":cid,
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

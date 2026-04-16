import frappe

@frappe.whitelist(allow_guest=True)
def get_full_paper(email,cid):
    if not email or not cid:
        return {"full_paper_info": []}

    full_paper_info = frappe.get_all(
        "Full Paper",
        filters={
            "email": email,
            "passport__cid_number":cid,
            "workflow_state": ["in", ["Waiting for Review", "Approved", "Rejected"]],
        },
        fields=["name","conference", "workflow_state"],
        order_by="creation desc",
        ignore_permissions=True
    )

    return {"full_paper_info": full_paper_info}

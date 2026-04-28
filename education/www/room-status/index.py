import frappe

@frappe.whitelist(allow_guest=True)
def get_room_info(email):
    if not email:
        return {"room_info": []}

    room_info = frappe.get_all(
        "Hall Booking",
        filters={
            "email": email,
           "workflow_state": ["in", ["Approved", "Waiting for Approval"]],
        },
        fields=["name",
        "venue","company","branch","cost_center","workflow_state","amount","total_days","total_amount","account_number","qr_code","country","dzongkhag","email","name1","designation","organization",],
        order_by="creation desc",
        ignore_permissions=True
    )
    return {"room_info": room_info}

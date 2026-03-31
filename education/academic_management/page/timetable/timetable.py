import frappe

@frappe.whitelist()
def get_timetable(college, programme, academic_term):
    timetable = frappe.get_all(
        "Timetable Schedule Entry",
        filters={"college": college, "programme": programme, "academic_term": academic_term},
        fields=["day","from_time","to_time","module_code","tutor","class_type","tutor_name","room_name"],
        order_by="from_time asc"
    )

    constraint = frappe.get_doc("Timetable Constraints", {"academic_term":"2025 Spring Semester"})
    blocked = []
    if timetable:
        for p in constraint.periods:
            period_name = p.period_name or "Non-Academic"
            for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
                if getattr(p, d):
                    blocked.append({
                        "day": d.capitalize(),
                        "from_time": p.from_time,
                        "to_time": p.to_time,
                        "period_name": period_name
                    })

    return {
        "timetable": timetable,
        "blocked": blocked
    }
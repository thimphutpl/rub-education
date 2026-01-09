import frappe
from frappe.model.document import Document

class ResearchCenterAnnualReporting(Document):
    pass


@frappe.whitelist()
def get_policy_briefs(research_center_name, posting_date):

    if not research_center_name or not posting_date:
        frappe.throw("Research Center Name and Posting Date are required")

    data = frappe.db.get_all(
        "Research Center Reporting Items",
        filters={
            "research_center_name": research_center_name,
            "posting_date": posting_date,
            "reporting_type": "Policy Briefs",
            "docstatus": 1
        },
        fields=[
            "policy_briefs_title",         
            "publisher_policy_brief",
            "date_of_publisher",
            "remarks_policy_briefs"
        ]
    )

    return data

@frappe.whitelist()
def get_journals(research_center_name, posting_date):

    if not research_center_name or not posting_date:
        frappe.throw("Research Center Name and Posting Date are required")

    data = frappe.db.get_all(
        "Research Center Reporting Items",
        filters={
            "research_center_name": research_center_name,
            "posting_date": posting_date,
            "reporting_type": "Journals",
            "docstatus": 1
        },
        fields=[
            "name_of_the_journal",
            "vol_no_journal",
            "issue_no_journal",
            "website_links_journal",
            "year"
        ]
    )

    return data

@frappe.whitelist()
def get_research_articles(research_center_name, posting_date):
    """
    Fetch Research Articles details including students' full names and employees' full names with designation.
    """

    if not research_center_name or not posting_date:
        frappe.throw("Research Center Name and Posting Date are required")
    articles = frappe.db.get_all(
        "Research Center Reporting Items",
        filters={
            "research_center_name": research_center_name,
            "posting_date": posting_date,
            "reporting_type": "Research Articles",
            "docstatus": 1
        },
        fields=[
            "name", 
            "research_articles_title",
            "publisher",
            "website_link_articles",
            "year"
        ]
    )

    result = []

    for article in articles:
        students = frappe.db.get_all(
            "Research Article Students",
            filters={"parent": article.name},
            fields=["student"]
        )
        student_fullnames = []
        for s in students:
            student_doc = frappe.get_doc("Student", s.student)
            student_fullnames.append(f"{student_doc.first_name} {student_doc.last_name}")
        employees = frappe.db.get_all(
            "Research Article Employees",
            filters={"parent": article.name},
            fields=["employee"]
        )
        employee_fullnames = []
        for e in employees:
            emp_doc = frappe.get_doc("Employee", e.employee)
            employee_fullnames.append(f"{emp_doc.employee_name} ({emp_doc.designation})")
        row = {
            "research_articles_title": article.research_articles_title,
            "publisher": article.publisher,
            "website_link_articles": article.website_link_articles,
            "year": article.year,
            "students": student_fullnames,     
            "employees": employee_fullnames    
        }
        result.append(row)

    return result




@frappe.whitelist()
def get_conference_seminar_paper(research_center_name, posting_date):
    """
    Fetch Conference/Seminar Paper details including students' full names and employees' full names with designation.
    """

    if not research_center_name or not posting_date:
        frappe.throw("Research Center Name and Posting Date are required")
    papers = frappe.db.get_all(
        "Research Center Reporting Items",
        filters={
            "research_center_name": research_center_name,
            "posting_date": posting_date,
            "reporting_type": "Conference Seminar Paper",
            "docstatus": 1
        },
        fields=[
            "name",
            "conference_seminar_paper_title",
            "conferenceseminar_title",
            "date",
            "nationalinternational"
        ]
    )

    result = []

    for paper in papers:
        students = frappe.db.get_all(
            "Research Article Students",
            filters={"parent": paper.name},
            fields=["student"]
        )
        student_fullnames = []
        for s in students:
            student_doc = frappe.get_doc("Student", s.student)
            student_fullnames.append(f"{student_doc.first_name} {student_doc.last_name}")
        employees = frappe.db.get_all(
            "Research Article Employees",
            filters={"parent": paper.name},
            fields=["employee"]
        )
        employee_fullnames = []
        for e in employees:
            emp_doc = frappe.get_doc("Employee", e.employee)
            employee_fullnames.append(f"{emp_doc.employee_name} ({emp_doc.designation})")
        row = {
            "conference_seminar_paper_title": paper.conference_seminar_paper_title,
            "conferenceseminar_title": paper.conferenceseminar_title,
            "date": paper.date,
            "nationalinternational": paper.nationalinternational,
            "students": student_fullnames,      
            "employees": employee_fullnames     
        }
        result.append(row)

    return result


@frappe.whitelist()
def get_books_chapter(research_center_name, posting_date):
    """
    Fetch Book Chapter details including students' full names and employees' full names with designation.
    """

    if not research_center_name or not posting_date:
        frappe.throw("Research Center Name and Posting Date are required")
    chapters = frappe.db.get_all(
        "Research Center Reporting Items",
        filters={
            "research_center_name": research_center_name,
            "posting_date": posting_date,
            "reporting_type": "Book Chapters",
            "docstatus": 1
        },
        fields=[
            "name",
            "book_chapter_title",
            "book_title",
            "publishers",
            "website_link_books"
        ]
    )

    result = []

    for chapter in chapters:
        students = frappe.db.get_all(
            "Research Article Students",
            filters={"parent": chapter.name},
            fields=["student"]
        )

        student_fullnames = []
        for s in students:
            student_doc = frappe.get_doc("Student", s.student)
            student_fullnames.append(f"{student_doc.first_name} {student_doc.last_name}")
        employees = frappe.db.get_all(
            "Research Article Employees",
            filters={"parent": chapter.name},
            fields=["employee"]
        )

        employee_fullnames = []
        for e in employees:
            emp_doc = frappe.get_doc("Employee", e.employee)
            employee_fullnames.append(f"{emp_doc.employee_name} ({emp_doc.designation})")
        row = {
            "book_chapter_title": chapter.book_chapter_title,
            "book_title": chapter.book_title,
            "publishers": chapter.publishers,
            "website_link_books": chapter.website_link_books,
            "students": student_fullnames,      
            "employees": employee_fullnames     
        }
        result.append(row)

    return result

@frappe.whitelist()
def get_training_workshop_organized(research_center_name, posting_date):
    """
    Fetch Training/Workshop details organized by the Research Center including employees involved.
    """
    if not research_center_name or not posting_date:
        frappe.throw("Research Center Name and Posting Date are required")

    trainings = frappe.db.get_all(
        "Research Center Reporting Items",
        filters={
            "research_center_name": research_center_name,
            "posting_date": posting_date,
            "reporting_type": "Knowledge Transfer and Community Service",
            "docstatus": 1
        },
        fields=[
            "name",
            "trainings_organized_title",
            "no_of_staffs_engaged",
            "no_of_student_engaged",
            "no_of_external_participants",
            "venue",
            "date",
            "funding_source",
            "remarks"
        ]
    )

    result = []

    for training in trainings:
        employees = frappe.db.get_all(
            "Research Article Employees",
            filters={"parent": training.name},
            fields=["employee"]
        )

        employee_fullnames = []
        for e in employees:
            emp_doc = frappe.get_doc("Employee", e.employee)
            employee_fullnames.append(f"{emp_doc.employee_name} ({emp_doc.designation})")

        row = {
            "trainings_organized_title": training.trainings_organized_title,
            "no_of_staffs_engaged": training.no_of_staffs_engaged,
            "no_of_student_engaged": training.no_of_student_engaged,
            "no_of_external_participants": training.no_of_external_participants,
            "venue": training.venue,
            "date": training.date,
            "funding_source": training.funding_source,
            "remarks": training.remarks,
            "employee": employee_fullnames 
        }
        result.append(row)

    return result


@frappe.whitelist()
def get_research_event_organized(research_center_name, posting_date):
    """
    Fetch Research Event details organized by the Research Center.
    Returns a list of dicts for the child table.
    """
    if not research_center_name or not posting_date:
        frappe.throw(_("Research Center Name and Posting Date are required"))

    organizeds = frappe.db.get_all(
        "Research Center Reporting Items",
        filters={
            "research_center_name": research_center_name,
            "posting_date": posting_date,
            "reporting_type": "Research Event Organized",
            "docstatus": 1
        },
        fields=[
            "name",
            "research_event_organized_title",
            "no_of_staffs_engageds",
            "no_of_student_engageds",
            "no_of_external_participantss",
            "venues",
            "funding_sources",
            "remarkss"
        ]
    )

    # Prepare result list
    result = []
    for organized in organizeds:
        result.append({
            "research_event_organized_title": organized.get("research_event_organized_title"),
            "no_of_staffs_engageds": organized.get("no_of_staffs_engageds"),
            "no_of_student_engageds": organized.get("no_of_student_engageds"),
            "no_of_external_participantss": organized.get("no_of_external_participantss"),
            "venues": organized.get("venues"),
            "funding_sources": organized.get("funding_sources"),
            "remarkss": organized.get("remarkss")
        })

    return result

@frappe.whitelist()
def get_research_projects_funding(research_center_name, posting_date):

    if not research_center_name or not posting_date:
        frappe.throw("Research Center Name and Posting Date are required")

    fundings = frappe.db.get_all(
        "Research Center Reporting Items",
        filters={
            "research_center_name": research_center_name,
            "posting_date": posting_date,
            "reporting_type": "Research Projects and Funding",
            "docstatus": 1
        },
        fields=[
            "name",
            "project_title",
            "funding_agency_nameinstitution",
            "country",
            "application_amount",
            "funding_secured",
            "is_joint_research",
            "secured_amount",
            "grant_in_kind",
            "project_completed"
        ]
    )

    result = []

    for funding in fundings:

        investigators = frappe.db.get_all(
            "Research Article Employees",
            filters={"parent": funding.name},
            fields=["employee"]
        )

        principal = []
        co_investigators = []

        for idx, inv in enumerate(investigators):

            if not inv.employee:
                continue

            emp = frappe.db.get_value(
                "Employee",
                inv.employee,
                ["employee_name", "designation"],
                as_dict=True
            )

            if not emp:
                continue

            emp_label = f"{emp.employee_name} ({emp.designation})"

            if idx == 0:
                principal.append(emp_label)
            else:
                co_investigators.append(emp_label)

        result.append({
            "project_title": funding.project_title,
            "funding_agency_nameinstitution": funding.funding_agency_nameinstitution,
            "country": funding.country,
            "application_amount": funding.application_amount,
            "funding_secured": funding.funding_secured,
            "is_joint_research": funding.is_joint_research,
            "secured_amount": funding.secured_amount,
            "grant_in_kind": funding.grant_in_kind,
            "project_completed": funding.project_completed,
            "principal": principal,
            "employees": co_investigators
        })

    return result

# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Module",
            "fieldname": "module",
            "fieldtype": "Data",
            "width": 300
        },
        
        {
            "label": "Type",
            "fieldname": "type",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Semester",
            "fieldname": "module_semester",
            "fieldtype": "Data",
            "width": 120
        },
         {
            "label": "Max. Marks",
            "fieldname": "max_marks",
            "fieldtype": "Float",
            "width": 120
        },
         {
            "label": "Marks Secured",
            "fieldname": "marks_secured",
            "fieldtype": "Float",
            "width": 120
        }
    ]


def get_data(filters):
    filters = filters or {}

    conditions = []
    values = {}

    if filters.get("college"):
        conditions.append("mc.college = %(college)s")
        values["college"] = filters.get("college")

    if filters.get("semester"):
        conditions.append("mc.module_semester = %(semester)s")
        values["semester"] = filters.get("semester")

    if filters.get("programme"):
        conditions.append("mc.programme = %(programme)s")
        values["programme"] = filters.get("programme")

    condition_sql = ""
    if conditions:
        condition_sql = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT 
            m.name AS module,
            mc.module_semester
        FROM `tabModule College` mc
        INNER JOIN `tabModule` m 
            ON mc.parent = m.name
        {condition_sql}
    """

    data = frappe.db.sql(query, values, as_dict=True)

    #Adding total marks for each module here on
    new_data = []

    for row in data:
        # First copy → Continuous Assessment
        ca_row = row.copy()
        ca_row["type"] = "CA"
        new_data.append(ca_row)

        # Second copy → Semester Exam
        se_row = row.copy()
        se_row["type"] = "SE"
        new_data.append(se_row)

    data = new_data

    student = filters.get("student")
    college = filters.get("college")
    programme = filters.get("programme")
    semester = filters.get("semester")

    for i in data:
        # Determine the assessment type
        if i.type == 'SE':
            assessment_type = 'Semester Exam'
        elif i.type == 'CA':
            assessment_type = 'Continuous Assessment'
        else:
            continue  # skip if type is unknown

        total = frappe.db.sql("""
            SELECT SUM(al.weightage_achieved)
            FROM `tabAssessment Ledger` al
            INNER JOIN `tabAssessment Component` ac
                ON al.assessment_component = ac.name
            WHERE al.student = %s
            AND al.college = %s
            AND al.programme = %s
            AND al.semester = %s
            AND al.module = %s
            AND al.is_cancelled != 1
            AND al.has_reassessment !=1
            AND ac.assessment_component_type = %s
        """, (student, college, programme, semester, i.module, assessment_type))

        i["marks_secured"] = total[0][0] or 0

        query1 = f"""
                SELECT sum(mai.weightage)
                FROM `tabModule Assessment Item` mai
                INNER JOIN `tabModule Assessment Criteria` mac 
                    ON mai.parent = mac.name
                WHERE mac.college = '{college}'
                AND mac.programme = '{programme}'
                AND mac.module = '{i.module}'
                AND mac.semester = '{semester}'
                AND mai.assessment_component_type = '{assessment_type}'
                and docstatus =1
            """

        # frappe.throw(str(query1))
        

        result1 = frappe.db.sql(query1)
        if result1:
            i["max_marks"] = result1[0][0]

        # frappe.throw(frappe.as_json(result))

        

    # frappe.throw(frappe.as_json(data))
    # for i in data:
    #     if i.module
    previous_module = None

    for row in data:
        if row["module"] == previous_module:
            row["module"] = ""
        else:
            previous_module = row["module"]

    return data
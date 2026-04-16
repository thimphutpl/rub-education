import frappe

# @frappe.whitelist()
# def get_results(college, programme, academic_term, student_section):

#     # 🔹 Get modules
#     modules = frappe.db.sql("""
#         SELECT module
#         FROM `tabModule Enrolment Key`
#         WHERE college=%s
#         AND programme=%s
#         AND academic_term=%s
#         AND student_section=%s 
#         AND docstatus = 1
#     """, (college, programme, academic_term, student_section), as_dict=1)

   

#     module_list = [m.module for m in modules]
#     # final_module_list = []

#     final_module_list = []

#     for i in module_list:
#         total_weightage = frappe.db.sql("""
#             SELECT 
#                 ma.module, 
#                 SUM(CASE 
#                     WHEN mai.assessment_component_type IN 
#                         ('Continuous Assessment', 'Continuous Assessment (Theory)')          
#                     THEN mai.weightage ELSE 0 
#                 END) AS ca_total,      

#                 SUM(CASE 
#                     WHEN mai.assessment_component_type IN 
#                         ('Semester Exam', 'Semester Exam (Theory)')        
#                     THEN mai.weightage ELSE 0 
#                 END) AS semester_total  

#             FROM `tabModule Assessment Item` mai 
#             INNER JOIN `tabModule Assessment Criteria` ma      
#                 ON mai.parent = ma.name 

#             WHERE 
#                 ma.college = %s 
#                 AND ma.academic_term = %s  
#                 AND ma.module = %s 

#             GROUP BY ma.module
#         """, (college, academic_term, i), as_dict=True)

#         if total_weightage:
#             final_module_list.append({
#                 "module": total_weightage[0]["module"],
#                 "ca_total": total_weightage[0]["ca_total"],
#                 "semester_total": total_weightage[0]["semester_total"]
#             })
#         else:
#             final_module_list.append({
#                 "module": i,
#                 "ca_total": 0,
#                 "semester_total": 0
#             })

#     # frappe.throw(frappe.as_json(final_module_list))

#     # # 🔹 Get students
#     students = frappe.db.sql("""
#         SELECT distinct student, student_name
#         FROM `tabModule Enrolment`
#         WHERE college=%s
#         AND program=%s
#         AND academic_term=%s
#         AND student_section=%s
#         And docstatus =1
#     """, (college, programme, academic_term, student_section), as_dict=1)

#     # frappe.throw(frappe.as_json(students))

#     result = []

#     for stu in students:
#         student_data = {
#             "student_no": stu.student,
#             "student_name": stu.student_name,
#             "results": {}
#         }

#         for m in module_list:
#             # 🔹 Replace with your real marks table
#             marks = frappe.db.sql("""
#                 SELECT 
#                     SUM(CASE 
#                         WHEN ac.assessment_component_type IN ('Continuous Assessment', 'Continuous Assessment (Theory)')
#                         THEN al.weightage_achieved ELSE 0 END) AS ca,

#                     SUM(CASE 
#                         WHEN ac.assessment_component_type = 'Semester Exam'
#                         THEN al.weightage_achieved ELSE 0 END) AS se

#                 FROM `tabAssessment Ledger` al
#                 INNER JOIN `tabAssessment Component` ac 
#                     ON al.assessment_component = ac.name

#                 WHERE 
#                     al.student = %s
#                     AND al.module = %s
#                     and is_cancelled = 0
#                     and has_reassessment = 0
#             """, (stu.student, m), as_dict=1)

#             if marks:
#                 ca = marks[0].ca or 0
#                 se = marks[0].se or 0
#                 total = ca + se

#                 student_data["results"][m] = {
#                     "ca": ca,
#                     "se": se,
#                     "tl": total
#                 }
#             else:
#                 student_data["results"][m] = {
#                     "ca": 0,
#                     "se": 0,
#                     "tl": 0
#                 }

#         result.append(student_data)
  
   

#     return {
#         "modules": module_list,
#         "module_weightage": final_module_list,
#         "students": result
#     }

@frappe.whitelist()
def get_results(college, programme, academic_term, student_section):



    # 🔹 1. Get modules
    modules = frappe.db.sql("""
        SELECT module
        FROM `tabModule Enrolment Key`
        WHERE college=%s
        AND programme=%s
        AND academic_term=%s
        AND student_section=%s 
        AND docstatus = 1
    """, (college, programme, academic_term, student_section), as_dict=1)

    module_list = [m.module for m in modules]

    if not module_list:
        return {
            "modules": [],
            "module_weightage": [],
            "students": []
        }

    # 🔹 2. Get module weightage (OPTIMIZED - single query)
    weightage_data = frappe.db.sql("""
        SELECT 
            ma.module, 

            COALESCE(SUM(CASE 
                WHEN mai.assessment_component_type IN 
                    ('Continuous Assessment', 'Continuous Assessment (Theory)')          
                THEN mai.weightage ELSE 0 
            END), 0) AS ca_total,      

            COALESCE(SUM(CASE 
                WHEN mai.assessment_component_type IN 
                    ('Semester Exam', 'Semester Exam (Theory)')        
                THEN mai.weightage ELSE 0 
            END), 0) AS semester_total  

        FROM `tabModule Assessment Item` mai 
        INNER JOIN `tabModule Assessment Criteria` ma      
            ON mai.parent = ma.name 

        WHERE 
            ma.college = %s 
            AND ma.academic_term = %s  
            AND ma.module IN %s

        GROUP BY ma.module
    """, (college, academic_term, tuple(module_list)), as_dict=1)

    weightage_map = {d.module: d for d in weightage_data}

    # frappe.throw(frappe.as_json())

    final_module_list = []
    for m in module_list:
        if m in weightage_map:
            final_module_list.append({
                "module": m,
                "ca_total": weightage_map[m].ca_total,
                "semester_total": weightage_map[m].semester_total
            })
        else:
            final_module_list.append({
                "module": m,
                "ca_total": 0,
                "semester_total": 0
            })

    # 🔹 3. Get students
    students = frappe.db.sql("""
        SELECT DISTINCT student, student_name
        FROM `tabModule Enrolment`
        WHERE college=%s
        AND program=%s
        AND academic_term=%s
        AND student_section=%s
        AND docstatus = 1
    """, (college, programme, academic_term, student_section), as_dict=1)

    if not students:
        return {
            "modules": module_list,
            "module_weightage": final_module_list,
            "students": []
        }

    student_ids = [s.student for s in students]

    # 🔹 4. Get all marks (OPTIMIZED - single query)
    all_marks = frappe.db.sql("""
        SELECT 
            al.student,
            al.module,

            COALESCE(SUM(CASE 
                WHEN ac.assessment_component_type IN 
                    ('Continuous Assessment', 'Continuous Assessment (Theory)')
                THEN al.weightage_achieved ELSE 0 END), 0) AS ca,

            COALESCE(SUM(CASE 
                WHEN ac.assessment_component_type IN 
                    ('Semester Exam', 'Semester Exam (Theory)')
                THEN al.weightage_achieved ELSE 0 END), 0) AS se

        FROM `tabAssessment Ledger` al
        INNER JOIN `tabAssessment Component` ac 
            ON al.assessment_component = ac.name

        WHERE 
            al.student IN %s
            AND al.module IN %s
            AND al.is_cancelled = 0
            AND al.has_reassessment = 0

        GROUP BY al.student, al.module
    """, (tuple(student_ids), tuple(module_list)), as_dict=1)

    # 🔹 5. Create lookup map
    marks_map = {}
    for row in all_marks:
        marks_map[(row.student, row.module)] = row

    # 🔹 6. Build final result
    result = []

    for stu in students:
        student_data = {
            "student_no": stu.student,
            "student_name": stu.student_name,
            "results": {}
        }

        for m in module_list:
            key = (stu.student, m)

            if key in marks_map:
                ca = marks_map[key].ca or 0
                se = marks_map[key].se or 0
            else:
                ca = 0
                se = 0

            student_data["results"][m] = {
                "ca": ca,
                "se": se,
                "tl": ca + se
            }

        result.append(student_data)

    # frappe.throw(frappe.as_json(result))
    ca_pass_percentage = frappe.db.get_value("Pass Criteria",{"college":college},'ca_passing_citeria')
    se_pass_percentage = frappe.db.get_value("Pass Criteria",{"college":college},'se_passing_citeria')
    tl_pass_percentage = frappe.db.get_value("Pass Criteria",{"college":college},'total_passing_citeria')
    failed_module_for_repeat = frappe.db.get_value("Pass Criteria",{"college":college},'failed_module')

    for i in result:

        failed_modules = []

        for module, res in i.get("results", {}).items():

            module_info = weightage_map.get(module, {})

            ca_total = module_info.get("ca_total", 0)
            se_total = module_info.get("semester_total", 0)

            ca = res.get("ca") or 0
            se = res.get("se") or 0
            tl = res.get("tl") or 0

            module_failed = []

            # -----------------------
            # CA CHECK
            ca_percent = (ca / ca_total * 100) if ca_total else 0
            if ca_percent < ca_pass_percentage:
                module_failed.append("CA")
                res["ca_pass"] = 0
            else:
                res["ca_pass"] = 1

            # -----------------------
            # SE CHECK
            se_percent = (se / se_total * 100) if se_total else 0
            if se_percent < se_pass_percentage:
                module_failed.append("SE")
                res["se_pass"] = 0
            else:
                res["se_pass"] = 1

            # -----------------------
            # TL CHECK
            tl_total = ca_total + se_total
            tl_percent = (tl / tl_total * 100) if tl_total else 0

            if tl_percent < tl_pass_percentage:
                module_failed.append("TL")
                res["tl_pass"] = 0
            else:
                res["tl_pass"] = 1

            # -----------------------
            # MODULE FAILED?
            if module_failed:
                failed_modules.append(module)

        # =========================
        # FINAL RESULT RULE
        # =========================
        no_failed = len(failed_modules)

        if no_failed == 0:
            i["remarks"] = "Pass"

        elif no_failed >= 3:
            i["remarks"] = "Semester Repeat"

        else:
            i["remarks"] = "Fail"

        i["no_failed_modules"] = no_failed

    

    # frappe.throw(str(result))
    return {
        "modules": final_module_list,
        "students": result
    }


@frappe.whitelist()
def get_declared_results(college, programme, academic_term, student_section):

    # 🔹 1. Get modules
    modules = frappe.db.sql("""
        SELECT module
        FROM `tabModule Enrolment Key`
        WHERE college=%s
        AND programme=%s
        AND academic_term=%s
        AND student_section=%s 
        AND docstatus = 1
    """, (college, programme, academic_term, student_section), as_dict=1)

    # frappe.throw(frappe.as_json(modules))

    module_list = [m.module for m in modules]

    if not module_list:
        return {
            "modules": [],
            "module_weightage": [],
            "students": []
        }

    # 🔹 2. Get module weightage (OPTIMIZED - single query)
    weightage_data = frappe.db.sql("""
        SELECT 
            ma.module, 

            COALESCE(SUM(CASE 
                WHEN mai.assessment_component_type IN 
                    ('Continuous Assessment', 'Continuous Assessment (Theory)')          
                THEN mai.weightage ELSE 0 
            END), 0) AS ca_total,      

            COALESCE(SUM(CASE 
                WHEN mai.assessment_component_type IN 
                    ('Semester Exam', 'Semester Exam (Theory)')        
                THEN mai.weightage ELSE 0 
            END), 0) AS semester_total  

        FROM `tabModule Assessment Item` mai 
        INNER JOIN `tabModule Assessment Criteria` ma      
            ON mai.parent = ma.name 

        WHERE 
            ma.college = %s 
            AND ma.academic_term = %s  
            AND ma.module IN %s

        GROUP BY ma.module
    """, (college, academic_term, tuple(module_list)), as_dict=1)

    weightage_map = {d.module: d for d in weightage_data}

    # frappe.throw(frappe.as_json())

    final_module_list = []
    for m in module_list:
        if m in weightage_map:
            final_module_list.append({
                "module": m,
                "ca_total": weightage_map[m].ca_total,
                "semester_total": weightage_map[m].semester_total
            })
        else:
            final_module_list.append({
                "module": m,
                "ca_total": 0,
                "semester_total": 0
            })

    # 🔹 3. Get students
    students = frappe.db.sql("""
        SELECT DISTINCT student, student_name
        FROM `tabModule Enrolment`
        WHERE college=%s
        AND program=%s
        AND academic_term=%s
        AND student_section=%s
        AND docstatus = 1
    """, (college, programme, academic_term, student_section), as_dict=1)

    if not students:
        return {
            "modules": module_list,
            "module_weightage": final_module_list,
            "students": []
        }

    student_ids = [s.student for s in students]

    # 🔹 4. Get all marks (OPTIMIZED - single query)
    all_marks = frappe.db.sql("""
        SELECT 
            re.student,
            rea.module,
            COALESCE(rea.ca, 0) AS ca,
            COALESCE(rea.se, 0) AS se,
            COALESCE(rea.weightage_obtained, 0) AS tl,
            rea.passed

        FROM `tabResult Entry Item` rea
        INNER JOIN `tabResult Entry` re 
            ON rea.parent = re.name

        WHERE 
            re.student IN %s
            AND rea.module IN %s
            AND re.docstatus = 0

    """, (tuple(student_ids), tuple(module_list)), as_dict=1)
    # frappe.throw(frappe.as_json(all_marks))
    # all_marks = frappe.db.sql("""
    #     SELECT 
    #         al.student,
    #         al.module,

    #         COALESCE(SUM(CASE 
    #             WHEN ac.assessment_component_type IN 
    #                 ('Continuous Assessment', 'Continuous Assessment (Theory)')
    #             THEN al.weightage_achieved ELSE 0 END), 0) AS ca,

    #         COALESCE(SUM(CASE 
    #             WHEN ac.assessment_component_type IN 
    #                 ('Semester Exam', 'Semester Exam (Theory)')
    #             THEN al.weightage_achieved ELSE 0 END), 0) AS se

    #     FROM `tabAssessment Ledger` al
    #     INNER JOIN `tabAssessment Component` ac 
    #         ON al.assessment_component = ac.name

    #     WHERE 
    #         al.student IN %s
    #         AND al.module IN %s
    #         AND al.is_cancelled = 0
    #         AND al.has_reassessment = 0

    #     GROUP BY al.student, al.module
    # """, (tuple(student_ids), tuple(module_list)), as_dict=1)

    # 🔹 5. Create lookup map
    marks_map = {}
    for row in all_marks:
        marks_map[(row.student, row.module)] = row

    # 🔹 6. Build final result
    result = []

    for stu in students:
        student_data = {
            "student_no": stu.student,
            "student_name": stu.student_name,
            "results": {}
        }

        for m in module_list:
            key = (stu.student, m)

            if key in marks_map:
                ca = marks_map[key].ca or 0
                se = marks_map[key].se or 0
                passed = marks_map[key].passed or 0
            else:
                ca = 0
                se = 0
                passed = 0

            student_data["results"][m] = {
                "ca": ca,
                "se": se,
                "tl": ca + se,
                "passed": passed
            }

        result.append(student_data)

    

   

    

    # frappe.throw(frappe.as_json(result))
    return {
        "modules": final_module_list,
        "students": result
    }


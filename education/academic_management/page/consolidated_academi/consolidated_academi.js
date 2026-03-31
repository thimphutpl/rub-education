frappe.pages['consolidated-academi'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Consolidated Academic Transcript',
        single_column: true
    });

    let topContainer = $('<div class="timetable-top-container"></div>').appendTo(page.body);

    // 🔹 Container for fields
    let fieldContainer = $(`
        <div class="custom-fields-container" 
             style="display:flex; flex-wrap:wrap; gap:20px; margin-bottom:10px;">
        </div>
    `).appendTo(topContainer);

    // 🔹 Table container
    let container = $('<div class="timetable-container"></div>').appendTo(topContainer);

    // 🔹 Student field
    let student = frappe.ui.form.make_control({
        df: {
            fieldname: 'student',
            label: 'Student',
            fieldtype: 'Link',
            options: "Student",
            reqd: 1,
            change: function () {
                let student_id = student.get_value();

                if (student_id) {
                    // Get student name and programme
                    frappe.db.get_value("Student", student_id, ["student_name", "programme"])
                        .then(r => {
                            if (r.message) {
                                student_name.set_value(r.message.student_name);
                                programme.set_value(r.message.programme);
                            }
                        });

                    // Load results
                    load_results(container, student_id);
                } else {
                    container.html("<b>Please select a student</b>");
                    student_name.set_value('');
                    programme.set_value('');
                }
            }
        },
        parent: fieldContainer,
        render_input: true
    });
    student.refresh();

    // 🔹 Student Name field (read-only)
    let student_name = frappe.ui.form.make_control({
        parent: fieldContainer,
        df: {
            label: 'Student Name',
            fieldname: 'student_name',
            fieldtype: 'Data',
            read_only: 1
        },
        render_input: true
    });
    student_name.refresh();

    // 🔹 Programme field (read-only)
    let programme = frappe.ui.form.make_control({
        parent: fieldContainer,
        df: {
            label: 'Programme',
            fieldname: 'programme',
            fieldtype: 'Link',
            options: 'Programme',
            read_only: 1
        },
        render_input: true
    });
    programme.refresh();
}


// function load_results(container, student) {
//     container.html("<p>Loading results...</p>");

//     frappe.call({
//         method: "education.academic_management.page.consolidated_academi.consolidated_academi.get_results",
//         args: { student: student },
//         callback: function(r) {
//             if (!r.message || !r.message.results.length) {
//                 container.html("<b>No data found</b>");
//                 return;
//             }

//             let data = r.message.results;
//             let student_name = r.message.student;

//             // 🔹 Group by semester
//             let grouped = {};
//             data.forEach(d => {
//                 if (!grouped[d.semester]) {
//                     grouped[d.semester] = [];
//                 }
//                 grouped[d.semester].push(d);
//             });

//             let html = `
//                 <style>
//                     table {
//                         border-collapse: collapse;
//                         width: 100%;
//                         font-size: 13px;
//                     }
//                     th, td {
//                         border: 1px solid #555;
//                         padding: 6px;
//                         text-align: center;
//                     }
//                     th {
//                         background-color: #f2f2f2;
//                     }
//                     .semester-cell {
//                         font-weight: bold;
//                         background-color: #fafafa;
//                     }
//                 </style>

//                 <h3>Semester Result — ${student_name}</h3>

//                 <table>
//                     <thead>
//                         <tr>
//                             <th>Semester</th>
//                             <th>Module</th>
//                             <th>Max. Marks</th>
//                             <th>Marks Secured</th>
//                             <th>Credit</th>
//                             <th>Weighting</th>
//                             <th>Remarks</th>
//                         </tr>
//                     </thead>
//                     <tbody>
//             `;

//             Object.keys(grouped).forEach(semester => {
//                 let rows = grouped[semester];

//                 // 🔹 Calculate semester total
//                 let total_marks = 0;
//                 let max_total = rows.length * 100;

//                 rows.forEach(d => {
//                     total_marks += Number(d.total) || 0;
//                 });

//                 let percentage = max_total > 0
//                     ? (total_marks / max_total) * 100
//                     : 0;

//                 // 🔹 Weighting (you can change logic)
//                 let weighting = percentage.toFixed(2) + "%";

//                 // 🔹 Remarks logic
//                 let remarks = percentage >= 50 ? "Pass" : "Fail";

//                 rows.forEach((d, index) => {
//                     html += `<tr>`;

//                     // Semester column
//                     if (index === 0) {
//                         html += `<td class="semester-cell" rowspan="${rows.length}">${semester}</td>`;
//                     }

//                     html += `
//                         <td>${d.module}</td>
//                         <td>100</td>
//                         <td>${d.total}</td>
//                         <td>${d.credit}</td>
//                     `;

//                     // 🔹 Weighting & Remarks only once per semester
//                     if (index === 0) {
//                         html += `
//                             <td rowspan="${rows.length}">${weighting}</td>
//                             <td rowspan="${rows.length}">${remarks}</td>
//                         `;
//                     }

//                     html += `</tr>`;
//                 });
//             });

//             html += `</tbody></table>`;
//             container.html(html);
//         }
//     });
// }
function load_results(container, student) {
    container.html("<p>Loading results...</p>");

    frappe.call({
        method: "education.academic_management.page.consolidated_academi.consolidated_academi.get_results",
        args: { student: student },
        callback: function(r) {
            if (!r.message || !r.message.results.length) {
                container.html("<b>No data found</b>");
                return;
            }

            let data = r.message.results;
            let student_name = r.message.student;

            // 🔹 Group by semester
            let grouped = {};
            data.forEach(d => {
                if (!grouped[d.semester]) {
                    grouped[d.semester] = [];
                }
                grouped[d.semester].push(d);
            });

            let html = `
                <style>
                    table {
                        border-collapse: collapse;
                        width: 100%;
                        font-size: 13px;
                    }
                    th, td {
                        border: 1px solid #555;
                        padding: 6px;
                        text-align: center;
                    }
                    th {
                        background-color: #f2f2f2;
                    }
                    .semester-cell {
                        font-weight: bold;
                        background-color: #fafafa;
                    }
                    .total-row {
                        font-weight: bold;
                        background-color: #f9f9f9;
                    }
                </style>

                <h3>Semester Result — ${student_name}</h3>

                <table>
                    <thead>
                        <tr>
                            <th>Semester</th>
                            <th>Module</th>
                            <th>Max. Marks</th>
                            <th>Marks Secured</th>
                            <th>Credit</th>
                            <th>Weighting</th>
                            <th>Remarks</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            Object.keys(grouped).forEach(semester => {
                let rows = grouped[semester];

                let total_marks = 0;
                let total_credit = 0;
                let max_total = rows.length * 100;

                rows.forEach(d => {
                    total_marks += Number(d.total) || 0;
                    total_credit += Number(d.credit) || 0;
                });

                let percentage = max_total > 0
                    ? (total_marks / max_total) * 100
                    : 0;

                let semester_weightage = Number(rows[0].weighting) || 0;
                let weighted_score = max_total > 0
                    ? ((total_marks / max_total) * semester_weightage).toFixed(2)
                    : 0;

                let remarks = percentage >= 50 ? "Pass" : "Fail";

                rows.forEach((d, index) => {
                    html += `<tr>`;

                    // 🔹 Semester column (rowspan includes total row)
                    if (index === 0) {
                        html += `<td class="semester-cell" rowspan="${rows.length + 1}">${semester}</td>`;
                    }

                    html += `
                        <td>${d.module}</td>
                        <td>100</td>
                        <td>${d.total}</td>
                        <td>${d.credit || ""}</td>
                    `;

                    // 🔹 Weighting & Remarks only once (NOT including total row)
                    if (index === 0) {
                        html += `
                            <td rowspan="${rows.length}">${semester_weightage}</td>
                            <td rowspan="${rows.length}">${remarks}</td>
                        `;
                    }

                    html += `</tr>`;
                });

                // 🔹 TOTAL ROW (aligned correctly under columns)
                html += `
                    <tr class="total-row">
                        <td>Total</td>
                        <td>${max_total}</td>
                        <td>${total_marks}</td>
                        <td>${total_credit}</td>
                        <td>${weighted_score}</td> <!-- THIS is under Weighting -->
                        <td></td>
                    </tr>
                `;
            });

            html += `</tbody></table>`;
            container.html(html);
        }
    });
}

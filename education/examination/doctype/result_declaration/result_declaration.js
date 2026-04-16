frappe.ui.form.on("Result Declaration", {

    refresh: function(frm) {
        // Optional: auto load on refresh if fields are filled
        if (all_fields_filled(frm)) {
            load_results(frm);
        }
    },

    get_data: function(frm) {
        if (!all_fields_filled(frm)) {
            frappe.msgprint("Please select all fields");
            return;
        }
        load_results(frm);
    }
});


// ✅ Check required fields
function all_fields_filled(frm) {
    return frm.doc.college && frm.doc.programme && frm.doc.academic_term && frm.doc.student_section;
}


// ✅ Load data from backend
function load_results(frm) {

    frm.fields_dict.result_html.$wrapper.html("<p>Loading...</p>");

    frappe.call({
        method: "education.academic_management.page.semester_result_decl.semester_result_decl.get_results",
        args: {
            college: frm.doc.college,
            programme: frm.doc.programme,
            academic_term: frm.doc.academic_term,
            student_section: frm.doc.student_section
        },
        callback: function(r) {

            if (!r.message) {
                frm.fields_dict.result_html.$wrapper.html("<b>No data found</b>");
                return;
            }

            render_table(frm, r.message);
        }
    });
}


// ✅ Render table
// function render_table(frm, data) {

//     let html = `
//         <style>
//             table, th, td {
//                 border: 1px solid #444;
//                 border-collapse: collapse;
//             }
//             th, td {
//                 padding: 5px;
//                 text-align: center;
//             }
//             thead {
//                 background: #f3f3f3;
//             }
//             .pass {
//                 color: green;
//                 font-weight: bold;
//             }
//             .fail {
//                 color: red;
//                 font-weight: bold;
//             }
//         </style>

//         <h4>Semester Result</h4>

//         <table>
//             <thead>
//                 <tr>
//                     <th rowspan="2">Student No</th>
//                     <th rowspan="2">Name</th>
//                     ${data.modules.map(m => `<th colspan="3">${m}</th>`).join("")}
//                     <th rowspan="2">Total</th>
//                     <th rowspan="2">%</th>
//                     <th rowspan="2">Result</th>
//                 </tr>
//                 <tr>
//                     ${data.modules.map(() => `<th>CA</th><th>SE</th><th>TL</th>`).join("")}
//                 </tr>
//             </thead>
//             <tbody>
//     `;

//     // 🔹 Students
//     data.students.forEach(stu => {

//         let total = 0;
//         let max_total = data.modules.length * 100;

//         html += `
//             <tr>
//                 <td>${stu.student_no}</td>
//                 <td>${stu.student_name}</td>
//         `;

//         data.modules.forEach(m => {

//             let res = stu.results[m] || {ca: 0, se: 0, tl: 0};

//             html += `
//                 <td>${res.ca}</td>
//                 <td>${res.se}</td>
//                 <td>${res.tl}</td>
//             `;

//             total += Number(res.tl) || 0;
//         });

//         let percentage = max_total > 0 ? ((total / max_total) * 100).toFixed(2) : 0;
//         let status = percentage >= 50 ? "Pass" : "Fail";
//         let cls = status === "Pass" ? "pass" : "fail";

//         html += `
//             <td>${total}</td>
//             <td>${percentage}%</td>
//             <td class="${cls}">${status}</td>
//         </tr>
//         `;
//     });

//     html += `
//             </tbody>
//         </table>
//     `;

//     // ✅ Render in HTML field
//     frm.fields_dict.result_html.$wrapper.html(html);
// }
function render_table(frm, data) {

    let html = `
        <style>
            table, th, td {
                border: 1px solid #444;
                border-collapse: collapse;
            }
            th, td {
                padding: 5px;
                text-align: center;
                font-size: 13px;
            }
            thead {
                background: #f3f3f3;
            }
            .pass {
                
                font-weight: bold;
            }
            .fail {
                color: red;
                font-weight: bold;
            }
        </style>

        <h4>Semester Result</h4>

        <table>
            <thead>
                <tr>
                    <th rowspan="2">Student No</th>
                    <th rowspan="2">Name</th>

                    ${data.modules.map(m => {
                        let module_name = m.module || m;
                        return `<th colspan="3">${module_name}</th>`;
                    }).join("")}

                    <th rowspan="2">Total</th>
                    <th rowspan="2">%</th>
                    <th rowspan="2">Remarks</th>
                </tr>

                <tr>
                    ${data.modules.map(m => `
                        <th>CA (${m.ca_total || 0})</th>
                        <th>SE (${m.semester_total || 0})</th>
                        <th>TL</th>
                    `).join("")}
                </tr>
            </thead>

            <tbody>
    `;

    data.students.forEach(stu => {

        let total = 0;
        let max_total = data.modules.length * 100;

        html += `
            <tr>
                <td>${stu.student_no}</td>
                <td>${stu.student_name}</td>
        `;

        data.modules.forEach(m => {

            let module_name = m.module || m;

            let res = stu.results[module_name] || {
                ca: 0,
                se: 0,
                tl: 0,
                ca_pass: 1,
                se_pass: 1,
                tl_pass: 1
            };

            // 🔴 Conditional coloring
            let caClass = res.ca_pass == 0 ? "fail" : "pass";
            let seClass = res.se_pass == 0 ? "fail" : "pass";
            let tlClass = res.tl_pass == 0 ? "fail" : "pass";

            html += `
                <td class="${caClass}">${res.ca}</td>
                <td class="${seClass}">${res.se}</td>
                <td class="${tlClass}">${res.tl}</td>
            `;

            total += Number(res.tl) || 0;
        });

        let percentage = max_total > 0 ? ((total / max_total) * 100).toFixed(2) : 0;

        let remarks = stu.remarks || "Pass";
        let cls = remarks.startsWith("Fail") ? "fail" : "pass";

        html += `
            <td><b>${total}</b></td>
            <td><b>${percentage}%</b></td>
            <td class="${cls}">${remarks}</td>
        </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    frm.fields_dict.result_html.$wrapper.html(html);
}
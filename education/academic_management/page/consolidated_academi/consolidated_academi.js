frappe.pages['consolidated-academi'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Consolidated Academic Transcript',
        single_column: true
    });

    let topContainer = $('<div class="timetable-top-container"></div>').appendTo(page.body);

    let printBtn = $('<button class="btn btn-primary" style="margin-bottom:10px;">Print Semester Result</button>')
		.appendTo(topContainer)
		.click(function(){
			printSemesterResult(container);
		});

    // 🔹 Container for fields
    let fieldContainer = $(`
        <div class="custom-fields-container" 
             style="display:flex; flex-wrap:wrap; gap:20px; margin-bottom:10px;">
        </div>
    `).appendTo(topContainer);
    
    // Button container
    let buttonContainer = $(`
        <div style="margin-bottom: 20px;">
            <button class="btn btn-primary btn-view-results">View Results</button>
        </div>
    `).appendTo(topContainer);

    // 🔹 Table container
    let container = $('<div class="timetable-container"></div>').appendTo(topContainer);

    // 🔹 Company field (MANDATORY)
    let company = frappe.ui.form.make_control({
        df: {
            fieldname: 'company',
            label: 'College',
            fieldtype: 'Link',
            options: "Company",
            reqd: 1,
            change: function() {
                // No auto-clearing of other fields anymore
            }
        },
        parent: fieldContainer,
        render_input: true
    });
    company.refresh();
    
    // 🔹 Program field (Optional)
    let program = frappe.ui.form.make_control({
        df: {
            fieldname: 'program',
            label: 'Programme (Optional)',
            fieldtype: 'Link',
            options: "Programme",
            change: function() {
                // No auto-clearing
            }
        },
        parent: fieldContainer,
        render_input: true
    });
    program.refresh();

    // 🔹 Student field (Optional)
    let student = frappe.ui.form.make_control({
        df: {
            fieldname: 'student',
            label: 'Student (Optional)',
            fieldtype: 'Link',
            options: "Student",
            change: function() {
                // No auto-clearing
            }
        },
        parent: fieldContainer,
        render_input: true
    });
    student.refresh();
    
    // View Results button click handler
    $('.btn-view-results').on('click', function() {
        let company_val = company.get_value();
        let program_val = program.get_value();
        let student_val = student.get_value();
        
        // Validate Company is mandatory
        if (!company_val) {
            frappe.msgprint({
                title: __('Validation Error'),
                message: __('Company is mandatory. Please select a Company.'),
                indicator: 'red'
            });
            return;
        }
        
        // Build filters object with all selected values
        let filters = { company: company_val };
        
        if (program_val) {
            filters.program = program_val;
        }
        
        if (student_val) {
            // If specific student is selected, load individual results
            load_results_individual(container, student_val, company_val);
        } 
        else if (program_val) {
            // Load results for program within the company
            load_results_bulk(container, filters, `${company_val} | Programme: ${program_val}`);
        }
        else {
            // Load all students under the company
            load_results_bulk(container, { company: company_val }, `${company_val}`);
        }
    });
}
function load_results_individual(container, student, company) {
    container.html("<p>Loading results...</p>");
    
    console.log("Loading individual results for student:", student, "company:", company); // Debug log

    frappe.call({
        method: "education.academic_management.page.consolidated_academi.consolidated_academi.get_results",
        args: { 
            student: student, 
            company: company 
        },
        callback: function(r) {
            console.log("Response received:", r); // Debug log
            
            // Check for server messages (errors)
            if (r.message && r.message._server_messages) {
                try {
                    let messages = JSON.parse(r.message._server_messages);
                    if (messages && messages.length) {
                        container.html(`<b>Error: ${messages[0]}</b>`);
                        return;
                    }
                } catch(e) {
                    console.log("Error parsing server messages:", e);
                }
            }
            
            // Check if we have valid data
            if (!r.message) {
                container.html("<b>Error: No response from server</b>");
                return;
            }
            
            if (!r.message.results) {
                container.html("<b>Error: Invalid response structure from server</b>");
                console.log("Invalid response:", r.message);
                return;
            }
            
            if (!r.message.results.length) {
                container.html(`<b>No results found for student ${student} under ${company}</b>`);
                return;
            }

            let data = r.message.results;
            let student_name = r.message.student || student;

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
                        margin-bottom: 20px;
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
                    .student-header {
                        margin-bottom: 20px;
                        padding: 10px;
                        background-color: #f5f5f5;
                        border-left: 4px solid #2490ef;
                    }
                </style>

                <div class="student-header">
                    <strong>College:</strong> ${company}<br>
                    <strong>Student:</strong> ${student_name} (${student})<br>
                </div>

                <h3>Semester Result</h3>

                <table>
                    <thead>
                        <tr>
                            <th>Semester</th>
                            <th>Module</th>
                            <th>Year of Passing</th>
                            <th>Max. Marks</th>
                            <th>Marks Secured</th>
                            <th>Credit</th>
                            <th>Weighting</th>
                            <th>Remarks</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            // Sort semesters
            Object.keys(grouped).sort().forEach(semester => {
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

                    if (index === 0) {
                        html += `<td class="semester-cell" rowspan="${rows.length}">${semester}</td>`;
                    }

                    html += `
                        <td>${d.module}</td>
                        <td>${d.year_of_passing}</td>
                        <td>100</td>
                        <td>${d.total}</td>
                        <td>${d.credit || ""}</td>
                    `;

                    if (index === 0) {
                        html += `
                            <td rowspan="${rows.length}">${semester_weightage}</td>
                            <td rowspan="${rows.length}">${remarks}</td>
                        `;
                    }

                    html += `</tr>`;
                });

                html += `
                    <tr class="total-row">
                        <td colspan="2"><strong>Total</strong></td>
                        <td>
                        <td><strong>${max_total}</strong></td>
                        <td><strong>${total_marks}</strong></td>
                        <td><strong>${total_credit}</strong></td>
                        <td><strong>${weighted_score}</strong></td>
                        <td>
                    </tr>
                `;
            });

            html += `</tbody>
            </table>`;
            container.html(html);
        },
        error: function(err) {
            console.error("Error in frappe.call:", err);
            container.html(`<b>Error loading results: ${err.message || "Unknown error"}</b>`);
        }
    });
}

function load_results_bulk(container, filters, title) {
    container.html(`<p>Loading results for ${title}...</p>`);
    
    frappe.call({
        method: "education.academic_management.page.consolidated_academi.consolidated_academi.get_results",
        args: filters,
        callback: function(r) {
            if (!r.message || !r.message.students || !r.message.students.length) {
                container.html(`<b>No data found for ${title}</b>`);
                return;
            }
            
            let students = r.message.students;
            // let html = `
            //     <style>
            //         table {
            //             border-collapse: collapse;
            //             width: 100%;
            //             font-size: 13px;
            //             margin-bottom: 20px;
            //         }
            //         th, td {
            //             border: 1px solid #555;
            //             padding: 6px;
            //             text-align: center;
            //         }
            //         th {
            //             background-color: #f2f2f2;
            //         }
            //         .semester-cell {
            //             font-weight: bold;
            //             background-color: #fafafa;
            //         }
            //         .total-row {
            //             font-weight: bold;
            //             background-color: #f9f9f9;
            //         }
            //         .student-section {
            //             margin-bottom: 50px;
            //             page-break-after: always;
            //         }
            //         .student-header {
            //             margin-bottom: 20px;
            //             padding: 10px;
            //             background-color: #f5f5f5;
            //             border-left: 4px solid #2490ef;
            //         }
            //         h3 {
            //             color: #2490ef;
            //             margin-top: 0;
            //         }
            //     </style>
                
            //     <h2>Academic Transcripts: ${title}</h2>
            //     <p></p>
            //     <p>Total Students: ${students.length}</p>
            // `;
            let html = `
                    <style>
                        table {
                            border-collapse: collapse;
                            width: 100%;
                            font-size: 13px;
                            margin-bottom: 20px;
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
                        .student-section {
                            margin-bottom: 30px;
                            page-break-inside: avoid; /* Keep table together */
                        }
                        .student-header {
                            margin-bottom: 20px;
                            padding: 10px;
                            background-color: #f5f5f5;
                            border-left: 4px solid #2490ef;
                        }
                        h3 {
                            color: #2490ef;
                            margin-top: 0;
                        }
                        
                        /* Print styles to prevent page breaks inside tables */
                        @media print {
                            .student-section {
                                page-break-inside: avoid;
                                page-break-after: avoid;
                            }
                            table {
                                page-break-inside: avoid;
                            }
                            tr {
                                page-break-inside: avoid;
                            }
                            .student-section:last-child {
                                page-break-after: avoid;
                            }
                        }
                    </style>
                    
                    <h2>Academic Transcripts: ${title}</h2>
                    <p></p>
                    <p>Total Students: ${students.length}</p>
                `;
            
            students.forEach((student, idx) => {
                html += `<div class="student-section">
                            <div class="student-header">
                                <strong>Student:</strong> ${student.student_name || student.student} <br>
                            </div>`;
                
                if (student.results && student.results.length) {
                    // Group by semester (same as individual view)
                    let grouped = {};
                    student.results.forEach(d => {
                        if (!grouped[d.semester]) {
                            grouped[d.semester] = [];
                        }
                        grouped[d.semester].push(d);
                    });
                    
                    html += `<h3>Semester Result</h3>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Semester</th>
                                        <th>Module</th>
                                        <th>Year of Passing</th>
                                        <th>Max. Marks</th>
                                        <th>Marks Secured</th>
                                        <th>Credit</th>
                                        <th>Weighting</th>
                                        <th>Remarks</th>
                                    </tr>
                                </thead>
                                <tbody>`;
                    
                    Object.keys(grouped).forEach(semester => {
                        let rows = grouped[semester];
                        
                        let total_marks = 0;
                        let total_credit = 0;
                        let max_total = rows.length * 100;
                        
                        rows.forEach(d => {
                            total_marks += Number(d.total) || 0;
                            total_credit += Number(d.credit) || 0;
                        });
                        
                        let percentage = max_total > 0 ? (total_marks / max_total) * 100 : 0;
                        let semester_weightage = Number(rows[0].weighting) || 0;
                        let weighted_score = max_total > 0 ? ((total_marks / max_total) * semester_weightage).toFixed(2) : 0;
                        let remarks = percentage >= 50 ? "Pass" : "Fail";
                        
                        rows.forEach((d, index) => {
                            html += `<tr>`;
                            
                            if (index === 0) {
                                html += `<td class="semester-cell" rowspan="${rows.length}">${semester}</td>`;
                            }
                            
                            html += `
                                <td>${d.module}</td>
                                <td>${d.year_of_passing}</td>
                                <td>100</td>
                                <td>${d.total}</td>
                                <td>${d.credit || ""}</td>
                            `;
                            
                            if (index === 0) {
                                html += `
                                    <td rowspan="${rows.length}">${semester_weightage}</td>
                                    <td rowspan="${rows.length}">${remarks}</td>
                                `;
                            }
                            
                            html += `</tr>`;
                        });
                        
                        html += `
                            <tr class="total-row">
                                <td colspan="2">Total</td>
                                <td></td>
                                <td>${max_total}</td>
                                <td>${total_marks}</td>
                                <td>${total_credit}</td>
                                <td>${weighted_score}</td>
                                <td></td>
                            </tr>
                        `;
                    });
                    
                    html += `</tbody></table>`;
                } else {
                    html += `<p><i>No results found for this student</i></p>`;
                }
                
                html += `</div>`;
                if (idx < students.length - 1) {
                    html += `<div style="page-break-after: always;"></div>`;
                }
            });
            
            container.html(html);
        }
    });
}


function printSemesterResult(container){
    let content = container.html(); // get timetable HTML
    
    // First, fetch the header image
    frappe.call({
        method: "education.academic_management.page.semester_result_decl.semester_result_decl.get_header",
        callback: function(r) {
            let headerImage = r.message || '';
            
            // Now create the print window with the image
            let myWindow = window.open('', '', 'width=1000,height=800');
            myWindow.document.write('<html><head><title>Print Semester Result</title>');
            
            // Include all styles with full width header
            myWindow.document.write(`
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: Arial, sans-serif;
                    padding: 0;
                    margin: 0;
                    background: #fff;
                }
                .print-container {
                    max-width: 100%;
                    margin: 0 auto;
                }
                .header-container {
                    width: 100%;
                    background: #fff;
                    text-align: center;
                    padding: 0;
                    margin: 0;
                    line-height: 0;
                }
                .header-container img {
                    width: 100%;
                    height: auto;
                    display: block;
                    margin: 0;
                }
                .content-container {
                    padding: 20px 20px 20px 20px;
                }
                table {
                    border: 1px solid rgb(56, 56, 56);
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 12px;
                }
                th, td {
                    border: 1px solid rgb(56, 56, 56);
                    padding: 5px;
                    text-align: center;
                }
                thead tr {
                    background-color: #f3f3f3;
                }
                tbody tr {
                    background-color: #ffffff;
                }
                .pass {
                    color: green;
                    font-weight: bold;
                }
                .fail {
                    color: red;
                    font-weight: bold;
                }
                h3 {
                    text-align: center;
                    margin: 20px 0 10px 0;
                }

                /* Make it print-friendly */
                @media print {
                    body { 
                        margin: 0; 
                        padding: 0;
                    }
                    .print-container {
                        padding: 0;
                    }
                    .header-container {
                        padding: 0;
                        margin: 0;
                    }
                    .header-container img {
                        width: 100%;
                        height: auto;
                        display: block;
                    }
                    .content-container {
                        padding: 10px 20px 20px 20px;
                    }
                    table { 
                        page-break-inside: auto; 
                    }
                    tr { 
                        page-break-inside: avoid; 
                        page-break-after: auto; 
                    }
                    th, td {
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }
                }
            </style>`);

            myWindow.document.write('</head><body>');
            
            myWindow.document.write('<div class="print-container">');
            
            // Add header image if available - full width
            if (headerImage) {
                myWindow.document.write(`
                    <div class="header-container">
                        <img src="${headerImage}" alt="Letter Head" />
                    </div>
                `);
            }
            
            // Add the content with padding
            myWindow.document.write('<div class="content-container">');
            myWindow.document.write(content);
            myWindow.document.write('</div>');
            
            myWindow.document.write('</div>'); // Close print-container
            
            myWindow.document.write('</body></html>');

            myWindow.document.close();
            myWindow.focus();
            
            // Wait for image to load, then print
            setTimeout(function() {
                myWindow.print();
                myWindow.close();
            }, 500);
        },
        error: function(err) {
            console.error("Error fetching header:", err);
            // Print without header if error
            let myWindow = window.open('', '', 'width=1000,height=800');
            myWindow.document.write('<html><head><title>Print Semester Result</title>');
            myWindow.document.write(`
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: Arial, sans-serif;
                    padding: 0;
                    margin: 0;
                }
                .print-container {
                    padding: 20px;
                    max-width: 100%;
                }
                table {
                    border: 1px solid rgb(56, 56, 56);
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid rgb(56, 56, 56);
                    padding: 5px;
                    text-align: center;
                }
                thead tr {
                    background-color: #f3f3f3;
                }
                tbody tr {
                    background-color: #ffffff;
                }
                .pass {
                    color: green;
                    font-weight: bold;
                }
                .fail {
                    color: red;
                    font-weight: bold;
                }
                h3 {
                    text-align: center;
                    margin: 20px 0;
                }
                @media print {
                    body { margin: 0; padding: 0; }
                    .print-container { padding: 0; }
                    table { page-break-inside: auto; }
                    tr { page-break-inside: avoid; page-break-after: auto; }
                    th, td {
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }
                }
            </style>`);
            myWindow.document.write('</head><body>');
            myWindow.document.write('<div class="print-container">');
            myWindow.document.write(content);
            myWindow.document.write('</div>');
            myWindow.document.write('</body></html>');
            myWindow.document.close();
            myWindow.focus();
            myWindow.print();
            myWindow.close();
        }
    });
}
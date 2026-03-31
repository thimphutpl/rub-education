frappe.pages['semester-result-decl'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Semester Result Declaration',
		single_column: true
	});

	// Create a container for the print button and table
	let topContainer = $('<div class="timetable-top-container"></div>').appendTo(page.body);

	// 🔹 Add Print Button at the top
	// let printBtn = $('<button class="btn btn-primary" style="margin-bottom:10px;">Print Timetable</button>')
	// 	.appendTo(topContainer)
	// 	.click(function(){
	// 		printTimetable(container);
	// 	});
    // 🔹 Custom fields container (flex layout)
    let fieldContainer = $(`
        <div class="custom-fields-container" 
             style="display:flex; flex-wrap:wrap; gap:20px; margin-bottom:10px;">
        </div>
    `).appendTo(topContainer);
	// let container = $('<div class="timetable-container"></div>').appendTo(page.body);
	// Table container
	let container = $('<div class="timetable-container"></div>').appendTo(topContainer);
	// Add Print Button
	let college = frappe.ui.form.make_control({
        df: {
            fieldname: 'college',
            label: 'College',
            fieldtype: 'Link', // Text field
			options:"Company",
            placeholder: 'Select College', // Text field
            reqd: 1
        },
        parent: fieldContainer,
        render_input: true
    });
	college.refresh(); // render the field
	let programme = frappe.ui.form.make_control({
        parent: fieldContainer,
        df: {
            label: 'Programme',
            fieldname: 'programme',
            fieldtype: 'Link',
			options: 'Programme',
            placeholder: 'Select Programme', // Text field

        },
        render_input: true
    });
    programme.refresh();
	let academic_term = frappe.ui.form.make_control({
        parent: fieldContainer,
        df: {
            label: 'Academic Term',
            fieldname: 'academic_term',
            fieldtype: 'Link',
			options: 'Academic Term',
            placeholder: 'Select Academic Term', // Text field

        },
        render_input: true
    });
	academic_term.refresh();
	let student_section = frappe.ui.form.make_control({
        parent: fieldContainer,
        df: {
            label: 'Student Section',
            fieldname: 'student_section',
            fieldtype: 'Link',
			options: 'Student Section',
            placeholder: 'Select Student Section', // Text field

        },
        render_input: true
    });
	student_section.refresh()
   
	function checkAndLoad() {
		if(college.get_value() && programme.get_value() && academic_term.get_value() && student_section.get_value()){
			load_results(
				container,
				college.get_value(),
				programme.get_value(),
				academic_term.get_value(),
				student_section.get_value()
			);
		}
		else{
			container.empty();
			container.html("<b>Please select all the fields</b>")
		}
	}
    [college, programme, academic_term,student_section].forEach(f => {
        f.df.onchange = checkAndLoad;
    });

}

function load_results(container, college, programme, academic_term, student_section) {
    container.html("<p>Loading results...</p>");

    frappe.call({
        method: "education.academic_management.page.semester_result_decl.semester_result_decl.get_results",
        args: {
            college,
            programme,
            academic_term,
            student_section
        },
        callback: function(r) {
            if (!r.message) {
                container.html("<b>No data found</b>");
                return;
            }

            let data = r.message;
            console.log(data)

            // 🔹 Build table with two-row header
            let html = `
            <style>
                table, th, td {
                    border: 1px solid rgb(56, 56, 56);
                    border-collapse: collapse;
                }
                th, td {
                    padding: 5px;
                    text-align: center;
                    width: 47px;
                }
                thead tr {
                    background-color: #f3f3f3;
                }
            
                /* Student rows */
                tbody tr {
                    background-color: #ffffff;
                }
            </style>

            <h3>Semester Result</h3>
            <table>
                <thead>
                    <tr>   
                        <th rowspan="2" style="width:120px;">Student No</th>
                        <th rowspan="2" style="width:130px;">Name</th>
                        ${data.modules.map(m => `<th colspan="3">${m}</th>`).join("")}
                        <th rowspan="2">Total CV</th>
                        <th rowspan="2">Percentage Achieved</th>
                    </tr>
                    <tr>
                        ${data.modules.map(m => `<th>CA</th><th>SE</th><th>TL</th>`).join("")}
                    </tr>
                </thead>
                <tbody>
            `;

            // 🔹 Student data rows
            // data.students.forEach(stu => {
            //     html += `<tr>
            //                 <td>${stu.student_no}</td>
            //                 <td>${stu.student_name}</td>`;

            //     data.modules.forEach(m => {
            //         let res = stu.results[m] || {ca:'', se:'', tl:''};
            //         html += `<td>${res.ca}</td><td>${res.se}</td><td>${res.tl}</td>`;
            //     });

            //     html += `</tr>`;
            // });

            data.students.forEach(stu => {
                let total_cv = 0;           // Sum of TL across modules
                let max_total = data.modules.length * 100; // Each module = 100
            
                html += `<tr>
                            <td>${stu.student_no}</td>
                            <td>${stu.student_name}</td>`;
            
                data.modules.forEach(m => {
                    let res = stu.results[m] || {ca: 0, se: 0, tl: 0};
                    html += `<td>${res.ca}</td><td>${res.se}</td><td>${res.tl}</td>`;
            
                    // Add TL to total_cv
                    total_cv += Number(res.tl) || 0;
                });
            
                // Percentage calculation
                let percentage = max_total > 0 ? ((total_cv / max_total) * 100).toFixed(2) : 0;
            
                // Add new columns at the end
                html += `<td>${total_cv}</td><td>${percentage}%</td>`;
            
                html += `</tr>`;
            });

            html += `
                </tbody>
            </table>
            `;

            container.html(html);
        }
    });
}
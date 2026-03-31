frappe.pages['timetable'].on_page_load = function(wrapper) {

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Timetable',
		single_column: true
	});
	// Create a container for the print button and table
	let topContainer = $('<div class="timetable-top-container"></div>').appendTo(page.body);

	// 🔹 Add Print Button at the top
	let printBtn = $('<button class="btn btn-primary" style="margin-bottom:10px;">Print Timetable</button>')
		.appendTo(topContainer)
		.click(function(){
			printTimetable(container);
		});
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
	function checkAndLoad() {
		if(college.get_value() && programme.get_value() && academic_term.get_value()){
			load_timetable(container, college.get_value(), programme.get_value(), academic_term.get_value());
		}
		else{
			container.empty();
			container.html("<b>Please select all the fields</b>")
		}
	}
    [college, programme, academic_term].forEach(f => {
        f.df.onchange = checkAndLoad;
    });

	// 🔹 Apply company logo as background dynamically

};


function load_timetable(container, college, programme, academic_term){
	frappe.call({
		method: "education.academic_management.page.timetable.timetable.get_timetable",
		args: {"college": college, "programme": programme, "academic_term": academic_term},
		callback: function(r){

			let data = r.message.timetable || [];
			let blocked = r.message.blocked || [];

			// Create a map for fast lookup
			let map = {};
			if(data.length > 0){
			data.forEach(d=>{
				let time = moment(d.from_time,"HH:mm:ss").format("HH:mm");
				map[`${d.day}_${time}`] = d;
			});

			// Pass map to the draw function
				draw_timetable(container, data, blocked, map);
			}
			else{
				container.empty();
				container.html("<b>No Timetable Generated</b>")

			}
			// let company_name = "College of Language and Culture Studies"; // get default company ***for now its static. Need to fetch company/college from logged in user
			// frappe.db.get_value("Company", company_name, ["logo"], function(r){
			// 	let logo_url = r.logo; // full URL of the company logo
			// 	applyLogoBackground(logo_url, container); // function that adds logo div behind timetable
			// });
		}
	})

}


function draw_timetable(container, data, blocked, map){

	const days = ["Monday","Tuesday","Wednesday","Thursday","Friday"];

	let slots = generate_slots();
	slots.sort();

	let table = $('<table class="table table-bordered timetable-table"></table>');

	// Header row (Time Slots)
	let header = "<tr><th>Day</th>";
	slots.forEach(slot=>{
		// header += `<th>${slot}</th>`;
		header += `<th>${moment(slot,"HH:mm").format("hh:mm A")}</th>`;
	});
	header += "</tr>";
	table.append(header);

	// Rows for each day
	days.forEach(day=>{

		let row = `<tr><td class="day-column"><b>${day}</b></td>`;

		slots.forEach(slot=>{

			let entry = map[`${day}_${slot}`];
		
			// Check if this slot is a blocked/non-academic period
			let blockedSlot = blocked.find(b => {
				return b.day === day && moment(slot,"HH:mm").isBetween(
					moment(b.from_time,"HH:mm:ss").subtract(1,'seconds'),
					moment(b.to_time,"HH:mm:ss")
				);
			});
		
			if(entry){
				row += `
				<td class="tt-cell">
					<div class="module">${entry.module_code}</div>
					<div class="tutor">(${entry.class_type})</div>
					<div class="tutor">${entry.tutor_name}</div>
					<div class="tutor">Room: ${entry.room_name}</div>
				</td>`;
			}else if(blockedSlot){
				row += `<td class="tt-break">${blockedSlot.period_name}</td>`;
			}else{
				row += "<td></td>";
			}
		
		});

		row += "</tr>";
		table.append(row);

	});

	container.html(table);

}

function convertTo12Hour(time24) {
    let [hours, minutes] = time24.split(":");
    hours = parseInt(hours);
    let ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12;
    if(hours === 0) hours = 12;
    return `${hours.toString().padStart(2,'0')}:${minutes} ${ampm}`;
}

// function applyLogoBackground(logo_url, container){
//     if(!logo_url) return;

//     // // Remove previous logo if exists
//     // container.find(".timetable-table").remove();
//     if (logo_url && !logo_url.startsWith("http")) {
//         logo_url = "https://rub.thimphutechpark.bt" + logo_url;
//     }
//     container.css({"position":"relative"}); // ensure relative positioning
//     container.prepend('<div class="timetable-logo-bg"></div>');

//     container.find(".timetable-table").css({
//         "position": "absolute",
//         "top": 0,
//         "left": 0,
//         "width": "100%",
//         "height": "100%",
//         "background-image": `url(${logo_url})`,
//         "background-repeat": "no-repeat",
//         "background-position": "center",
//         "background-size": "200px auto",
//         "opacity": "0.1",
//         "z-index": 0
//     });

//     // Bring table to front
//     container.find(".timetable-table").css({"position":"relative","z-index":1});
// }
function applyLogoBackground(logo_url, container){
    if(!logo_url) return;
    if (logo_url && !logo_url.startsWith("http")) {
        logo_url = "https://rub.thimphutechpark.bt" + logo_url;
    }
    let table = container.find(".timetable-table");

    table.css({
        "position": "relative",
        "background-image": `url(${logo_url})`,
        "background-repeat": "no-repeat",
        "background-position": "center",
        "background-size": "300px auto"
    });
}
function generate_slots(){

	let start = moment("09:00","HH:mm");
	let end = moment("17:00","HH:mm");

	let slots = [];

	while(start <= end){  // < instead of <= to avoid duplicate last slot
		slots.push(start.format("HH:mm"));
		start.add(1,"hour");
	}

	return slots;
}

function printTimetable(container){
    let content = container.html(); // get timetable HTML

    let myWindow = window.open('', '', 'width=1000,height=800');
    myWindow.document.write('<html><head><title>Print Timetable</title>');

    // Include all styles
    myWindow.document.write(`
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .timetable-table{
            font-size:12px;
            text-align:center;
            border-collapse: collapse;
            width: 100%;
            table-layout: fixed; /* important for fixed-width cells */
        }
        .timetable-table th, .timetable-table td{
            border:1px solid #ccc;
            word-wrap: break-word;
            white-space: normal; /* allow wrapping */
            padding: 5px;
        }
        .tt-cell{
            background:#e6f7ff; /* academic */
            font-weight:bold;
        }
        .tt-break{
            background:#f3f3f3; /* non-academic */
            color:#666;
            font-weight:bold;
        }
        .day-column{
            background:#dff0d8; /* days column */
            font-weight:bold;
        }

        /* Make it print-friendly */
        @media print {
            body { margin:0; }
            .timetable-table { page-break-inside: auto; }
            .timetable-table tr { page-break-inside: avoid; page-break-after: auto; }
			* {
				-webkit-print-color-adjust: exact !important; /* Chrome/Safari */
				print-color-adjust: exact !important;       /* Firefox */
			}
        }
    </style>`);

    myWindow.document.write('</head><body>');
    myWindow.document.write(content);
    myWindow.document.write('</body></html>');

    myWindow.document.close();
    myWindow.focus();
    myWindow.print();
    myWindow.close();
}

$(`<style>
	.timetable-table{
		font-size:13px;
		text-align:center;
		border-collapse: collapse;
	}
	
	.timetable-table th,
	.timetable-table td{
		border:1px solid #ccc;
		width:120px;       /* fixed width */
		min-width:120px;
		max-width:120px;
		height:50px;       /* min height */
		vertical-align: middle;
		word-wrap: break-word;   /* wrap text */
		white-space: normal;     /* allow multiple lines */
	}
	.timetable-table th{
		background:#E6E6E6; /* academic class color */
		font-weight:bold;
	}
	.tt-cell{
		background:#e6f7ff; /* academic class color */
		font-weight:bold;
	}
	.day-column {
    background: #dff0d8; /* light green */
    font-weight: bold;
    color: #333;
    text-align: center;
}
	.tt-break{
		background:#f3f3f3;
		color:#666;
		font-weight:bold;
	}
	
	.module{
		font-weight:bold;
	}
	
	.tutor{
		color:#666;
	}
	
	.room{
		color:#999;
	}
	
	</style>`).appendTo("head");
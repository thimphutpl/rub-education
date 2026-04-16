frappe.pages['tutor-dashboard'].on_page_load = function(wrapper) {

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Tutor Dashboard',
		single_column: true
	});
	let layout = $(`
		<div class="timetable-layout" style="display:flex; gap:20px;">
			<div class="timetable-sidebar"></div>
			<div class="timetable-main" style="flex:1;"></div>
		</div>
	`).appendTo(page.body);
	
	// Sidebar & Main references
	let sidebar = layout.find(".timetable-sidebar");
	let main = layout.find(".timetable-main");
	// Create a container for the print button and table
	let topContainer = $('<div class="timetable-top-container"></div>').appendTo(main);
	sidebar.html(`
		<div class="sidebar-card user-profile-card" style="text-align:center;">
        <img id="user-profile-pic" src="/assets/frappe/images/ui/avatar.png" 
             style="width:60px; height:60px; border-radius:50%; margin-bottom:10px;">
        <div id="user-fullname" style="font-weight:bold;"></div>
        <div id="user-email" style="font-size:12px; color:#666;"></div>
		</div>
		<div class="sidebar-card">
			<h4 id="realtime-date" style="font-size:14px; margin-bottom:5px;"></h4>
			<div id="realtime-clock" style="font-size:16px; font-weight:bold;"></div>
		</div>
		<div class="sidebar-card">
			<h4>Tutor Profile</h4>
			<div id="user-college" style="font-weight:bold;"></div>
			<div id="user-programme" style="font-size:12px; color:#666;"></div>
		</div>
	
		<div class="sidebar-card">
			<h4>Legend</h4>
			<div><span class="legend-box academic"></span> Academic</div>
			<div><span class="legend-box break"></span> Break</div>
		</div>
	`);
	function startClock() {
		function updateClock() {
			let now = new Date();
	
			// Format date as: Day, DD Month YYYY
			let options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
			let dateString = now.toLocaleDateString(undefined, options);
			$('#realtime-date').text(dateString);
	
			// Format time as: hh:mm:ss AM/PM
			let hours = now.getHours();
			let minutes = now.getMinutes();
			let seconds = now.getSeconds();
			let ampm = hours >= 12 ? 'PM' : 'AM';
			hours = hours % 12;
			if (hours === 0) hours = 12;
			let h = hours.toString().padStart(2, '0');
			let m = minutes.toString().padStart(2, '0');
			let s = seconds.toString().padStart(2, '0');
			let timeString = `${h}:${m}:${s} ${ampm}`;
			$('#realtime-clock').text(timeString);
		}
	
		updateClock(); // initial call
		setInterval(updateClock, 1000);
	}
	
	// Start the clock
	startClock();
	// frappe.call({
	// 	method:"education.academic_management.page.student_dashboard.student_dashboard.get_student_details",
	// 	args: {"user": frappe.session.user},
	// 	callback: function(r){

	// 	}
	// })
	(async () => {

		let r = await frappe.db.get_value("Employee",
			{"user_id": frappe.session.user},
			["company", "programme"]
		);
	
		if (r.message && r.message.company) {
	
			let college_val = r.message.company;
			let programme_val = r.message.programme;
	
			$('#user-college').text(college_val);
			$('#user-programme').text(programme_val);
	
		}
	
	})();
	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "User",
			name: frappe.session.user
		},
		callback: function(r) {
			if (r.message) {
				let user = r.message;
				// Use first_name + last_name if full_name is empty
				let fullname = user.full_name
	
				$('#user-fullname').text(fullname);
				$('#user-email').text(user.email);
	
				if (user.user_image) {
					$('#user-profile-pic').attr('src', user.user_image).show();
					$('#user-initials').remove();
				} else {
					let initials = fullname
						.split(" ")
						.map(n => n[0])
						.join("")
						.toUpperCase()
						.substring(0, 2);
	
					$('#user-profile-pic').hide();
					$('#user-initials').remove();
					$(`<div id="user-initials">${initials}</div>`).css({
						width: "60px",
						height: "60px",
						"border-radius": "50%",
						background: "#6c757d",
						color: "#fff",
						display: "flex",
						"align-items": "center",
						"justify-content": "center",
						"font-weight": "bold",
						"font-size": "20px",
						margin: "0 auto 10px auto"
					}).insertBefore('#user-fullname');
				}
			}
		}
	});
	// if(frappe.db.exists("Student", filters={"user":frappe.session.user})==true){

		// frappe.call({
		// 	method: "frappe.client.get",
		// 	args: {
		// 		doctype: "Student",
		// 		filters: {"user":frappe.session.user},
		// 		field_name: ["company", "programme"]
		// 	},
		// 	callback: function(r) {
		// 		if(r.message) {
		// 			let student = r.message;
		// 			let college = student.company
		// 			let programme = student.programme;
	
		// 			$('#user-college').text(college);
		// 			$('#user-programme').text(programme);
		// 		}
		// 	}
		// });
	// }

	// 🔹 Add Print Button at the top
	// let printBtn = $('<button class="btn btn-primary" style="margin-bottom:10px;">Print Timetable</button>')
	// 	.appendTo(topContainer)
	// 	.click(function(){
	// 		printTimetable(container);
	// 	});
	let collapsible = $(`
		<div class="timetable-collapsible">
			<div class="timetable-header" style="cursor:pointer; font-weight:bold; padding:8px; background:#f0f0f0; border-radius:6px;">
				▶ Academic Timetable
			</div>
			<div class="timetable-body" style="display:none; margin-top:10px;"></div>
		</div>
	`).appendTo(topContainer);
	let container = collapsible.find(".timetable-body");
	renderFilters(container);
	let printBtn = $('<button class="btn btn-primary" style="margin-bottom:10px;">Print Timetable</button>')
    .prependTo(container)   // 🔥 move inside collapsible
    .click(function(){
        printTimetable(container);
    });
    // 🔹 Custom fields container (flex layout)
    // let fieldContainer = $(`
    //     <div class="custom-fields-container" 
    //          style="display:flex; flex-wrap:wrap; gap:20px; margin-bottom:10px;">
    //     </div>
    // `).appendTo(topContainer);
	// let fieldContainer = $(`
	// 	<div class="custom-fields-container" 
	// 		 style="display:flex; flex-wrap:wrap; gap:20px; margin-bottom:10px;">
	// 	</div>
	// `).prependTo(container);
	// let container = $('<div class="timetable-container"></div>').appendTo(page.body);
	// Table container

	
	// collapsible.find(".timetable-header").click(function(){
	// 	let body = collapsible.find(".timetable-body");
	// 	let isVisible = body.is(":visible");
	
	// 	body.slideToggle(200);
	
	// 	$(this).text(isVisible ? "▶ Timetable" : "▼ Timetable");
	// });
	collapsible.find(".timetable-body").show();
	collapsible.find(".timetable-header").text("▼Academic Timetable");
	collapsible.find(".timetable-header").click(function(){
		let body = collapsible.find(".timetable-body");
		let isVisible = body.is(":visible");
	
		body.slideToggle(200);
		$(this).text(isVisible ? "▶ Academic Timetable" : "▼ Academic Timetable");
	
		// ✅ Prevent duplicate rendering
		if (body.find(".custom-fields-container").length === 0) {
			renderFilters(body);
		}
	});

	function renderFilters(container) {

		let fieldContainer = $(`
			<div class="custom-fields-container"
				 style="display:flex; flex-wrap:wrap; gap:20px; margin-bottom:10px;">
			</div>
		`).appendTo(container);
		
		// ✅ NEW: separate table container
		let tableContainer = $('<div class="timetable-table-container"></div>').appendTo(container);
	
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
		let college_val = ""
		let programme_val = ""
		let current_at = ""
		frappe.call({
			method:"education.academic_management.page.student_dashboard.student_dashboard.get_student_details",
			args: {"user": frappe.session.user},
			async: false,
			callback: function(r){
				if(r.message){
					college_val = r.message[0]
					programme_val = r.message[1]
					current_at = r.message[2]
				}
			}
		})
		// let r = await frappe.db.get_value("Student",
		// 	{"user": frappe.session.user},
		// 	["company", "programme"]
		// );
	
		// if (r.message && r.message.company) {
	
		// 	let college_val = r.message.company;
		// 	let programme_val = r.message.programme;
	
		// 	college.set_value(college_val);
		// 	programme.set_value(programme_val);
		// }
		Promise.all([
			college.set_value(college_val),
			programme.set_value(programme_val),
			academic_term.set_value(current_at)
		]).then(() => {
			checkAndLoad();   // 🔥 runs AFTER values are actually set
		});

		function checkAndLoad() {
			if (college.get_value() && programme.get_value() && academic_term.get_value()) {
				load_timetable(
					tableContainer,   // ✅ ONLY update table area
					college.get_value(),
					programme.get_value(),
					academic_term.get_value()
				);
			} else {
				tableContainer.html("<b>Please select all the fields</b>");
			}
		}
		[college, programme, academic_term].forEach(f => {
			f.$input.on("change", checkAndLoad);
		});

	}

	// 🔹 Apply company logo as background dynamically

};
// function get_student_details(){
// 	frappe.call({
// 		method: "education.academic_management.page.student_dashboard.student_dashboard.get_student_details",
// 		args: {"user": frappe.session.user},
// 		callback: function(r){

// 			let data = r.message.timetable || [];
// 			let blocked = r.message.blocked || [];

// 			// Create a map for fast lookup
// 			let map = {};
// 			if(data.length > 0){
// 			data.forEach(d=>{
// 				let time = moment(d.from_time,"HH:mm:ss").format("HH:mm");
// 				map[`${d.day}_${time}`] = d;
// 			});

// 			// Pass map to the draw function
// 				draw_timetable(container, data, blocked, map);
// 			}
// 			else{
// 				container.empty();
// 				container.html("<b>No Timetable Generated</b>")

// 			}
// 			// let company_name = "College of Language and Culture Studies"; // get default company ***for now its static. Need to fetch company/college from logged in user
// 			// frappe.db.get_value("Company", company_name, ["logo"], function(r){
// 			// 	let logo_url = r.logo; // full URL of the company logo
// 			// 	applyLogoBackground(logo_url, container); // function that adds logo div behind timetable
// 			// });
// 		}
// 	})


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
	let tableWrapper = $('<div class="timetable-print-only"></div>');
	tableWrapper.append(table);
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
	container.html(tableWrapper);

	// container.html(table);

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
    // let content = container.html(); // get timetable HTML
	let content = container.find('.timetable-print-only').html();

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
		font-size:9px;
		text-align:center;
		border-collapse: collapse;
	}
	.timetable-container td,
	.timetable-container th {
		padding: 4px 6px;   /* reduce spacing */
		font-size: 12px;    /* optional */
	}
	.timetable-table th,
	.timetable-table td{
		border:1px solid #ccc;
		width:80px;       /* fixed width */
		min-width:100px;
		max-width:100px;
		padding:3px;
		height:45px;
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
	.user-profile-card img {
		border: 2px solid #ddd;
	}
	.user-profile-card {
		padding: 15px;
		background: #fff;
		border-radius: 8px;
		box-shadow: 0 1px 3px rgba(0,0,0,0.1);
		margin-bottom: 15px;
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
	.timetable-sidebar{
    width:250px;
    background:#f8f9fa;
    border:1px solid #ddd;
    border-radius:8px;
    padding:15px;
	flex-shrink: 0;   /* 🔥 prevents shrinking */
	
    height:fit-content;
}
.layout-main-section {
    padding-left: 5px !important;   /* reduce left gap */
    padding-right: 5px !important;
}
	.page-content {
	max-width: 100% !important;
    padding-left: 0 !important;
    margin-left: 0 !important;
}
.sidebar-card{
    margin-bottom:15px;
    padding:10px;
    background:#fff;
    border-radius:6px;
    box-shadow:0 1px 3px rgba(0,0,0,0.1);
}

.legend-box{
    display:inline-block;
    width:12px;
    height:12px;
    margin-right:5px;
}

.legend-box.academic{ background:#e6f7ff; }
.legend-box.break{ background:#f3f3f3; }
	</style>`).appendTo("head");
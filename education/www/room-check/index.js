frappe.ready(function () {
    // 1️⃣ Populate college dropdown
    frappe.call({
        method: "education.www.room-check.index.get_college",
        callback: function (r) {
            if (r.message && r.message.college) {
                const select = document.getElementById("college");
                r.message.college.forEach(function (c) {
                    const option = document.createElement("option");
                    option.value = c.name;
                    option.text = c.name;
                    select.appendChild(option);
                });
            }
        }
    });

    // // 2️⃣ Load all events initially
    // getEventsInfo();

    // 3️⃣ Handle search by college
    document.getElementById("searchForm").addEventListener("submit", function (e) {
        e.preventDefault();
        const college = document.getElementById("college").value;
        roomInfo(college);
    });
});

function roomInfo(college = '') {
    frappe.call({
        method: "education.www.room-check.index.get_room_info",
        args: { college: college },
        callback: function (r) {
            const container = document.getElementById("room-list");
            container.innerHTML = '';
            container.style.display = "flex";           // override grid
            container.style.justifyContent = "center";  // horizontal center
            container.style.alignItems = "center";

            if (!r.message || !r.message.room_info || r.message.room_info.length === 0) {
                container.innerHTML = `

            <div class="alertcontainer">     
            <div class="alert alert-info text-center">
                <p>No Room records found</p>
            </div>
            </div>
       `;
                return;
            }

            displayRoomInfo(r.message.room_info);
        }
    });
}

function displayRoomInfo(room_info) {
    const container = document.getElementById("room-list");
    let html = '';

    room_info.forEach(c => {

        let statusColor = c.status === "Available" ? "green" : "red";
        // let clickAction = c.status === "Available" ? `onclick="bookRoom('${c.name}', '${c.amount}')"` : "";
        let clickAction = c.status === "Available"
            ? `onclick="bookRoom('${c.name}','${c.company}','${c.branch}','${c.cost_center}','${c.amount}',)"`
            : "";
        let disabledStyle = c.status === "Available" ? "" : "opacity:0.5; cursor:not-allowed;";
        let bookingPeriod = "";
        if (c.status === "Not Available" && c.from_date && c.to_date) {
            bookingPeriod = ` (from ${c.from_date} ${c.from_time || ''} to ${c.to_date} ${c.to_time || ''})`;
        }
        html += `
    <div class="room-item">
        <div class="room-card" ${clickAction} style="${disabledStyle}">
            <div class="room-title">${c.room_name || 'N/A'}</div>
            <div class="room-info">Company: ${c.company || '0.0'}</div>
            <div class="room-info">Seating Capacity: ${c.seating_capacity || '0.0'}</div>
            <div class="room-info">Per Day/Per Event:Nu.${c.amount || '0.0'}</div>
            
             <div style="color:${statusColor}; font-weight:bold;">
                    ${c.status}${bookingPeriod}
            </div>
        </div>
        
    </div>`;
    });

    container.innerHTML = html;
}


function bookRoom(name, company, branch, cost_center, amount,) {
    const route_options = {
        venue: name,
        company: company,
        branch: branch,
        cost_center: cost_center,
        amount: amount

    };

    window.location.href =
        `/hall-booking/new?route_options=${encodeURIComponent(JSON.stringify(route_options))}`;

}

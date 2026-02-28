frappe.ready(function () {
    // 1️⃣ Populate college dropdown
    frappe.call({
        method: "education.www.events.index.get_college",
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
        getEventsInfo(college);
    });
});

function getEventsInfo(college = '') {
    frappe.call({
        method: "education.www.events.index.get_events_info",
        args: { college: college },
        callback: function (r) {
            const container = document.getElementById("events-list");
            container.innerHTML = '';
            container.style.display = "flex";           // override grid
            container.style.justifyContent = "center";  // horizontal center
            container.style.alignItems = "center";

            if (!r.message || !r.message.events_info || r.message.events_info.length === 0) {
                container.innerHTML = `
            
            <div class="alertcontainer">     
            <div class="alert alert-info text-center">
                <p>No Events records found</p>
            </div>
            </div>
       `;
                return;
            }

            displayEventsInfo(r.message.events_info);
        }
    });
}

function displayEventsInfo(events) {
    const container = document.getElementById("events-list");
    let html = '';

    events.forEach(c => {
        let registrationUrl = '';
        if (c.event_type === "Conference") {
            registrationUrl = `/audience-registration/new?route_options=${encodeURIComponent(JSON.stringify({ event: c.name }))}`;
        } else {
            registrationUrl = `/event-registration/new?route_options=${encodeURIComponent(JSON.stringify({ event: c.name }))}`;
        }
        html += `
          <div class="event-item">
        <div class="event-card">
            ${c.event_banner ? `<img src="${c.event_banner}" class="event-image"/>`
                : `<div class="event-image-placeholder">No Image</div>`}
            <div class="event-title">${c.event_title || 'N/A'}</div>
            <div class="event-type">Event Type: ${c.event_type || 'N/A'}</div>
            <div class="event-start-date">🗓️ Start: ${c.start_date || 'N/A'}</div>
            <div class="event-end-date">🗓️ End: ${c.end_date || 'N/A'}</div>
            <div class="event-location">Venue: ${c.room || 'N/A'}</div>
            <div class="event-location">Capacity: ${c.capacity || 'N/A'}</div>
       
           </div>
               <button class="register-btn" onclick="registerEvent('${c.name}', '${c.event_type}')">Register</button>
           </div>
        `;
    });

    container.innerHTML = html;
}

// function registerEvent(name) {
//     const route_options = { event: decodeURIComponent(name) };
//     window.location.href = `/event-registration/new?route_options=${encodeURIComponent(JSON.stringify(route_options))}`;
// }

function registerEvent(name, event_type) {
    const route_options = { event: decodeURIComponent(name) };

    if (event_type === "Conference") {
        window.location.href = `/audience-registration/new?route_options=${encodeURIComponent(JSON.stringify(route_options))}`;
    } else {
        window.location.href = `/event-registration/new?route_options=${encodeURIComponent(JSON.stringify(route_options))}`;
    }
}

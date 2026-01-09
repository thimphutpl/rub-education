

function getConferenceInfo() {
    frappe.call({
        method: "education.www.conference-announcement.index.get_conference_info",
        callback: function (r) {

            if (!r.message || !r.message.conferences || r.message.conferences.length === 0) {

                const container = document.getElementById("conference-list");

                // Switch layout to flex for centering
                container.style.display = "flex";
                container.style.justifyContent = "center";
                container.style.alignItems = "center";
                container.style.gridTemplateColumns = "";
                container.innerHTML = `
                    <div class="alert alert-info text-center" style="padding: 1.5rem; font-size: 1.1rem;">
                        <p>No Conference Announcement records found</p>
                    </div>
                `;
                return;
            }
            displayConferenceInfo(r.message.conferences);
        }
    });
}
// function displayConferenceInfo(conferences) {
//     var container = document.getElementById("conference-list");
//     var html = '';


//     conferences.forEach(function (c) {
//         html += '<div class="conference-card">' +
//             (c.image
//                 ? '<img src="' + c.image + '" class="conference-image" />'
//                 : '<div class="conference-image-placeholder">No Image</div>') +
//             '<div class="conference-title">' + (c.theme || '') + '</div>' +
//             '<div class="conference-title">' + (c.title || '') + '</div>' +
//             '<div class="conference-start-date">🗓️' + (c.start_date || '') + '</div>' +
//             '<div class="conference-end-date">🗓️' + (c.end_date || '') + '</div>' +
//             '<div class="conference-location">📍' + (c.location || '') + '</div>' +
//             '<div class="conference-location">Deadline:' + (c.deadline || '') + '</div>' +
//             '<button class="register-btn" onclick="registerConference(\'' + c.name + '\',\'' + c.theme + '\')"> Register</button>' +
//             '</div>';

//     });

//     container.innerHTML = html;
// }

// frappe.ready(function () {
//     getConferenceInfo();
// });


// // function registerConference(conferenceName) {
// //     // You can replace this with your actual registration logic
// //     window.location.href = '/conference-registration?conference=' + encodeURIComponent(conferenceName);
// // }
// function registerConference(conferenceName) {
//     const decodedName = decodeURIComponent(conferenceName);
//     const route_options = { conference: decodedName };
//     window.location.href = `/conference-registration/new?route_options=${encodeURIComponent(JSON.stringify(route_options))}`;
// }
function displayConferenceInfo(conferences) {
    const container = document.getElementById("conference-list");
    let html = '';

    conferences.forEach(function (c) {
        // Use template literals for cleaner HTML and JSON.stringify for safe onclick
        html += `
            <div class="conference-card">
                ${c.image
                ? `<img src="${c.image}" class="conference-image" />`
                : `<div class="conference-image-placeholder">No Image</div>`}
                <div class="conference-title">${c.theme || ''}</div>
                <div class="conference-location">${c.title || ''}</div>
                <div class="conference-start-date">🗓️ ${c.start_date || ''}</div>
                <div class="conference-end-date">🗓️ ${c.end_date || ''}</div>
                <div class="conference-location">📍 ${c.location || ''}</div>
                <div class="conference-location">Deadline: ${c.deadline || ''}</div>
                <button class="register-btn" onclick='registerConference(${JSON.stringify({ name: c.name, theme: c.theme })})'>
                    Register
                </button>
            </div>
        `;
    });

    container.innerHTML = html;
}

frappe.ready(function () {
    getConferenceInfo();
});

function registerConference(conferenceObj) {
    // conferenceObj contains { name, theme }
    const route_options = { conference: conferenceObj.name, theme: conferenceObj.theme };
    window.location.href = `/call-for-paper/new?route_options=${encodeURIComponent(JSON.stringify(route_options))}`;
}

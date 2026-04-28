// function getRoomInfo() {
//     let emailValue = document.querySelector("input[name='email']").value.trim();
//     if (!emailValue) {
//         alert("Please enter your email address.");
//         return;
//     }

//     frappe.call({
//         method: "education.www.room-status.index.get_room_info",
//         args: { email: emailValue },
//         callback: function (r) {
//             displayRoomInfo(r.message);
//         },
//         error: function (err) {
//             console.error("API Error:", err);
//             alert("Error connecting to server. Please try again.");
//         }
//     });
// }

// function displayRoomInfo(response) {
//     var roomContainer = document.getElementById("room-status");

//     if (response && response.room_info && response.room_info.length > 0) {
//         let html = '';

//         response.room_info.forEach(function (room, index) {
//             // Set badge color based on workflow_state or availability
//             let badgeColor = "badge-warning"; // default

//             if (room.workflow_state === "Approved") {
//                 badgeColor = "badge-success";
//             }
//             else if (room.workflow_state === "Waiting for Approval") {
//                 badgeColor = "badge-warning";
//             }
//             else if (room.workflow_state === "Rejected") {
//                 badgeColor = "badge-danger"; // commonly used red color for rejection
//             }


//             // Show booking period if available
//             let bookingPeriod = "";
//             if (room.from_date && room.to_date) {
//                 bookingPeriod = ` (from ${room.from_date} ${room.from_time || ''} to ${room.to_date} ${room.to_time || ''})`;
//             }
//             let paymentButton = "";
//             if (room.workflow_state === "Approved") {
//                 paymentButton = `
//             <button class="btn btn-primary make-payment-btn" 
//                     onclick="goToPayment(
//                     '${room.venue}',
//                     '${room.company}',
//                     '${room.branch}',
//                     '${room.cost_center}',
//                     '${room.email}',
//                     '${room.name1}',
//                     '${room.country}',
//                     '${room.dzongkhag}',
//                     '${room.designation}',
//                     '${room.organization}',
//                     '${room.amount}',
//                     '${room.total_days}',
//                     '${room.total_amount}',
//                     '${room.account_number}'
//                  )" 
//                     title="Click to complete your payment for this room">Pay Now
//             </button>
//         `;
//             }

//             html += `
//                 <div class="room-status">
//                     <div class="room-card-status">
//                     <div class="room-title-status">
//                     ${room.venue || 'N/A'}
//                     </div>
//                     <div class="room-info">Company:${room.company || 'None'}</div>
//                     <div class="room-info">Per Day/Per Event:Nu.${room.amount || '0.0'}</div>
//                     <div class="room-info">Total Days:${room.total_days || '0.0'}</div>
//                     <div class="room-info">Total Amount:Nu.${room.total_amount || '0.0'}</div>
         
//                         <p class="status-text ${badgeColor}">
//                             <strong></strong> ${room.workflow_state || 'N/A'}${bookingPeriod}
//                         </p>
                         
//                     </div>
                    
//                 </div>
//                 <div class"button-container">
//                      ${paymentButton}
//                 </div>
//             `;
//         });

//         roomContainer.innerHTML = html;
//     } else {
//         roomContainer.innerHTML = `
//             <div class="alert alert-info text-center">
//                 <p>No bookings were found for this email address.</p>
//             </div>
//         `;
//     }
// }

// // Auto-load if email pre-filled
// frappe.ready(function () {
//     let inputField = document.querySelector("input[name='email']");
//     let email = inputField.value.trim();
//     if (email !== "") {
//         getRoomInfo();
//     }
// });


// function goToPayment(venue, company, branch, cost_center, email, name1, country, dzongkhag,
//     designation, organization, amount, total_days, total_amount,account_number
// ) {
//     const route_options = {
//         venue: venue,
//         company: company,
//         branch: branch,
//         cost_center: cost_center,
//         email: email,
//         name1: name1,
//         dzongkhag: dzongkhag,
//         country: country,
//         designation: designation,
//         organization: organization,
//         amount: amount,
//         total_days: total_days,
//         total_amount: total_amount,
//         account_number:account_number


//     };

//     window.location.href = `/hall-payment/new?route_options=${encodeURIComponent(JSON.stringify(route_options))}`;

// }


// // function goToPayment(venue) {
// //     const route_options = { venue: decodeURIComponent(venue) };

// //     window.location.href = `/hall-payment/new?route_options=${encodeURIComponent(JSON.stringify(route_options))}`;
// // }



function getRoomInfo() {
    let emailValue = document.querySelector("input[name='email']").value.trim();
    if (!emailValue) {
        alert("Please enter your email address.");
        return;
    }

    frappe.call({
        method: "education.www.room-status.index.get_room_info",
        args: { email: emailValue },
        callback: function (r) {
            displayRoomInfo(r.message);
        },
        error: function (err) {
            console.error("API Error:", err);
            alert("Error connecting to server. Please try again.");
        }
    });
}

function displayRoomInfo(response) {
    var roomContainer = document.getElementById("room-status");

    if (response && response.room_info && response.room_info.length > 0) {
        let html = '';

        response.room_info.forEach(function (room, index) {
            // Set badge color based on workflow_state or availability
            let badgeColor = "badge-warning"; // default

            if (room.workflow_state === "Approved") {
                badgeColor = "badge-success";
            }
            else if (room.workflow_state === "Waiting for Approval") {
                badgeColor = "badge-warning";
            }
            else if (room.workflow_state === "Rejected") {
                badgeColor = "badge-danger"; // commonly used red color for rejection
            }


            // Show booking period if available
            let bookingPeriod = "";
            if (room.from_date && room.to_date) {
                bookingPeriod = ` (from ${room.from_date} ${room.from_time || ''} to ${room.to_date} ${room.to_time || ''})`;
            }
            let paymentButton = "";
            if (room.workflow_state === "Approved") {
                paymentButton = `
            <button class="btn btn-primary make-payment-btn" 
                   onclick="goToPayment('${encodeURIComponent(room.name)}')"
                    title="Click to complete your payment for this room">Pay Now
            </button>
        `;
            }

            html += `
                <div class="room-status">
                    <div class="room-card-status">
                    <div class="room-title-status">
                    ${room.venue || 'N/A'}
                    </div>
                    <div class="room-info">Company:${room.company || 'None'}</div>
                    <div class="room-info">Per Day/Per Event:Nu.${room.amount || '0.0'}</div>
                    <div class="room-info">Total Days:${room.total_days || '0.0'}</div>
                    <div class="room-info">Total Amount:Nu.${room.total_amount || '0.0'}</div>
         
                        <p class="status-text ${badgeColor}">
                            <strong></strong> ${room.workflow_state || 'N/A'}${bookingPeriod}
                        </p>
                         
                    </div>
                    
                </div>
                <div class"button-container">
                     ${paymentButton}
                </div>
            `;
        });

        roomContainer.innerHTML = html;
    } else {
        roomContainer.innerHTML = `
            <div class="alert alert-info text-center">
                <p>No bookings were found for this email address.</p>
            </div>
        `;
    }
}

frappe.ready(function () {
    let inputField = document.querySelector("input[name='email']");
    let email = inputField.value.trim();
    if (email !== "") {
        getRoomInfo();
    }
});

function goToPayment(name) {
	window.location.href = `/hall-payment/new?venue=${name}`;
}




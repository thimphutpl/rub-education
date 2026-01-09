function getConferenceInfo() {
    let emailValue = document.querySelector("input[name='email']").value;
    console.log("Email:", emailValue);

    if (!emailValue) {
        alert("Please enter your email address.");
        return;
    }

    frappe.call({
        method: "education.www.abstract-review-status-check.index.get_conference",
        args: {
            email: emailValue
        },
        callback: function (r) {
            console.log("API Response:", r);
            displayConferenceInfo(r.message);
        },
        error: function (err) {
            console.error("API Error:", err);
            alert("Error connecting to server. Please try again.");
        }
    });
}

function displayConferenceInfo(response) {
    var infoContainer = document.getElementById("abstract-review-status-check");
    console.log("Display response:", response);

    // Use response.conferences (the data you're actually getting)
    if (response && response.conferences_info && response.conferences_info.length > 0) {
        console.log("Found conferences:", response.conferences_info);

        let html = '';



        response.conferences_info.forEach(function (conferences_info, index) {
            let badgeColor;
            switch (conferences_info.workflow_state) {
                case 'Approved':
                    badgeColor = 'success';
                    break;
                case 'Rejected':
                    badgeColor = 'danger';
                    break;
                case 'Waiting for Review':
                default:
                    badgeColor = 'warning';
                    break;
            }
            html += `
            <div class="conference-card mb-4 p-3 shadow-sm">
                <div class="conference-detail">
                    <p>Name: ${conferences_info.name1}</p>
                    <p>Name: ${conferences_info.theme}</p>
                    
                    <p class="status-text badge-${badgeColor}"> ${conferences_info.workflow_state || 'N/A'}</p>
                   ${conferences_info.workflow_state === 'Approved' ? `
                    <div class="d-flex justify-content-center mt-auto">
                      <button class="full-button"
        onclick='applyFullPaper(${JSON.stringify({
                name: conferences_info.name,
                theme: conferences_info.theme,
                conference: conferences_info.conference,
                prefix: conferences_info.prefix,
                first_name: conferences_info.first_name,
                middle_name: conferences_info.middle_name,
                last_name: conferences_info.last_name,
                nationality: conferences_info.nationality,
                passport__cid_number: conferences_info.passport__cid_number,
                country_of_your_current_location: conferences_info.country_of_your_current_location,
                organisation: conferences_info.organisation,
                current_position: conferences_info.current_position,
                email: conferences_info.email,
                mobile_number: conferences_info.mobile_number,
                name1: conferences_info.name1,
                contact_number: conferences_info.contact_number,
                relationship: conferences_info.relationship,
                title: conferences_info.title,
                affiliation: conferences_info.affiliation,
                brief_bio_of_the_authors: conferences_info.brief_bio_of_the_authors,
                abstract: conferences_info.abstract,
                author_name: conferences_info.author_name || [],
                author_details: conferences_info.author_details || []
            })})'>
        Apply Full Paper
        </button>
                            </div>` : ''}
                </div>
            </div>
            `;
        });

        infoContainer.innerHTML = html;
    }
    else {
        infoContainer.innerHTML = `
            <div class="alert alert-info text-center">
                <p>No conference registrations were found for this email address.</p>
            </div>
        `;
    }
}

function applyFullPaper(conferenceName) {

    // const route_options = {
    //     conference: conferenceName.conference,
    //     theme: conferenceName.theme,
    //     prefix: conferenceName.prefix
    // };
    const route_options = conferenceName;

    window.location.href = `/full-paper/new?route_options=${encodeURIComponent(JSON.stringify(route_options))}`;
}


frappe.ready(function () {
    let inputField = document.querySelector("input[name='email']");
    let email = inputField.value;

    if (email && email.trim() !== "") {
        getConferenceInfo(email);
    }
});
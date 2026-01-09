function getFullPaperInfo() {
    let emailValue = document.querySelector("input[name='email']").value;
    console.log("Email:", emailValue);

    if (!emailValue) {
        alert("Please enter your email address.");
        return;
    }

    frappe.call({
        method: "education.www.full-paper-review-status-check.index.get_full_paper",
        args: {
            email: emailValue
        },
        callback: function (r) {
            console.log("API Response:", r);
            displayFullPaperInfo(r.message);
        },
        error: function (err) {
            console.error("API Error:", err);
            alert("Error connecting to server. Please try again.");
        }
    });
}

function displayFullPaperInfo(response) {
    var infoFullPager = document.getElementById("full-paper-review-status-check");
    console.log("Display response:", response);

    // Use response.conferences (the data you're actually getting)
    if (response && response.full_paper_info && response.full_paper_info.length > 0) {
        console.log("Found conferences:", response.full_paper_info);

        let html = '';



        response.full_paper_info.forEach(function (full_paper_info, index) {
            let badgeColor;
            switch (full_paper_info.workflow_state) {
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
            <div class="full-paper-card mb-4 p-3 shadow-sm">
                <div class="full-paper-detail">
                    <p>Name: ${full_paper_info.name}</p>
                    <p class="status-text badge-${badgeColor}"> ${full_paper_info.workflow_state || 'N/A'}</p>
                   ${full_paper_info.workflow_state === 'Approved' ? `
                    <div class="d-flex justify-content-center mt-auto">
                        <button class="full-button" onclick="applyFullPaper('${full_paper_info.name}')">Apply Full Paper</button>
                        
                    </div>` : ''}
                </div>
            </div>
            `;
        });

        infoFullPager.innerHTML = html;
    }
    else {
        infoFullPager.innerHTML = `
            <div class="alert alert-info text-center">
                <p>No conference registrations were found for this email address.</p>
            </div>
        `;
    }
}

frappe.ready(function () {
    let inputField = document.querySelector("input[name='email']");
    let email = inputField.value;

    if (email && email.trim() !== "") {
        getFullPaperInfo(email);
    }
});
frappe.ready(function() {
    let captchaWidget = null;
    let captchaRendered = false;
    let captchaVerified = false;
    let perDayAmount = 0;

    
    function renderCaptcha() {
        // Don't re-render if already rendered and valid
        if (captchaRendered && captchaWidget !== null) {
            try {
                // Check if widget still exists
                if (typeof grecaptcha !== 'undefined' && grecaptcha.getResponse(captchaWidget)) {
                    console.log("Captcha already valid");
                    return;
                }
            } catch(e) {
                captchaRendered = false;
            }
        }

        let container = document.getElementById("recaptcha-container");
        
        if (!container) {
            // Find a better place to insert - before the submit button
            const $form = $('form');
            if ($form.length) {
                $form.append(`
                    <div class="form-group">
                        <div class="col-sm-12">
                            <div id="recaptcha-container" style="width:100%;"></div>
                        </div>
                    </div>
                `);
                container = document.getElementById("recaptcha-container");
            } else {
                // Wait for form to be available using MutationObserver
                waitForFormAndRender();
                return;
            }
        }

        if (typeof grecaptcha === "undefined") {
            // Load reCAPTCHA if not loaded
            if (!document.querySelector('script[src*="recaptcha/api.js"]')) {
                const script = document.createElement('script');
                script.src = 'https://www.google.com/recaptcha/api.js?render=explicit';
                script.async = true;
                script.defer = true;
                script.onload = function() {
                    renderCaptcha();
                };
                document.head.appendChild(script);
            } else {
                // Wait for grecaptcha to be available
                waitForGrecaptchaAndRender();
            }
            return;
        }

        if (captchaWidget !== null) {
            try {
                grecaptcha.reset(captchaWidget);
                return;
            } catch(e) {
                captchaWidget = null;
            }
        }

        try {
            // Clear container
            container.innerHTML = '';
            
            captchaWidget = grecaptcha.render(container, {
                sitekey: "6Lery8osAAAAAIvNfDE7w9rNEA5etF5cGkWlD4tY",
                callback: function(response) {
                    console.log("✅ Captcha verified");
                    captchaRendered = true;
                    captchaVerified = true;
                    // Enable submit button when captcha is verified
                    enableSubmitButton(true);
                },
                "expired-callback": function() {
                    console.log("⚠️ Captcha expired - re-rendering");
                    captchaWidget = null;
                    captchaRendered = false;
                    captchaVerified = false;
                    // Disable submit button when captcha expires
                    enableSubmitButton(false);
                    renderCaptcha();
                },
                "error-callback": function() {
                    console.error("❌ Captcha error");
                    captchaWidget = null;
                    captchaRendered = false;
                    captchaVerified = false;
                    // Disable submit button on error
                    enableSubmitButton(false);
                }
            });
            console.log("✅ reCAPTCHA rendered");
            
            // Initially disable submit button until captcha is verified
            enableSubmitButton(false);
        } catch (error) {
            console.error("Error:", error);
            // Try again on next event loop
            requestAnimationFrame(() => renderCaptcha());
        }
    }

    // Helper function to enable/disable submit button
    function enableSubmitButton(enable) {
        const $submitBtn = $('form button[type="submit"]');
        if ($submitBtn.length) {
            if (enable) {
                $submitBtn.prop("disabled", false);
                $submitBtn.css('opacity', '1');
                console.log("✅ Submit button enabled");
            } else {
                $submitBtn.prop("disabled", true);
                $submitBtn.css('opacity', '0.5');
                console.log("❌ Submit button disabled");
            }
        }
    }

    // Helper function to check if button should be enabled
    function updateSubmitButtonState() {
        if (!frappe.web_form || typeof frappe.web_form.get_value !== 'function') {
            enableSubmitButton(false);
            return;
        }
        
        const email = frappe.web_form.get_value("email");
        const venue = frappe.web_form.get_value("venue");
        const from_date = frappe.web_form.get_value("from_date");
        const to_date = frappe.web_form.get_value("to_date");
        
        const requiredFieldsFilled = email && venue && from_date && to_date;
        const shouldEnable = requiredFieldsFilled && captchaVerified;
        
        enableSubmitButton(shouldEnable);
    }

    // Helper function to wait for form element
    function waitForFormAndRender() {
        const observer = new MutationObserver(function(mutations, obs) {
            const $form = $('form');
            if ($form.length) {
                obs.disconnect();
                renderCaptcha();
            }
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    }

    // Helper function to wait for grecaptcha
    function waitForGrecaptchaAndRender() {
        const checkGrecaptcha = function() {
            if (typeof grecaptcha !== "undefined") {
                renderCaptcha();
                return true;
            }
            return false;
        };
        
        if (!checkGrecaptcha()) {
            const observer = new MutationObserver(function() {
                if (checkGrecaptcha()) {
                    observer.disconnect();
                }
            });
            observer.observe(document.head, { childList: true, subtree: true });
        }
    }

    function getCaptchaResponse() {
        if (captchaWidget !== null && typeof grecaptcha !== 'undefined') {
            try {
                const response = grecaptcha.getResponse(captchaWidget);
                return response && response.length > 0 ? response : null;
            } catch(e) {
                return null;
            }
        }
        return null;
    }

    function resetCaptcha() {
        if (captchaWidget !== null && typeof grecaptcha !== 'undefined') {
            try {
                grecaptcha.reset(captchaWidget);
                captchaRendered = false;
                captchaVerified = false;
                enableSubmitButton(false);
            } catch(e) {
                captchaWidget = null;
                renderCaptcha();
            }
        }
    }

    function verifyWithServer(captchaResponse, callback) {
        frappe.call({
            method: "education.event_management.web_form.hall_booking.hall_booking.verify_captcha",
            args: { "response": captchaResponse },
            callback: function(r) {
                if (r.message && r.message.verified) {
                    callback(true);
                } else {
                    callback(false);
                }
            },
            error: function() {
                callback(false);
            }
        });
    }

    const params = new URLSearchParams(window.location.search);
    const name = params.get("venue");
    
    if (name) {
        frappe.call({
            method: "education.event_management.web_form.hall_booking.hall_booking.get_hall_data",
            args: { name: name },
            callback: function(r) {
                if (!r.message || r.message.error) {
                    frappe.msgprint(r.message?.error || "Error loading hall booking data");
                    return;
                }
                
                const opts = r.message;
                console.log(opts);
                
                frappe.web_form.set_value("venue", opts.venue);
                frappe.web_form.set_value("company", opts.company);
                frappe.web_form.set_value("branch", opts.branch);
                frappe.web_form.set_value("cost_center", opts.cost_center);
                frappe.web_form.set_value("amount", opts.amount);
                
                if (opts.amount) {
                    perDayAmount = parseFloat(opts.amount);
                }
                
                if (opts.qr_code) {
                    const $qrField = $(`[data-fieldname="qr_code"] .control-value`);
                    if ($qrField.length) {
                        $qrField.html(`<img src="${opts.qr_code}" style="max-width:200px; border:1px solid #ddd; padding:5px; border-radius:8px;" />`);
                    } else {
                        frappe.web_form.set_value("qr_code", opts.qr_code);
                    }
                }
                
                // Update button state after loading data
                updateSubmitButtonState();
            }
        });
    }

    const calculateTotal = () => {
        const fromDate = frappe.web_form.get_value("from_date");
        const toDate = frappe.web_form.get_value("to_date");
        const amountField = parseFloat(frappe.web_form.get_value("amount")) || 0;
        const perDay = amountField || perDayAmount || 0;

        if (fromDate && toDate && perDay > 0) {
            const result = calculateBooking(fromDate, toDate, perDay);
            frappe.web_form.set_value("total_days", result.total_days);
            frappe.web_form.set_value("total_amount", result.total_amount);
        } else {
            frappe.web_form.set_value("total_days", 0);
            frappe.web_form.set_value("total_amount", 0);
        }
        

        updateSubmitButtonState();
    };

    frappe.web_form.on("from_date", (field, value) => calculateTotal());
    frappe.web_form.on("to_date", (field, value) => calculateTotal());
    frappe.web_form.on("amount", (field, value) => calculateTotal());

    function calculateBooking(fromDate, toDate, perDayAmount) {
        let from, to;

        if (typeof fromDate === 'string') {
            if (fromDate.includes('-')) {
                const parts = fromDate.split('-');
                if (parts[0].length === 4) {
                    from = new Date(parts[0], parts[1] - 1, parts[2]);
                    to = new Date(toDate.split('-')[0], toDate.split('-')[1] - 1, toDate.split('-')[2]);
                } else {
                    from = new Date(parts[2], parts[1] - 1, parts[0]);
                    to = new Date(toDate.split('-')[2], toDate.split('-')[1] - 1, toDate.split('-')[0]);
                }
            }
        } else {
            from = new Date(fromDate);
            to = new Date(toDate);
        }

        const diffTime = Math.abs(to - from);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
        const total_amount = diffDays * perDayAmount;

        return { total_days: diffDays, total_amount };
    }

    function setupFieldChangeListeners() {
        if (!frappe.web_form) return;
        
        const requiredFields = ['email', 'venue', 'from_date', 'to_date'];
        
        requiredFields.forEach(fieldname => {
            $(document).on('frappe.web_form.field_change', function(e, field) {
                if (requiredFields.includes(field.df.fieldname)) {
                    updateSubmitButtonState();
                }
            });
        });
        
        $('input[data-fieldname="from_date"], input[data-fieldname="to_date"], input[data-fieldname="email"], select[data-fieldname="venue"]').on('change keyup', function() {
            updateSubmitButtonState();
        });
        
        updateSubmitButtonState();
    }


    $('form button[type="submit"]').on('click', function(e) {
        e.preventDefault();
        
        // Check captcha verification before proceeding
        if (!captchaVerified) {
            frappe.msgprint({
                title: "Verification Required",
                message: 'Please complete the "I am not a robot" verification.',
                indicator: "red"
            });
            return false;
        }

        const email = frappe.web_form.get_value("email");
        const venue = frappe.web_form.get_value("venue");
        const from_date = frappe.web_form.get_value("from_date");
        const to_date = frappe.web_form.get_value("to_date");
        
        if (from_date && to_date) {
            const from = new Date(from_date);
            const to = new Date(to_date);

            if (from > to) {
                frappe.msgprint("From Date cannot be after To Date");
                return;
            }
        }

        // Get captcha response
        const captchaResponse = getCaptchaResponse();
        
        if (!captchaResponse) {
            frappe.msgprint({
                title: "Verification Required",
                message: 'Please check the "I am not a robot" box.',
                indicator: "red"
            });
            return false;
        }

        const $btn = $(this);
        const originalText = $btn.html();
        $btn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> Verifying...');

        // Verify captcha with server
        verifyWithServer(captchaResponse, function(isValid) {
            if (!isValid) {
                frappe.msgprint({
                    title: "Verification Failed",
                    message: "Captcha verification failed. Please try again.",
                    indicator: "red"
                });
                resetCaptcha();
                $btn.prop('disabled', false).html(originalText);
                return;
            }

            // Check venue availability
            frappe.call({
                method: "education.event_management.web_form.hall_booking.hall_booking.check_duplicate_venue",
                args: {
                    email: email,
                    venue: venue,
                    from_date: from_date,
                    to_date: to_date
                },
                callback: function(r) {
                    if (r.message.conflict) {
                        frappe.msgprint(`This venue is already booked from ${r.message.booked_from} to ${r.message.booked_to}.`);
                        resetCaptcha();
                        $btn.prop('disabled', false).html(originalText);
                    } else {
                        $btn.html('<i class="fa fa-spinner fa-spin"></i> Submitting...');
                        $('form').submit();
                    }
                },
                error: function() {
                    frappe.msgprint("Error checking availability. Please try again.");
                    $btn.prop('disabled', false).html(originalText);
                }
            });
        });
    });

    function initialize() {
        console.log("Initializing captcha...");
        renderCaptcha();
        setupFieldChangeListeners();
        calculateTotal();
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
});
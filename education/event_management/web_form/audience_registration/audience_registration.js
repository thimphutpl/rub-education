// frappe.ready(function () {
// 	const params = new URLSearchParams(window.location.search);
// 	const route_options = params.get("route_options");

// 	if (route_options) {
// 		const opts = JSON.parse(decodeURIComponent(route_options));
// 		frappe.web_form.set_value("full_paper", opts.event);
// 	}

// 	let is_submitting = false;

// 	$('form button[type="submit"]').on('click', function (e) {

// 		if (is_submitting) return;

// 		e.preventDefault();

// 		is_submitting = true;

// 		const email = frappe.web_form.get_value("email_address");
// 		const event = frappe.web_form.get_value("full_paper");

// 		frappe.call({
// 			method: "education.event_management.web_form.audience_registration.audience_registration.check_duplicate_registration",
// 			args: {
// 				full_paper: event,
// 				email: email
// 			}
// 		}).then(r => {

// 			if (r.message && r.message.status === "duplicate") {
// 				frappe.msgprint(" " + r.message.message);
// 				is_submitting = false;
// 			} else {
// 				$('form').submit();
// 				setTimeout(function () {
// 					window.location.href = '/events';
// 				}, 1000);
// 			}

// 		});

// 	});
// });

frappe.ready(function() {
    let captchaWidget = null;
    let captchaRendered = false;
    let captchaVerified = false;
    let is_submitting = false;

    const params = new URLSearchParams(window.location.search);
    const route_options = params.get("route_options");

    if (route_options) {
        try {
            const opts = JSON.parse(decodeURIComponent(route_options));
            if (opts.event) frappe.web_form.set_value("full_paper", opts.event);
        } catch(e) {
            console.error("Error parsing route_options:", e);
        }
    }

    // ==========================================
    // Helper: Wait for element using requestAnimationFrame
    // ==========================================
    function waitForElement(selector, callback, maxAttempts = 30) {
        let attempts = 0;
        
        const checkElement = () => {
            const element = document.querySelector(selector);
            if (element) {
                callback(element);
                return true;
            }
            attempts++;
            if (attempts < maxAttempts) {
                requestAnimationFrame(checkElement);
            } else {
                console.error(`Element ${selector} not found`);
            }
            return false;
        };
        
        checkElement();
    }

    function waitForGrecaptcha(callback) {
        const checkGrecaptcha = () => {
            if (typeof grecaptcha !== 'undefined') {
                callback();
                return true;
            }
            requestAnimationFrame(checkGrecaptcha);
            return false;
        };
        checkGrecaptcha();
    }

    // ==========================================
    // 1. Create captcha container
    // ==========================================
    function createCaptchaContainer() {
        let container = document.getElementById("recaptcha-container");
        if (container) return container;

        const $form = $('form');
        if (!$form.length) return null;

        const $submitBtn = $('form button[type="submit"]');
        const captchaHtml = `
            <div class="form-group">
                <div class="col-sm-12">
                    <div id="recaptcha-container" style="width:100%; margin: 15px 0;"></div>
                </div>
            </div>
        `;
        
        if ($submitBtn.length) {
            $submitBtn.closest('.form-group').before(captchaHtml);
        } else {
            $form.append(captchaHtml);
        }
        
        return document.getElementById("recaptcha-container");
    }

    // ==========================================
    // 2. Render reCAPTCHA
    // ==========================================
    function renderCaptcha() {
        if (captchaRendered && captchaWidget !== null) {
            try {
                if (typeof grecaptcha !== 'undefined' && grecaptcha.getResponse(captchaWidget)) {
                    console.log("Captcha already valid");
                    captchaVerified = true;
                    enableSubmitButton(true);
                    return;
                }
            } catch(e) {
                captchaRendered = false;
            }
        }

        let container = createCaptchaContainer();
        
        if (!container) {
            waitForElement('form', () => {
                renderCaptcha();
            });
            return;
        }

        if (typeof grecaptcha === "undefined") {
            if (!document.querySelector('script[src*="recaptcha/api.js"]')) {
                const script = document.createElement('script');
                script.src = 'https://www.google.com/recaptcha/api.js?render=explicit';
                script.async = true;
                script.defer = true;
                script.onload = () => renderCaptcha();
                document.head.appendChild(script);
            } else {
                waitForGrecaptcha(() => renderCaptcha());
            }
            return;
        }

        if (captchaWidget !== null) {
            try {
                grecaptcha.reset(captchaWidget);
                captchaVerified = false;
                enableSubmitButton(false);
                return;
            } catch(e) {
                captchaWidget = null;
            }
        }

        try {
            container.innerHTML = '';
            
            captchaWidget = grecaptcha.render(container, {
                sitekey: "6Lery8osAAAAAIvNfDE7w9rNEA5etF5cGkWlD4tY",
                callback: function(response) {
                    console.log("✅ Captcha verified");
                    captchaVerified = true;
                    captchaRendered = true;
                    enableSubmitButton(true);
                },
                "expired-callback": function() {
                    console.log("⚠️ Captcha expired");
                    captchaWidget = null;
                    captchaVerified = false;
                    captchaRendered = false;
                    enableSubmitButton(false);
                    renderCaptcha();
                },
                "error-callback": function() {
                    console.error("❌ Captcha error");
                    captchaWidget = null;
                    captchaVerified = false;
                    captchaRendered = false;
                    enableSubmitButton(false);
                }
            });
            console.log("✅ reCAPTCHA rendered");
            enableSubmitButton(false);
        } catch (error) {
            console.error("Error:", error);
            requestAnimationFrame(() => renderCaptcha());
        }
    }

    function enableSubmitButton(enable) {
        const $submitBtn = $('form button[type="submit"]');
        if ($submitBtn.length) {
            if (enable) {
                $submitBtn.prop("disabled", false);
                $submitBtn.css('opacity', '1');
                $submitBtn.css('cursor', 'pointer');
                console.log("Submit button ENABLED");
            } else {
                $submitBtn.prop("disabled", true);
                $submitBtn.css('opacity', '0.5');
                $submitBtn.css('cursor', 'not-allowed');
                console.log("Submit button DISABLED");
            }
        }
    }

    function updateSubmitButtonState() {
        if (!frappe.web_form || typeof frappe.web_form.get_value !== 'function') {
            enableSubmitButton(false);
            return;
        }
        
        const email = frappe.web_form.get_value("email_address");
        const event = frappe.web_form.get_value("full_paper");
        
        const requiredFieldsFilled = email && event;
        const shouldEnable = requiredFieldsFilled && captchaVerified;
        
        console.log("Button state - Email:", !!email, "Event:", !!event, "Captcha:", captchaVerified, "Enable:", shouldEnable);
        enableSubmitButton(shouldEnable);
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
                captchaVerified = false;
                enableSubmitButton(false);
                console.log("Captcha reset");
            } catch(e) {
                captchaWidget = null;
                requestAnimationFrame(() => renderCaptcha());
            }
        }
    }

    function verifyWithServer(captchaResponse, callback) {
        frappe.call({
            method: "education.event_management.web_form.audience_registration.audience_registration.verify_captcha",
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

    // ==========================================
    // Monitor form field changes
    // ==========================================
    function setupFieldChangeListeners() {
        if (!frappe.web_form) {
            const observer = new MutationObserver(() => {
                if (frappe.web_form && typeof frappe.web_form.get_value === 'function') {
                    observer.disconnect();
                    setupFieldChangeListeners();
                }
            });
            observer.observe(document.body, { attributes: true, childList: true, subtree: true });
            return;
        }
        
        const $emailField = $('input[data-fieldname="email_address"]');
        const $eventField = $('select[data-fieldname="full_paper"], input[data-fieldname="full_paper"]');
        
        if ($emailField.length) {
            $emailField.on('change keyup', function() {
                updateSubmitButtonState();
            });
        }
        
        if ($eventField.length) {
            $eventField.on('change keyup', function() {
                updateSubmitButtonState();
            });
        }
        
        updateSubmitButtonState();
    }

    // ==========================================
    // Handle form submission with captcha
    // ==========================================
    $(document).off('click', 'form button[type="submit"]').on('click', 'form button[type="submit"]', function(e) {
        if (is_submitting) return false;
        
        e.preventDefault();
        e.stopImmediatePropagation();

        console.log('Button clicked - checking captcha');

        if (!captchaVerified) {
            frappe.msgprint({
                title: "Verification Required",
                message: 'Please complete the "I am not a robot" verification.',
                indicator: "red"
            });
            return false;
        }

        const email = frappe.web_form.get_value("email_address");
        const event = frappe.web_form.get_value("full_paper");
        const $btn = $(this);

        if (!email || !event) {
            frappe.msgprint("Please fill in both email and event.");
            return false;
        }

        const captchaResponse = getCaptchaResponse();
        
        if (!captchaResponse) {
            frappe.msgprint({
                title: "Verification Required",
                message: 'Please check the "I am not a robot" box.',
                indicator: "red"
            });
            return false;
        }

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
                is_submitting = false;
                return;
            }

            // Check for duplicate registration
            frappe.call({
                method: "education.event_management.web_form.audience_registration.audience_registration.check_duplicate_registration",
                args: {
                    full_paper: event,
                    email: email
                },
                callback: function(r) {
                    if (r.message && r.message.status === "duplicate") {
                        frappe.msgprint(" " + r.message.message);
                        $btn.prop('disabled', false).html(originalText);
                        is_submitting = false;
                    } else {
                        $btn.prop('disabled', false).html(originalText);
                        $('form').submit();
                        // Use requestAnimationFrame instead of setTimeout
                        requestAnimationFrame(function() {
                            window.location.href = '/events';
                        });
                    }
                },
                error: function() {
                    frappe.msgprint("Error checking registration. Please try again.");
                    $btn.prop('disabled', false).html(originalText);
                    is_submitting = false;
                }
            });
        });

        return false;
    });

    // ==========================================
    // Initialize
    // ==========================================
    function initialize() {
        console.log("Initializing captcha for audience registration...");
        renderCaptcha();
        setupFieldChangeListeners();
    }
    
    initialize();
});
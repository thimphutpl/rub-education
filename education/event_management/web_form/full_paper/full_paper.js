// frappe.ready(function () {
// 	const params = new URLSearchParams(window.location.search);
// 	const route_options = params.get("route_options");
// 	console.log('Route options1:', route_options);
// 	let wordLimits = {
// 		min_revise_abstract: 0,
// 		max_revise_abstract: 0
// 	};
// 	frappe.call({
// 		method: "education.event_management.doctype.word_limit_settings.word_limit_settings.get_word_limits",
// 		callback: function (r) {
// 			if (r.message) {

// 				wordLimits.min_revise_abstract = r.message.min_revise_abstract;
// 				wordLimits.max_revise_abstract = r.message.max_revise_abstract;


// 				// Abstract description
// 				const $abstractField = $('textarea[data-fieldname="revise_abstract"]');
// 				console.log('Abstract field element:', $abstractField);
// 				if ($abstractField.next('.word-limit-desc').length === 0) {
// 					$abstractField.after(`<small class="word-limit-desc" style="color: #555;">Write between ${wordLimits.min_revise_abstract} - ${wordLimits.max_revise_abstract} words.</small>  <span style="color:red">*</span>`);
// 				} else {
// 					$abstractField.next('.word-limit-desc').text(`Write between ${wordLimits.min_revise_abstract} - ${wordLimits.max_revise_abstract} words.`);
// 				}

// 			}
// 		}
// 	});



// 	if (route_options) {
// 		const opts = JSON.parse(decodeURIComponent(route_options));
// 		frappe.web_form.set_value("conference", opts.conference);
// 		frappe.web_form.set_value("theme", opts.theme);
// 		frappe.web_form.set_value("prefix", opts.prefix);
// 		frappe.web_form.set_value("first_name", opts.first_name);
// 		frappe.web_form.set_value("middle_name", opts.middle_name);
// 		frappe.web_form.set_value("last_name", opts.last_name);
// 		frappe.web_form.set_value("nationality", opts.nationality);
// 		frappe.web_form.set_value("passport__cid_number", opts.passport__cid_number);
// 		frappe.web_form.set_value("country_of_your_current_location", opts.country_of_your_current_location);
// 		frappe.web_form.set_value("organisation", opts.organisation);
// 		frappe.web_form.set_value("current_position", opts.current_position);
// 		frappe.web_form.set_value("email", opts.email);
// 		frappe.web_form.set_value("mobile_number", opts.mobile_number);
// 		frappe.web_form.set_value("name1", opts.name1);
// 		frappe.web_form.set_value("contact_number", opts.contact_number);
// 		frappe.web_form.set_value("relationship", opts.relationship);
// 		frappe.web_form.set_value("title", opts.title);
// 		frappe.web_form.set_value("affiliation", opts.affiliation);
// 		frappe.web_form.set_value("brief_bio_of_the_authors", opts.brief_bio_of_the_authors);
// 		frappe.web_form.set_value("abstract", opts.abstract);
// 		if (Array.isArray(opts.author_name)) {


// 			const authorField = frappe.web_form.fields_dict['author_name'];
// 			authorField.df.data = []; // clear existing rows
// 			authorField.grid.grid_rows.forEach(r => r.remove()); // remove grid rows

// 			opts.author_name.forEach((row, idx) => {

// 				authorField.grid.add_new_row();
// 				const newRow = authorField.grid.get_row(authorField.grid.grid_rows.length - 1);
// 				newRow.doc.name1 = row.name1;
// 				newRow.refresh(); // refresh the new row
// 			});

// 			authorField.grid.refresh();
// 		}
// 		if (Array.isArray(opts.author_details)) {
// 			const bioField = frappe.web_form.fields_dict['brief_bio']; // use correct child table fieldname
// 			bioField.df.data = []; // clear existing rows
// 			bioField.grid.grid_rows.forEach(r => r.remove()); // remove existing grid rows

// 			opts.author_details.forEach((row, idx) => {

// 				bioField.grid.add_new_row();
// 				const newRow = bioField.grid.get_row(bioField.grid.grid_rows.length - 1);
// 				newRow.doc.brief_bio_of_the_authors = row.brief_bio_of_the_authors;
// 				newRow.refresh();
// 			});

// 			;
// 			bioField.grid.refresh();
// 		}

// 	}
// 	function getWordCount(text) {
// 		return text.trim().split(/\s+/).filter(w => w).length;
// 	}

// 	// Intercept the submit button click instead of form submission
// 	$('form button[type="submit"]').on('click', function (e) {
// 		e.preventDefault();
// 		e.stopImmediatePropagation();

// 		console.log('Button clicked - starting duplicate check');

// 		const email = frappe.web_form.get_value("email");
// 		// const conference = frappe.web_form.get_value("conference");
// 		const theme = frappe.web_form.get_value("theme");
// 		const prefix = frappe.web_form.get_value("prefix");
// 		const $btn = $(this);
// 		// console.log("Conference:", conference);


// 		// $btn.prop('disabled', true).html('Checking...');
// 		const abstractText = $('textarea[data-fieldname="revise_abstract"]').val() || "";
// 		// const bioCount = getWordCount(bioText);
// 		const abstractCount = getWordCount(abstractText);
// 		if (abstractCount < wordLimits.min_revise_abstract || abstractCount > wordLimits.max_revise_abstract) {
// 			frappe.msgprint(`Revised Abstract must have between ${wordLimits.min_revise_abstract} - ${wordLimits.max_revise_abstract} words. Current words: ${abstractCount}`);
// 			return false;
// 		}
// 		if (abstractCount > wordLimits.max_revise_abstract) {
// 			frappe.msgprint(`Revised Abstract must not exceed ${wordLimits.max_revise_abstract} words. Current words: ${abstractCount}`);
// 			return false;
// 		}

// 		// Make synchronous-like call using async/await
// 		frappe.call({
// 			method: "education.event_management.web_form.full_paper.full_paper.check_duplicate_registration",
// 			args: {
// 				// doctype: "Full Paper",
// 				// filters: [
// 				// 	// ["email", "=", email],
// 				// 	["conference", "=", conference]
// 				// ],
// 				// conference: conference,
// 				email: email,
// 				theme: theme
// 				// fields: ["name"],
// 				// limit: 1
// 			},
// 			callback: function (r) {



// 				if (r.message.exists) {
// 					console.log('Blocking submission - duplicate found');
// 					frappe.msgprint("You are already registered for this full paper.");
// 					$btn.prop('disabled', false).html('Submit');
// 				} else {
// 					$btn.prop('disabled', false).html('Submit');
// 					// Submit the form
// 					$('form').submit();
// 					setTimeout(function () {
// 						window.location.href = '/abstract-review-status-check';
// 					}, 1000);
// 				}
// 			}
// 		});

// 		return false;
// 	});
// });


frappe.ready(function() {
    let captchaWidget = null;
    let captchaRendered = false;
    let captchaVerified = false;

    const params = new URLSearchParams(window.location.search);
    const route_options = params.get("route_options");
    
    let wordLimits = {
        min_revise_abstract: 0,
        max_revise_abstract: 0
    };

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
                    captchaVerified = true;
                    captchaRendered = true;
                    enableSubmitButton(true);
                },
                "expired-callback": function() {
                    captchaWidget = null;
                    captchaVerified = false;
                    captchaRendered = false;
                    enableSubmitButton(false);
                    renderCaptcha();
                },
                "error-callback": function() {
                    captchaWidget = null;
                    captchaVerified = false;
                    captchaRendered = false;
                    enableSubmitButton(false);
                }
            });
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
            } else {
                $submitBtn.prop("disabled", true);
                $submitBtn.css('opacity', '0.5');
                $submitBtn.css('cursor', 'not-allowed');
         
            }
        }
    }

    function updateSubmitButtonState() {
        if (!frappe.web_form || typeof frappe.web_form.get_value !== 'function') {
            enableSubmitButton(false);
            return;
        }
        
        const email = frappe.web_form.get_value("email");
        const reviseAbstract = $('textarea[data-fieldname="revise_abstract"]').val() || "";
        
        const requiredFieldsFilled = email && reviseAbstract;
        const shouldEnable = requiredFieldsFilled && captchaVerified;
        
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
            } catch(e) {
                captchaWidget = null;
                requestAnimationFrame(() => renderCaptcha());
            }
        }
    }

    // ==========================================
    // Get word limits
    // ==========================================
    frappe.call({
        method: "education.event_management.doctype.word_limit_settings.word_limit_settings.get_word_limits",
        callback: function (r) {
            if (r.message) {
                wordLimits.min_revise_abstract = r.message.min_revise_abstract;
                wordLimits.max_revise_abstract = r.message.max_revise_abstract;

                const $abstractField = $('textarea[data-fieldname="revise_abstract"]');
                console.log('Abstract field element:', $abstractField);
                if ($abstractField.length) {
                    if ($abstractField.next('.word-limit-desc').length === 0) {
                        $abstractField.after(`<small class="word-limit-desc" style="color: #555;">Write between ${wordLimits.min_revise_abstract} - ${wordLimits.max_revise_abstract} words.</small>  <span style="color:red">*</span>`);
                    } else {
                        $abstractField.next('.word-limit-desc').text(`Write between ${wordLimits.min_revise_abstract} - ${wordLimits.max_revise_abstract} words.`);
                    }
                }
            }
        }
    });

    // ==========================================
    // Set route options
    // ==========================================
    if (route_options) {
        try {
            const o = JSON.parse(decodeURIComponent(route_options));
           
            // if (opts.conference) frappe.web_form.set_value("conference", opts.conference);
            // if (opts.theme) frappe.web_form.set_value("theme", opts.theme);
            // if (opts.prefix) frappe.web_form.set_value("prefix", opts.prefix);
            // if (opts.first_name) frappe.web_form.set_value("first_name", opts.first_name);
            // if (opts.middle_name) frappe.web_form.set_value("middle_name", opts.middle_name);
            // if (opts.last_name) frappe.web_form.set_value("last_name", opts.last_name);
            // if (opts.nationality) frappe.web_form.set_value("nationality", opts.nationality);
            // if (opts.passport__cid_number) frappe.web_form.set_value("passport__cid_number", opts.passport__cid_number);
            // if (opts.country_of_your_current_location) frappe.web_form.set_value("country_of_your_current_location", opts.country_of_your_current_location);
            // if (opts.organisation) frappe.web_form.set_value("organisation", opts.organisation);
            // if (opts.current_position) frappe.web_form.set_value("current_position", opts.current_position);
            // if (opts.email) frappe.web_form.set_value("email", opts.email);
            // if (opts.mobile_number) frappe.web_form.set_value("mobile_number", opts.mobile_number);
            // if (opts.name1) frappe.web_form.set_value("name1", opts.name1);
            // if (opts.contact_number) frappe.web_form.set_value("contact_number", opts.contact_number);
            // if (opts.relationship) frappe.web_form.set_value("relationship", opts.relationship);
            // if (opts.title) frappe.web_form.set_value("title", opts.title);
            // if (opts.affiliation) frappe.web_form.set_value("affiliation", opts.affiliation);
            // if (opts.abstract) frappe.web_form.set_value("abstract", opts.abstract);
            
            // if (Array.isArray(opts.author_name)) {
            //     const authorField = frappe.web_form.fields_dict['author_name'];
            //     if (authorField && authorField.grid) {
            //         authorField.df.data = [];
            //         authorField.grid.grid_rows.forEach(r => r.remove());
                    
            //         opts.author_name.forEach((row, idx) => {
            //             authorField.grid.add_new_row();
            //             const newRow = authorField.grid.get_row(authorField.grid.grid_rows.length - 1);
            //             if (newRow) {
            //                 newRow.doc.name1 = row.name1;
            //                 newRow.doc.brief_bio_of_the_author=row.brief_bio_of_the_author;
            //                 newRow.refresh();
            //             }
            //         });
            //         authorField.grid.refresh();
            //     }
            // }
            frappe.call({
            method: "education.event_management.web_form.full_paper.full_paper.get_data",
            args: { name: o.name },
            callback: function (r) {

                const opts = r.message;
                if (!opts) return;

                // -------------------------
                // Parent fields
                // -------------------------
                const fields = [
                    "conference", "theme", "prefix", "first_name",
                    "middle_name", "last_name", "nationality",
                    "passport__cid_number", "country_of_your_current_location",
                    "organisation", "current_position", "email",
                    "mobile_number", "title", "affiliation", "abstract"
                ];

                fields.forEach(f => {
                    if (opts[f]) {
                        frappe.web_form.set_value(f, opts[f]);
                    }
                });

                // -------------------------
                // Child Table
                // -------------------------
                if (Array.isArray(opts.author_name)) {

                    const field = frappe.web_form.fields_dict['author_name'];

                    if (field && field.grid) {

                        field.df.data = [];
                        field.grid.grid_rows.forEach(r => r.remove());

                        opts.author_name.forEach(row => {
                            field.grid.add_new_row();

                            const newRow = field.grid.get_row(
                                field.grid.grid_rows.length - 1
                            );

                            if (newRow) {
                                newRow.doc.name1 = row.name1;
                                newRow.doc.brief_bio_of_the_author = row.brief_bio_of_the_author;
                                newRow.refresh();
                            }
                        });

                        field.grid.refresh();
                    }
                }

            }
        });
            
            
        } catch(e) {
            console.error("Error parsing route_options:", e);
        }
    }
    
    function getWordCount(text) {
        if (!text) return 0;
        return text.trim().split(/\s+/).filter(w => w).length;
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
        
        const $emailField = $('input[data-fieldname="email"]');
        const $abstractField = $('textarea[data-fieldname="revise_abstract"]');
        
        if ($emailField.length) {
            $emailField.on('change keyup', function() {
                updateSubmitButtonState();
            });
        }
        
        if ($abstractField.length) {
            $abstractField.on('change keyup', function() {
                updateSubmitButtonState();
            });
        }
        
        updateSubmitButtonState();
    }

    // ==========================================
    // Handle form submission with captcha
    // ==========================================
    $(document).off('click', 'form button[type="submit"]').on('click', 'form button[type="submit"]', function(e) {
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

        const email = frappe.web_form.get_value("email");
        const theme = frappe.web_form.get_value("theme");
        const $btn = $(this);

        const abstractText = $('textarea[data-fieldname="revise_abstract"]').val() || "";
        const abstractCount = getWordCount(abstractText);
        
        if (abstractCount < wordLimits.min_revise_abstract || abstractCount > wordLimits.max_revise_abstract) {
            frappe.msgprint(`Revised Abstract must have between ${wordLimits.min_revise_abstract} - ${wordLimits.max_revise_abstract} words. Current words: ${abstractCount}`);
            return false;
        }
        if (abstractCount > wordLimits.max_revise_abstract) {
            frappe.msgprint(`Revised Abstract must not exceed ${wordLimits.max_revise_abstract} words. Current words: ${abstractCount}`);
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

        // Verify with server (client-side for now)
        frappe.call({
            method: "education.event_management.web_form.full_paper.full_paper.verify_captcha",
            args: { "response": captchaResponse },
            callback: function(r) {
                const isValid = r.message && r.message.verified;
                
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

                // Check for duplicate registration
                frappe.call({
                    method: "education.event_management.web_form.full_paper.full_paper.check_duplicate_registration",
                    args: {
                        email: email,
                        theme: theme
                    },
                    callback: function (r) {
                        if (r.message && r.message.exists) {
                            console.log('Blocking submission - duplicate found');
                            frappe.msgprint("You are already registered for this full paper.");
                            resetCaptcha();
                            $btn.prop('disabled', false).html(originalText);
                        } else {
                            $btn.prop('disabled', false).html(originalText);
                            $('form').submit();
                            // Use requestAnimationFrame for navigation
                            requestAnimationFrame(() => {
                                window.location.href = '/abstract-review-status-check';
                            });
                        }
                    },
                    error: function() {
                        frappe.msgprint("Error checking registration. Please try again.");
                        $btn.prop('disabled', false).html(originalText);
                    }
                });
            },
            error: function() {
                frappe.msgprint("Error verifying captcha. Please try again.");
                $btn.prop('disabled', false).html(originalText);
            }
        });

        return false;
    });

    // ==========================================
    // Initialize
    // ==========================================
    function initialize() {
        console.log("Initializing captcha for full paper...");
        renderCaptcha();
        setupFieldChangeListeners();
    }
    
    initialize();
});
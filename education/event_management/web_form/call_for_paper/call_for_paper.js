// frappe.ready(function () {


// 	const params = new URLSearchParams(window.location.search);
// 	const route_options = params.get("route_options");

// 	let theme = null;

// 	if (route_options) {
// 		try {
// 			const parsedOptions = JSON.parse(route_options);
// 			theme = parsedOptions.theme;
// 			console.log('Current theme:', theme);
// 		} catch (e) {
// 			console.error('Error parsing route_options:', e);
// 		}
// 	}

// 	console.log('Current theme:', theme);
// 	let wordLimits = {
// 		min_words: 0,
// 		max_words: 0,
// 		min_abstract: 0,
// 		max_abstract: 0
// 	};
// 	frappe.call({

// 		method: "education.event_management.doctype.word_limit_settings.word_limit_settings.get_word_limits",
// 		args: {
// 			theme: theme   // ✅ PASS THEME HERE
// 		},
// 		callback: function (r) {
// 			if (r.message) {
// 				wordLimits.min_words = r.message.min_words;
// 				wordLimits.max_words = r.message.max_words;
// 				wordLimits.min_abstract = r.message.min_abstract;
// 				wordLimits.max_abstract = r.message.max_abstract;
// 				const bioField = frappe.web_form.fields_dict['author_name'];

// 				bioField.df.description = `Each author's bio must be between ${wordLimits.min_words} - ${wordLimits.max_words} words.`;


// 				// Append description to the table label in the DOM
// 				const $bioWrapper = $(bioField.wrapper);
// 				console.log('Bio wrapper element:', $bioWrapper);
// 				if ($bioWrapper.length) {
// 					$bioWrapper.find('.word-limit-desc').remove();
// 					$bioWrapper.append(
// 						`<small class="word-limit-desc" style="color:#555; display:block; margin-top:4px;">
//                     Each author's bio must be between ${wordLimits.min_words} - ${wordLimits.max_words} words.
// 					  <span style="color:red">*</span>
//                 </small>`
// 					);
// 				}

// 				// Abstract description
// 				const $abstractField = $('textarea[data-fieldname="abstract"]');
// 				if ($abstractField.next('.word-limit-desc').length === 0) {
// 					$abstractField.after(`<small class="word-limit-desc" style="color: #555;">Write between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words.</small>  <span style="color:red">*</span>`);
// 				} else {
// 					$abstractField.next('.word-limit-desc').text(`Write between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words.`);
// 				}

// 			}

// 		}


// 	});



// 	if (route_options) {
// 		const opts = JSON.parse(decodeURIComponent(route_options));
// 		frappe.web_form.set_value("conference", opts.conference);
// 		frappe.web_form.set_value("theme", opts.theme);
// 	}
// 	function getWordCount(text) {
// 		return text.trim().split(/\s+/).filter(w => w).length;
// 	}

// 	// Intercept the submit button click instead of form submission
// 	$('form button[type="submit"]').on('click', function (e) {
// 		e.preventDefault();
// 		e.stopImmediatePropagation();



// 		const email = frappe.web_form.get_value("email");
// 		const conference = frappe.web_form.get_value("conference");
// 		const title = frappe.web_form.get_value("title");
// 		const theme = frappe.web_form.get_value("theme");

// 		// console.log('Checking for conference:', conference, 'and theme:', theme);
// 		const $btn = $(this);

// 		if (!email || !conference) {
// 			frappe.msgprint("Please fill in both email and conference.");
// 			return false;
// 		}
// 		if (!title) {
// 			frappe.msgprint("Please fill in the title of the paper.");
// 			return false;
// 		}

// 		// const bioText = $('textarea[data-fieldname="brief_bio_of_the_authors"]').val() || "";
// 		const abstractText = $('textarea[data-fieldname="abstract"]').val() || "";
// 		// const bioCount = getWordCount(bioText);
// 		const abstractCount = getWordCount(abstractText);

// 		const bioField = frappe.web_form.fields_dict['author_name'];

// 		// Loop through each row
// 		for (let row of bioField.grid.get_data()) {
// 			const bioText = row.brief_bio_of_the_author || "";
// 			const wordCount = bioText.trim().split(/\s+/).filter(w => w).length;

// 			if (!bioText) {
// 				frappe.msgprint(`Please fill in the brief bio for each author.`);
// 				return false; // stop submission
// 			}

// 			if (wordCount < wordLimits.min_words || wordCount > wordLimits.max_words) {
// 				frappe.msgprint(`Each author's bio must be between ${wordLimits.min_words} and ${wordLimits.max_words} words. Current words: ${wordCount}`);
// 				return false; // stop submission
// 			}
// 			if (wordCount > wordLimits.max_words) {
// 				frappe.msgprint(`Each author's bio must not exceed ${wordLimits.max_words} words. Current words: ${wordCount}`);
// 				return false;
// 			}
// 		}

// 		if (abstractCount < wordLimits.min_abstract || abstractCount > wordLimits.max_abstract) {
// 			frappe.msgprint(`Abstract must have between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words. Current words: ${abstractCount}`);
// 			return false;
// 		}
// 		if (abstractCount > wordLimits.max_abstract) {
// 			frappe.msgprint(`Abstract must not exceed ${wordLimits.max_abstract} words. Current words: ${abstractCount}`);
// 			return false;
// 		}

// 		$btn.prop('disabled', true).html('Checking...');

// 		// Make synchronous-like call using async/await
// 		frappe.call({
// 			method: "education.event_management.web_form.call_for_paper.call_for_paper.check_duplicate_registration",
// 			args: {
// 				email: email,
// 				conference: conference
// 			},
// 			callback: function (r) {
// 				if (r.message.exists) {
// 					// console.log('Blocking submission - duplicate found');
// 					frappe.msgprint("You are already registered for this conference.");
// 					$btn.prop('disabled', false).html('Submit');
// 				} else {
// 					$btn.prop('disabled', false).html('Submit');
// 					// frappe.web_form.doc.workflow_state = "Waiting for Review";
// 					$('form').submit();
// 					setTimeout(function () {
// 						window.location.href = '/conference-announcement';
// 					}, 1000);
// 				}
// 			}
// 		});

// 		return false;
// 	});
// 	const authorField = frappe.web_form.fields_dict['author_name'];
// 	const bioField = frappe.web_form.fields_dict['brief_bio'];
// 	if (!authorField || !bioField) return;
// 	const authorGrid = authorField.grid;
// 	const bioGrid = bioField.grid;
// 	const originalAddNewRow = authorGrid.add_new_row.bind(authorGrid);
// 	authorGrid.add_new_row = function ($row, idx) {
// 		originalAddNewRow($row, idx);
// 		let row_idx = authorGrid.data.length - 1;
// 		bioGrid.add_new_row();
// 		bioGrid.refresh();
// 	};

// });

frappe.ready(function() {
    let captchaWidget = null;
    let captchaRendered = false;
    let captchaVerified = false;

    const params = new URLSearchParams(window.location.search);
    const route_options = params.get("route_options");

    let theme = null;

    if (route_options) {
        try {
            const parsedOptions = JSON.parse(route_options);
            theme = parsedOptions.theme;
          
        } catch (e) {
            console.error('Error parsing route_options:', e);
        }
    }

   
    
    let wordLimits = {
        min_words: 0,
        max_words: 0,
        min_abstract: 0,
        max_abstract: 0
    };

    function waitForElement(selector, callback, maxAttempts = 20) {
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

    function createCaptchaContainer() {
        let container = document.getElementById("recaptcha-container");
        if (container) return container;

        const $form = $('form');
        if (!$form.length) return null;

        const $submitBtn = $('form button[type="submit"]');
        const captchaHtml = `
            <div class="form-group">
                <div class="col-sm-12">
                    <div id="recaptcha-container" style="width:100%;"></div>
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
        const conference = frappe.web_form.get_value("conference");
        const title = frappe.web_form.get_value("title");
        
        const requiredFieldsFilled = email && conference && title;
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

    function verifyWithServer(captchaResponse, callback) {
        // Client-side verification (no server call)
        callback(true);
    }

    frappe.call({
        method: "education.event_management.doctype.word_limit_settings.word_limit_settings.get_word_limits",
        args: { theme: theme },
        callback: function (r) {
            if (r.message) {
                wordLimits.min_words = r.message.min_words;
                wordLimits.max_words = r.message.max_words;
                wordLimits.min_abstract = r.message.min_abstract;
                wordLimits.max_abstract = r.message.max_abstract;
                
                const bioField = frappe.web_form.fields_dict['author_name'];
                if (bioField) {
                    bioField.df.description = `Each author's bio must be between ${wordLimits.min_words} - ${wordLimits.max_words} words.`;

                    const $bioWrapper = $(bioField.wrapper);
                    if ($bioWrapper.length) {
                        $bioWrapper.find('.word-limit-desc').remove();
                        $bioWrapper.append(`
                            <small class="word-limit-desc" style="color:#555; display:block; margin-top:4px;">
                            Each author's bio must be between ${wordLimits.min_words} - ${wordLimits.max_words} words.
                            <span style="color:red">*</span>
                            </small>
                        `);
                    }
                }

                const $abstractField = $('textarea[data-fieldname="abstract"]');
                if ($abstractField.length) {
                    if ($abstractField.next('.word-limit-desc').length === 0) {
                        $abstractField.after(`<small class="word-limit-desc" style="color: #555;">Write between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words.</small>  <span style="color:red">*</span>`);
                    } else {
                        $abstractField.next('.word-limit-desc').text(`Write between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words.`);
                    }
                }
            }
        }
    });


    if (route_options) {
        try {
            const opts = JSON.parse(decodeURIComponent(route_options));
            if (opts.conference) frappe.web_form.set_value("conference", opts.conference);
            if (opts.theme) frappe.web_form.set_value("theme", opts.theme);
        } catch(e) {

        }
    }
    
    function getWordCount(text) {
        if (!text) return 0;
        return text.trim().split(/\s+/).filter(w => w).length;
    }

    function setupFieldChangeListeners() {
        if (!frappe.web_form) {
            // Wait for web_form to be available
            const observer = new MutationObserver(() => {
                if (frappe.web_form && typeof frappe.web_form.get_value === 'function') {
                    observer.disconnect();
                    setupFieldChangeListeners();
                }
            });
            observer.observe(document.body, { attributes: true, childList: true, subtree: true });
            return;
        }
        
        const requiredFields = ['email', 'conference', 'title'];
        
        requiredFields.forEach(fieldname => {
            const field = frappe.web_form.get_field(fieldname);
            if (field && field.wrapper) {
                const observer = new MutationObserver(() => {
                    updateSubmitButtonState();
                });
                observer.observe(field.wrapper, { attributes: true, childList: true, subtree: true });
                
                $(field.wrapper).find('input, select').on('change keyup', function() {
                    updateSubmitButtonState();
                });
            }
        });
        
        updateSubmitButtonState();
    }


    $(document).off('click', 'form button[type="submit"]').on('click', 'form button[type="submit"]', function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        if (!captchaVerified) {
            frappe.msgprint({
                title: "Verification Required",
                message: 'Please complete the "I am not a robot" verification.',
                indicator: "red"
            });
            return false;
        }

        const email = frappe.web_form.get_value("email");
        const conference = frappe.web_form.get_value("conference");
        const title = frappe.web_form.get_value("title");
        const country = frappe.web_form.get_value("nationality")
        const cid = frappe.web_form.get_value("passport__cid_number")

        const $btn = $(this);

        if (!email || !conference) {
            frappe.msgprint("Please fill in both email and conference.");
            return false;
        }
        if (!title) {
            frappe.msgprint("Please fill in the title of the paper.");
            return false;
        }
        if (country=="Bhutan"){
            if (cid && cid.length !== 11) {
                frappe.msgprint(__("CID number must be 11 digits."));
                return false;
            }
        }


        const abstractText = $('textarea[data-fieldname="abstract"]').val() || "";
        const abstractCount = getWordCount(abstractText);
        const bioField = frappe.web_form.fields_dict['author_name'];

        if (bioField && bioField.grid) {
            for (let row of bioField.grid.get_data()) {
                const bioText = row.brief_bio_of_the_author || "";
                const wordCount = getWordCount(bioText);

                if (!bioText) {
                    frappe.msgprint(`Please fill in the brief bio for each author.`);
                    return false;
                }

                if (wordCount < wordLimits.min_words || wordCount > wordLimits.max_words) {
                    frappe.msgprint(`Each author's bio must be between ${wordLimits.min_words} and ${wordLimits.max_words} words. Current words: ${wordCount}`);
                    return false;
                }
            }
        }

        if (abstractCount < wordLimits.min_abstract || abstractCount > wordLimits.max_abstract) {
            frappe.msgprint(`Abstract must have between ${wordLimits.min_abstract} - ${wordLimits.max_abstract} words. Current words: ${abstractCount}`);
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

            frappe.call({
                method: "education.event_management.web_form.call_for_paper.call_for_paper.check_duplicate_registration",
                args: { email: email, conference: conference },
                callback: function (r) {
                    if (r.message && r.message.exists) {
                        frappe.msgprint("You are already registered for this conference.");
                        resetCaptcha();
                        $btn.prop('disabled', false).html(originalText);
                    } else {
                        $btn.prop('disabled', false).html(originalText);
                        $('form').submit();
                        // Use requestAnimationFrame instead of setTimeout for navigation
                        requestAnimationFrame(() => {
                            window.location.href = '/conference-announcement';
                        });
                    }
                },
                error: function() {
                    frappe.msgprint("Error checking registration. Please try again.");
                    $btn.prop('disabled', false).html(originalText);
                }
            });
        });

        return false;
    });


    function setupGridSync() {
        const authorField = frappe.web_form.fields_dict['author_name'];
        const bioField = frappe.web_form.fields_dict['brief_bio'];
        
        if (authorField && bioField && authorField.grid && bioField.grid) {
            const authorGrid = authorField.grid;
            const bioGrid = bioField.grid;
            const originalAddNewRow = authorGrid.add_new_row.bind(authorGrid);
            
            authorGrid.add_new_row = function ($row, idx) {
                originalAddNewRow($row, idx);
                if (bioGrid && bioGrid.add_new_row) {
                    bioGrid.add_new_row();
                    bioGrid.refresh();
                }
            };
        } else {
            requestAnimationFrame(() => setupGridSync());
        }
    }


    function initialize() {
        renderCaptcha();
        setupFieldChangeListeners();
        setupGridSync();
    }
    
    initialize();
});
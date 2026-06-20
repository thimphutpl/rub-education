
frappe.ready(function () {
    let captchaWidget = null;
    let captchaRendered = false;
    let captchaVerified = false;
    let perDayAmount = 0;

    function renderCaptcha() {
        if (captchaRendered && captchaWidget !== null) {
            try {
                if (
                    typeof grecaptcha !== "undefined" &&
                    grecaptcha.getResponse(captchaWidget)
                ) {
                    console.log("Captcha already valid");
                    return;
                }
            } catch (e) {
                captchaRendered = false;
            }
        }

        let container = document.getElementById("recaptcha-container");

        if (!container) {
            const $form = $("form");

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
                waitForFormAndRender();
                return;
            }
        }

        if (typeof grecaptcha === "undefined") {
            if (!document.querySelector('script[src*="recaptcha/api.js"]')) {
                const script = document.createElement("script");
                script.src = "https://www.google.com/recaptcha/api.js?render=explicit";
                script.async = true;
                script.defer = true;
                script.onload = function () {
                    renderCaptcha();
                };
                document.head.appendChild(script);
            } else {
                waitForGrecaptchaAndRender();
            }

            return;
        }

        if (captchaWidget !== null) {
            try {
                grecaptcha.reset(captchaWidget);
                return;
            } catch (e) {
                captchaWidget = null;
            }
        }

        try {
            container.innerHTML = "";

            captchaWidget = grecaptcha.render(container, {
                sitekey: "6Lery8osAAAAAIvNfDE7w9rNEA5etF5cGkWlD4tY",

                callback: function () {
                    console.log("✅ Captcha verified");
                    captchaRendered = true;
                    captchaVerified = true;
                    updateSubmitButtonState();
                },

                "expired-callback": function () {
                    console.log("⚠️ Captcha expired");
                    captchaWidget = null;
                    captchaRendered = false;
                    captchaVerified = false;
                    enableSubmitButton(false);
                    renderCaptcha();
                },

                "error-callback": function () {
                    console.error("❌ Captcha error");
                    captchaWidget = null;
                    captchaRendered = false;
                    captchaVerified = false;
                    enableSubmitButton(false);
                }
            });

            console.log("✅ reCAPTCHA rendered");
            enableSubmitButton(false);
        } catch (error) {
            console.error("Captcha render error:", error);
            requestAnimationFrame(function () {
                renderCaptcha();
            });
        }
    }

    function enableSubmitButton(enable) {
        const $submitBtn = $('form button[type="submit"]');

        if (!$submitBtn.length) {
            return;
        }

        if (enable) {
            $submitBtn.prop("disabled", false);
            $submitBtn.css("opacity", "1");
        } else {
            $submitBtn.prop("disabled", true);
            $submitBtn.css("opacity", "0.5");
        }
    }

    function updateSubmitButtonState() {
        if (!frappe.web_form || typeof frappe.web_form.get_value !== "function") {
            enableSubmitButton(false);
            return;
        }

        const email = frappe.web_form.get_value("email");
        const venue = frappe.web_form.get_value("venue");
        const from_date = frappe.web_form.get_value("from_date");
        const from_time = frappe.web_form.get_value("from_time");
        const to_date = frappe.web_form.get_value("to_date");
        const to_time = frappe.web_form.get_value("to_time");

        const requiredFieldsFilled =
            email &&
            venue &&
            from_date &&
            from_time &&
            to_date &&
            to_time;

        enableSubmitButton(requiredFieldsFilled && captchaVerified);
    }

    function waitForFormAndRender() {
        const observer = new MutationObserver(function (mutations, obs) {
            const $form = $("form");

            if ($form.length) {
                obs.disconnect();
                renderCaptcha();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    function waitForGrecaptchaAndRender() {
        const checkGrecaptcha = function () {
            if (typeof grecaptcha !== "undefined") {
                renderCaptcha();
                return true;
            }

            return false;
        };

        if (!checkGrecaptcha()) {
            const observer = new MutationObserver(function () {
                if (checkGrecaptcha()) {
                    observer.disconnect();
                }
            });

            observer.observe(document.head, {
                childList: true,
                subtree: true
            });
        }
    }

    function getCaptchaResponse() {
        if (captchaWidget !== null && typeof grecaptcha !== "undefined") {
            try {
                const response = grecaptcha.getResponse(captchaWidget);
                return response && response.length > 0 ? response : null;
            } catch (e) {
                return null;
            }
        }

        return null;
    }

    function resetCaptcha() {
        if (captchaWidget !== null && typeof grecaptcha !== "undefined") {
            try {
                grecaptcha.reset(captchaWidget);
                captchaRendered = false;
                captchaVerified = false;
                enableSubmitButton(false);
            } catch (e) {
                captchaWidget = null;
                renderCaptcha();
            }
        }
    }

    function verifyWithServer(captchaResponse, callback) {
        frappe.call({
            method: "education.event_management.web_form.hall_booking.hall_booking.verify_captcha",
            args: {
                response: captchaResponse
            },
            callback: function (r) {
                if (r.message && r.message.verified) {
                    callback(true);
                } else {
                    callback(false);
                }
            },
            error: function () {
                callback(false);
            }
        });
    }

    function getHallDataFromURL() {
        const params = new URLSearchParams(window.location.search);
        const name = params.get("venue");

        if (!name) {
            return;
        }

        frappe.call({
            method: "education.event_management.web_form.hall_booking.hall_booking.get_hall_data",
            args: {
                name: name
            },
            callback: function (r) {
                if (!r.message || r.message.error) {
                    frappe.msgprint(r.message?.error || "Error loading hall booking data");
                    return;
                }

                const opts = r.message;

                frappe.web_form.set_value("venue", opts.venue);
                frappe.web_form.set_value("company", opts.company);
                frappe.web_form.set_value("branch", opts.branch);
                frappe.web_form.set_value("cost_center", opts.cost_center);
                frappe.web_form.set_value("amount", opts.amount);
                frappe.web_form.set_value("account_number", opts.account_number);
                frappe.web_form.set_value("qr_code", opts.qr_code);

                if (opts.amount) {
                    perDayAmount = parseFloat(opts.amount);
                }

                if (opts.qr_code) {
                    const $qrField = $(`[data-fieldname="qr_code"] .control-value`);

                    if ($qrField.length) {
                        $qrField.html(`
                            <img src="${opts.qr_code}"
                                 style="max-width:200px; border:1px solid #ddd; padding:5px; border-radius:8px;" />
                        `);
                    } else {
                        frappe.web_form.set_value("qr_code", opts.qr_code);
                    }
                }

                updateSubmitButtonState();
            }
        });
    }

    function parseDate(dateValue) {
        if (!dateValue) {
            return null;
        }

        if (typeof dateValue === "string") {
            const parts = dateValue.split("-");

            if (parts.length === 3) {
                if (parts[0].length === 4) {
                    return new Date(parts[0], parts[1] - 1, parts[2]);
                } else {
                    return new Date(parts[2], parts[1] - 1, parts[0]);
                }
            }
        }

        return new Date(dateValue);
    }

    function calculateBooking(fromDate, toDate, perDayAmount) {
        const from = parseDate(fromDate);
        const to = parseDate(toDate);

        if (!from || !to || isNaN(from.getTime()) || isNaN(to.getTime())) {
            return {
                total_days: 0,
                total_amount: 0
            };
        }

        const diffTime = Math.abs(to - from);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
        const total_amount = diffDays * perDayAmount;

        return {
            total_days: diffDays,
            total_amount: total_amount
        };
    }

    function calculateTotal() {
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
    }

    function combineDateTime(dateValue, timeValue) {
        if (!dateValue || !timeValue) {
            return null;
        }

        const date = parseDate(dateValue);

        if (!date || isNaN(date.getTime())) {
            return null;
        }

        const timeParts = timeValue.split(":");
        const hours = parseInt(timeParts[0] || "0", 10);
        const minutes = parseInt(timeParts[1] || "0", 10);
        const seconds = parseInt(timeParts[2] || "0", 10);

        date.setHours(hours, minutes, seconds, 0);

        return date;
    }

    function validateDateTimeRange() {
        const from_date = frappe.web_form.get_value("from_date");
        const from_time = frappe.web_form.get_value("from_time");
        const to_date = frappe.web_form.get_value("to_date");
        const to_time = frappe.web_form.get_value("to_time");

        if (!from_date || !from_time || !to_date || !to_time) {
            return true;
        }

        const fromDateTime = combineDateTime(from_date, from_time);
        const toDateTime = combineDateTime(to_date, to_time);

        if (!fromDateTime || !toDateTime) {
            frappe.msgprint({
                title: "Invalid Date/Time",
                message: "Please enter valid From Date, From Time, To Date and To Time.",
                indicator: "red"
            });

            return false;
        }

        if (fromDateTime >= toDateTime) {
            frappe.msgprint({
                title: "Invalid Booking Time",
                message: "To Date/Time must be greater than From Date/Time.",
                indicator: "red"
            });

            return false;
        }

        return true;
    }

    function setupFieldChangeListeners() {
        if (!frappe.web_form) {
            return;
        }

        frappe.web_form.on("from_date", function () {
            calculateTotal();
            updateSubmitButtonState();
        });

        frappe.web_form.on("to_date", function () {
            calculateTotal();
            updateSubmitButtonState();
        });

        frappe.web_form.on("from_time", function () {
            updateSubmitButtonState();
        });

        frappe.web_form.on("to_time", function () {
            updateSubmitButtonState();
        });

        frappe.web_form.on("amount", function () {
            calculateTotal();
        });

        frappe.web_form.on("email", function () {
            updateSubmitButtonState();
        });

        frappe.web_form.on("venue", function () {
            updateSubmitButtonState();
        });

        $(document).on("change keyup", "input, select, textarea", function () {
            updateSubmitButtonState();
        });

        updateSubmitButtonState();
    }

    function setupSubmitButton() {
        $(document).off("click", 'form button[type="submit"]');

        $(document).on("click", 'form button[type="submit"]', function (e) {
            e.preventDefault();

            const $btn = $(this);
            const originalText = $btn.html();

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
            const from_time = frappe.web_form.get_value("from_time");
            const to_date = frappe.web_form.get_value("to_date");
            const to_time = frappe.web_form.get_value("to_time");

            if (!email || !venue || !from_date || !from_time || !to_date || !to_time) {
                frappe.msgprint({
                    title: "Missing Details",
                    message: "Please fill Venue, Email, From Date, From Time, To Date and To Time.",
                    indicator: "red"
                });

                return false;
            }

            if (!validateDateTimeRange()) {
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

            $btn.prop("disabled", true).html('<i class="fa fa-spinner fa-spin"></i> Verifying...');

            verifyWithServer(captchaResponse, function (isValid) {
                if (!isValid) {
                    frappe.msgprint({
                        title: "Verification Failed",
                        message: "Captcha verification failed. Please try again.",
                        indicator: "red"
                    });

                    resetCaptcha();
                    $btn.prop("disabled", false).html(originalText);
                    return;
                }

                $btn.html('<i class="fa fa-spinner fa-spin"></i> Checking availability...');

                frappe.call({
                    method: "education.event_management.web_form.hall_booking.hall_booking.check_duplicate_venue",
                    args: {
                        email: email,
                        venue: venue,
                        from_date: from_date,
                        from_time: from_time,
                        to_date: to_date,
                        to_time: to_time
                    },
                    callback: function (r) {
                        if (r.message && r.message.conflict) {
                            let msg = r.message.message || "This venue is already booked during this time.";

                            if (r.message.booked_from && r.message.booked_to) {
                                msg = `This venue is already booked from <b>${r.message.booked_from}</b> to <b>${r.message.booked_to}</b>.`;
                            }

                            frappe.msgprint({
                                title: "Booking Conflict",
                                message: msg,
                                indicator: "red"
                            });

                            resetCaptcha();
                            $btn.prop("disabled", false).html(originalText);
                            return;
                        }

                        $btn.html('<i class="fa fa-spinner fa-spin"></i> Submitting...');

                        frappe.web_form.save();
                    },
                    error: function () {
                        frappe.msgprint({
                            title: "Error",
                            message: "Error checking availability. Please try again.",
                            indicator: "red"
                        });

                        $btn.prop("disabled", false).html(originalText);
                    }
                });
            });

            return false;
        });
    }

    function initialize() {
        console.log("Initializing Hall Booking Web Form...");

        getHallDataFromURL();
        renderCaptcha();
        setupFieldChangeListeners();
        setupSubmitButton();
        calculateTotal();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
});

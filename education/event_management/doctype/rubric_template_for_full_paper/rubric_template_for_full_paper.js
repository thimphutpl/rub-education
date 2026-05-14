// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rubric Template For Full Paper", {
	refresh(frm) {
         frm.add_custom_button('Start Tour', () => {
            const tour_name = 'Rubric Template For Full Paper';

            frm.tour.init({ tour_name }).then(() => {
                frm.tour.start();
            });
        });

	},
});

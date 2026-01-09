frappe.ui.form.on('Room', {
    onload: function(frm) {
        frm.set_query("cost_center", function (doc) {
			return {
				filters: {
					company: doc.company,
					is_group: 0,
					disabled: 0,
				},
			};
		});
    }
})

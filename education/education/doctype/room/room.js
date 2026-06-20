frappe.ui.form.on('Room', {
    onload: function(frm) {
        frm.set_query("cost_center", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0,
					disabled: 0,
				},
			};
		});
		frm.set_query("branch", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0,
					disabled: 0,
				},
			};
		});
    },
	setup:function(frm){
		frm.set_query("branch", function(){
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0,
					disabled: 0,
				}
			}
		});
		frm.set_query("cost_center", function(){
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0,
					disabled: 0,
				}
			}
		});

	},
	
	refresh(frm) { 
        frm.set_query("branch", function(){
			return {
				filters: {
					company: frm.doc.company,
					disabled: 0,
				}
			}
		});
		frm.set_query("cost_center", function(){
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0,
					disabled: 0,
				}
			}
		});
	}	
})

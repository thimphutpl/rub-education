// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Timetable Constraints", {
	setup:function(frm){
        frm.set_query("academic_term",function(){
            return{
                filters: {
                    college:frm.doc.college
                }
            }
        })
       
    }
});

# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.desk.reportview import get_match_cond
from frappe.model.mapper import get_mapped_doc
from erpnext.custom_workflow import validate_workflow_states, notify_workflow_states


class AnnualProgrammeMonitoringReport(Document):

	def validate(self):
		validate_workflow_states(self)
		self.validate_references()
		self.validate_permitted_users()
		self.update_references()

	def validate_references(self):
		if self.apmr_type == "Programme Level Compilation (APMR Development)":
			if not self.module_level_ref:
				frappe.throw("You cannot create this Document without Module Level Input Document reference")
		elif self.apmr_type == "College Level Review":
			if not self.programme_level_ref:
				frappe.throw("You cannot create this Document without Programme Level Document reference")
		elif self.apmr_type == "University Level Review & Recommendation":
			if not self.college_level_ref:
				frappe.throw("You cannot create this Document without College Level Document reference")
	@frappe.whitelist()
	def validate_permitted_users(self, client_side = 0):
		permitted_users = []
		if client_side == 0:
			for pu in self.permitted_users:
				permitted_users.append(pu.user)
		else:
			for pu in self.to:
				permitted_users.append(pu.user)
		if frappe.session.user not in permitted_users and self.apmr_type != "Module Level Input":
			if frappe.session.user != "Administrator":
				if client_side == 0 and self.permitted_users:
					if self.apmr_type == "University Level Review & Recommendation":
						if self.get("__islocal"):
							frappe.throw("You are not allowed to interact with this Document.<br>Allowed Users: <br> {}".format(", ".join(str(idx+1)+". "+a for idx, a in enumerate(permitted_users))))
					else:
						frappe.throw("You are not allowed to interact with this Document.<br>Allowed Users: <br> {}".format(", ".join(str(idx+1)+". "+a for idx, a in enumerate(permitted_users))))
				else:
					return "You are not allowed to interact with this Document.<br>Allowed Users: <br> {}".format(", ".join(str(idx+1)+". "+a for idx, a in enumerate(permitted_users)))

	def update_references(self):
		if self.apmr_type == "Programme Level Compilation (APMR Development)":
			self.programme_level_ref = None
			self.college_level_ref = None
		elif self.apmr_type == "College Level Review":
			self.module_level_ref = None
			self.college_level_ref = None
		elif self.apmr_type == "University Level Review & Recommendation":
			self.module_level_ref = None
			self.programme_level_ref = None
		else:
			self.module_level_ref = None
			self.programme_level_ref = None
			self.college_level_ref = None

	@frappe.whitelist()
	def check_reference(self):
		if self.apmr_type == "Programme Level Compilation (APMR Development)":
			next_doc = "College Level Review"
			ref_field = "programme_level_ref"
			reference = self.module_level_ref
		elif self.apmr_type == "College Level Review":
			next_doc = "University Level Review & Recommendation"
			ref_field = "college_level_ref"
			reference = self.programme_level_ref
		else:
			next_doc = "Programme Level Compilation (APMR Development)"
			ref_field = "module_leve_ref"
			reference = None
		return self.docstatus, self.apmr_type, reference, next_doc, ref_field

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_program_module(doctype, txt, searchfield, start, page_len, filters):
	if filters.get("validate") == 1:
		# if not filters.get("program"):
		# 	frappe.msgprint(_("Please select a Programme."))
		# 	return []
		if not filters.get("college"):
			frappe.msgprint(_("Please select a College."))
			return []
		# if not filters.get("semester"):
		# 	frappe.msgprint(_("Please select a Semester."))
		# 	return []
	# frappe.throw(str(txt))

	doctype = "Module"
	return frappe.db.sql(
		"""select m.name as course, m.module_title as course_name from `tabModule` m, `tabModule College` mc
        where  m.name = mc.parent and m.name like %(txt)s and mc.college = %(college)s
        order by
            if(locate(%(_txt)s, m.name), locate(%(_txt)s, m.name), 99999),
            m.name asc
        limit {start}, {page_len}""".format(
			match_cond=get_match_cond(doctype), start=start, page_len=page_len
		),
		{
			"txt": "%{0}%".format(txt),
			"_txt": txt.replace("%", ""),
			"college": filters["college"],
		},
	)

@frappe.whitelist()
def make_next_doc(source_name, target_doc=None, args=None):
	if args is None:
		args = {}
	if isinstance(args, str):
		args = json.loads(args)

	def set_missing_values(source, target_doc):
		target_doc.apmr_type = frappe.flags.args.get("next_doc")
		target_doc.permitted_users = source.to
		setattr(target_doc, frappe.flags.args.get("ref_field"), source.name)

	def select_item(d):
		filtered_items = args.get("filtered_children", [])
		child_filter = d.name in filtered_items if filtered_items else True

		qty = d.received_qty or d.ordered_qty

		return qty < d.stock_qty and child_filter

	doclist = get_mapped_doc(
		"Annual Programme Monitoring Report",
		source_name,
		{
			"Annual Programme Monitoring Report": {
				"doctype": "Annual Programme Monitoring Report",
				"validation": {"docstatus": ["=", 1]},
			},
		},
		target_doc,
		set_missing_values,
	)

	doclist.set_onload("load_after_mapping", False)
	return doclist

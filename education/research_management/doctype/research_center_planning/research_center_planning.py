# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ResearchCenterPlanning(Document):
	pass

# @frappe.whitelist()
# def make_research_proposal(source_name, target_doc=None):
#     def set_missing_values(source, target):
#         target.call_for_research = source.name

#     return get_mapped_doc(
#         "Research Center Planning",
#         source_name,
#         {
#             "Call for Research": {  
#                 "doctype": "Research Proposal",
#                 "field_map": {
#                     "grant_amount": "grant_amount",
#                     "topic_of_the_research_call": "topic_of_the_research_call",
#                     "grant_type": "grant_type",
#                     "research_type":"research_type"
#                 },
#             }
#         },
#         target_doc,
#         set_missing_values,
#     )

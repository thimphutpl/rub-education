# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WordLimitSettings(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_word_limits():
    record = frappe.get_all("Word Limit Settings", limit=1, fields=["min_words", "max_words", "min_abstract", "max_abstract", "min_revise_abstract", "max_revise_abstract"])
    if record:
        return record[0]
    else:
        return {
            "min_words": 0,
            "max_words": 0,
            "min_abstract": 0,
            "max_abstract": 0,
            "min_revise_abstract": 0,
            "max_revise_abstract": 0
        }
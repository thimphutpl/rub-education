# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class WebPage(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from frappe.website.doctype.web_page_block.web_page_block import WebPageBlock

		breadcrumbs: DF.Code | None
		content_type: DF.Literal["Rich Text", "Markdown", "HTML", "Page Builder", "Slideshow"]
		context_script: DF.Code | None
		css: DF.Code | None
		dynamic_route: DF.Check
		dynamic_template: DF.Check
		enable_comments: DF.Check
		end_date: DF.Datetime | None
		full_width: DF.Check
		header: DF.HTMLEditor | None
		idx: DF.Int
		insert_style: DF.Check
		javascript: DF.Code | None
		main_section: DF.TextEditor | None
		main_section_html: DF.HTMLEditor | None
		main_section_md: DF.MarkdownEditor | None
		meta_description: DF.SmallText | None
		meta_image: DF.AttachImage | None
		meta_title: DF.Data | None
		module: DF.Link | None
		page_blocks: DF.Table[WebPageBlock]
		published: DF.Check
		route: DF.Data | None
		show_sidebar: DF.Check
		show_title: DF.Check
		slideshow: DF.Link | None
		start_date: DF.Datetime | None
		text_align: DF.Literal["Left", "Center", "Right"]
		title: DF.Data
		website_sidebar: DF.Link | None
	# end: auto-generated types
	pass

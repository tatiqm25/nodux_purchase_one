# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Nodux Purchase One",
			"color": "darkgrey",
			"icon": "octicon octicon-file-directory",
			"type": "module",
			"label": _("Nodux Purchase One")
		},

		{
			"module_name": "Nodux Purchase One",
			"_doctype": "Purchases Invoice One",
			"color": "#f39c12",
			"icon": "octicon octicon-package",
			"type": "link",
			"link": "List/Purchases Invoice One"
		}
	]

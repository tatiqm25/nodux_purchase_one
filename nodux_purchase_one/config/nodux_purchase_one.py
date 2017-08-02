from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Reportes Compras"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "report",
					"name": "Report Payable",
					"doctype": "Purchases Invoice One",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Report Purchases",
					"doctype": "Purchases Invoice One",
					"is_query_report": True
				}

			]
		}
	]

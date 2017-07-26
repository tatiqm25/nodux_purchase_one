# -*- coding: utf-8 -*-
# Copyright (c) 2015, NODUX and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from frappe import _

class PurchasesInvoiceOne(Document):
	def before_save(self):
		self.docstatus = 1
		self.status = "Confirmed"
		self.residual_amount = self.total
		for line in self.lines:
			product = frappe.get_doc("Item", line.item_code)
			if product.total == None:
				product.total = line.qty
			else:
				product.total = product.total + line.qty
				product.cost_price = line.unit_price
				product.save()

	# def update_to_confirmed(self):
	# 	self.docstatus = 1
	# 	self.save()
	# 	self.status = "Confirmed"
	# 	self.residual_amount = self.total
	# 	for line in self.lines:
	# 		product = frappe.get_doc("Item", line.item_code)
	# 		if product.total == None:
	# 			product.total = line.qty
	# 		else:
	# 			product.total = product.total + line.qty
	# 			product.cost_price = line.unit_price
	# 			product.save()
	# 	self.save()

	def update_to_anulled(self):
		#agregar permisos de usuario
		for line in self.lines:
			product = frappe.get_doc("Item", line.item_code)
			if product.total == None:
				product.total = (line.qty - 1)
			else:
				product.total = product.total - line.qty
				product.save()

		self.status="Anulled"
		self.save()

	def update_to_pay(self, args=None):
		supplier = args.get('supplier')
		total = args.get('total')

		if self.paid_amount > 0:
			self.paid_amount = self.paid_amount + total
		else:
			self.paid_amount = total

		if self.residual_amount > 0:
			self.residual_amount = self.residual_amount - total

		if self.paid_amount == self.total:
			self.status ="Done"
		else:
			self.status = "Confirmed"
		self.save()

	def get_prices(self):
		subtotal = 0
		for line in lines:
			if line.subtotal:
				base_imponible += line.subtotal
		ret = {
			'base_imponible'		: base_imponible
		}
		return ret

	def get_item_details(self, args=None, for_update=False):
		item = frappe.db.sql("""select stock_uom, description, image, item_name,
			cost_price, cost_price_with_tax, barcode, tax from `tabItem`
			where name = %s
				and disabled=0
				and (end_of_life is null or end_of_life='0000-00-00' or end_of_life > %s)""",
			(args.get('item_code'), nowdate()), as_dict = 1)
		if not item:
			frappe.throw(_("Item {0} is not active or end of life has been reached").format(args.get("item_code")))

		item = item[0]

		ret = {
			'uom'			      	: item.stock_uom,
			'description'		  	: item.description,
			'item_name' 		  	: item.item_name,
			'qty'					: 1,
			'barcode'				: item.barcode,
			'unit_price'			: item.cost_price,
			'unit_price_with_tax'	: item.cost_price_with_tax,
			'subtotal'				: item.cost_price_with_tax
		}

		# update uom
		if args.get("uom") and for_update:
			ret.update(get_uom_details(args.get('item_code'), args.get('uom'), args.get('qty')))
		return ret

	def update_prices(self, args=None, for_update=False):
		item = frappe.db.sql("""select tax from `tabItem`
			where name = %s
				and disabled=0
				and (end_of_life is null or end_of_life='0000-00-00' or end_of_life > %s)""",
			(args.get('item_code'), nowdate()), as_dict = 1)

		item = item[0]

		if args.get("qty") and args.get("unit_price"):
			qty = args.get("qty")
			unit_price = args.get("unit_price")

			if item.tax == "IVA 0%":
				unit_price_with_tax = unit_price
				subtotal = qty * unit_price
			elif item.tax == "IVA 12%":
				unit_price_with_tax= unit_price * (1.12)
				subtotal = unit_price_with_tax * qty
			elif item.tax == "IVA 14%":
				unit_price_with_tax = unit_price * (1.14)
				subtotal = unit_price_with_tax * qty
			elif item.tax == "No aplica impuestos":
				unit_price_with_tax = unit_price
				subtotal = qty * unit_price

		ret = {
			'subtotal'				: subtotal,
			'unit_price_with_tax'	: unit_price_with_tax
		}

		return ret

	def get_item_code(self, args=None, serial_no=None):
		item = frappe.db.sql("""select stock_uom, description, image, item_name,
			cost_price, name, cost_price_with_tax from `tabItem`
			where barcode = %s
				and disabled=0
				and (end_of_life is null or end_of_life='0000-00-00' or end_of_life > %s)""",
			(args.get('barcode'), nowdate()), as_dict = 1)

		if not item:
			frappe.throw(_("No existe producto con codigo de barra {0}").format(args.get("barcode")))

		item = item[0]

		ret = {
			'uom'			      	: item.stock_uom,
			'description'		  	: item.description,
			'item_name' 		  	: item.item_name,
			'item_code'				: item.name,
			'qty'					: 1,
			'unit_price'			: item.cost_price,
			'unit_price_with_tax'	: item.cost_price_with_tax,
			'subtotal'				: item.cost_price_with_tax
		}

		return ret

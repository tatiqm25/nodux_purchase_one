// Copyright (c) 2016, NODUX and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchases Invoice One', {
	onload: function(frm) {
		var me = this;
		if (!frm.doc.status)
			frm.doc.status = 'Draft';
		//frm.disable_save();
	},

	refresh: function(frm) {
		// if (frm.doc.status == 'Draft') {
		// 	frm.add_custom_button(__("Confirm"), function() {
		// 		frm.events.update_to_confirmed(frm);
		// 	}).addClass("btn-primary");
		// }

		if (frm.doc.status == 'Draft' && frm.doc.docstatus=='1') {
			frm.add_custom_button(__("Pay"), function() {
				frm.events.update_to_pay(frm);
			}).addClass("btn-primary");
		}

		if (frm.doc.status == 'Confirmed' && frm.doc.docstatus=='1') {
			frm.add_custom_button(__('Pay'), function(){
				frm.events.update_to_pay(frm);
			}).addClass("btn-primary");
		}

		if (frm.doc.status == 'Done' && frm.doc.docstatus=='1') {
			frm.add_custom_button(__("Anull"), function() {
				frm.events.update_to_anulled(frm);
			}).addClass("btn-primary");
		}
		frm.refresh_fields();

	},

	supplier: function(frm) {
		if (frm.doc.supplier){
			frm.set_value("supplier_name", frm.doc.supplier);
			frm.set_value("due_date", frappe.datetime.nowdate());
		}
		frm.refresh_fields();
	},

	lines: function(frm){
		var base_imponible = 0;
		var total_taxes = 0;
		var total = 0;
		if (frm.doc.lines){
			for (line in frm.doc.lines){
				base_imponible += line.subtotal;
			}
			total = total_taxes + base_imponible;
		}
		frm.set_value("base_imponible", base_imponible);
		frm.set_value("total_taxes", total_taxes);
		frm.set_value("total", total);
		frm.set_value("residual_amount", total);
		frm.set_value("paid_amount", 0);

		frm.refresh_fields();
		frm.refresh();
	},

	update_to_confirmed: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "update_to_confirmed",
			freeze: true,
			callback: function(r) {
				frm.refresh_fields();
				frm.refresh();
			}
		});
		frm.refresh_fields();
		frm.refresh();
	},

	update_to_anulled: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "update_to_anulled",
			freeze: true,
			callback: function(r) {
				frm.refresh_fields();
				frm.refresh();
			}
		});
		frm.refresh_fields();
		frm.refresh();
	},

	update_to_pay: function(frm) {
		var d = new frappe.ui.Dialog({
			title: __("Payment"),
			fields: [
				{"fieldname":"supplier", "fieldtype":"Link", "label":__("Supplier"),
					options:"Supplier", reqd: 1, label:"Supplier", "default":frm.doc.supplier_name},
				{"fieldname":"total", "fieldtype":"Currency", "label":__("Total Amount"),
					label:"Total Amount", "default":frm.doc.residual_amount},
				{fieldname:"pay", "label":__("Pay"), "fieldtype":"Button"}]
		});
		d.get_input("pay").on("click", function() {
			var values = d.get_values();
			if(!values) return;
			if(values["total"] < 0) frappe.throw("Ingrese monto a pagar");
			if(values["total"] > frm.doc.total) frappe.throw("Monto a pagar no puede ser mayor al monto total de venta");
			return frappe.call({
				doc: frm.doc,
				method: "update_to_pay",
				args: values,
				freeze: true,
				callback: function(r) {
					d.hide();
					frm.refresh_fields();
					frm.refresh();
				}
			})
		});

		d.show();
		frm.refresh_fields();
		frm.refresh();
	}

});

frappe.ui.form.on('Purchases Invoice Item One', {
	item_name: function(frm, cdt, cdn) {
		var item = frappe.get_doc(cdt, cdn);
		if(!item.item_name) {
			item.item_name = "";
		} else {
			item.item_name = item.item_name;
		}
	},

	barcode: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.barcode) {
			args = {
				'barcode'			: d.barcode
			};
			return frappe.call({
				doc: cur_frm.doc,
				method: "get_item_code",
				args: args,
				callback: function(r) {
					if(r.message) {
						var d = locals[cdt][cdn];
						$.each(r.message, function(k, v) {
							d[k] = v;
						});
						calculate_base_imponible(frm);
						refresh_field("items");
						cur_frm.refresh_fields();
					}
				}
			});
		}
		cur_frm.refresh_fields();

	},

	item_code: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.item_code) {
			args = {
				'item_code'			: d.item_code,
				'qty'				: d.qty
			};
			return frappe.call({
				doc: cur_frm.doc,
				method: "get_item_details",
				args: args,
				callback: function(r) {
					if(r.message) {
						var d = locals[cdt][cdn];
						$.each(r.message, function(k, v) {
							d[k] = v;
						});
						calculate_base_imponible(frm);

						refresh_field("items");
						cur_frm.refresh_fields();
					}
				}
			});
		}
	},

	qty: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.qty) {
			args = {
				'item_code'			: d.item_code,
				'qty'				: d.qty,
				'unit_price': d.unit_price
			};
			return frappe.call({
				doc: cur_frm.doc,
				method: "update_prices",
				args: args,
				callback: function(r) {
					if(r.message) {
						var d = locals[cdt][cdn];
						$.each(r.message, function(k, v) {
							d[k] = v;
						});
						calculate_base_imponible(frm);
						refresh_field("items");
						cur_frm.refresh_fields();
					}
				}
			});
		}
	},

	unit_price: function(frm, cdt, cdn){
		// if user changes the rate then set margin Rate or amount to 0
		var d = locals[cdt][cdn];
		if(d.item_code){
			args = {
				'item_code'			: d.item_code,
				'qty'				: d.qty,
				'unit_price': d.unit_price
			};
			return frappe.call({
				doc: cur_frm.doc,
				method: "update_prices",
				args: args,
				callback: function(r) {
					if(r.message) {
						var d = locals[cdt][cdn];
						$.each(r.message, function(k, v) {
							d[k] = v;
						});
						calculate_base_imponible(frm);
						refresh_field("items");
						cur_frm.refresh_fields();
					}
				}
			});
		}
	}
})


var calculate_base_imponible =  function(frm) {
	var doc = frm.doc;
	doc.base_imponible = 0;
	doc.total_taxes = 0;
	doc.total = 0;

	if(doc.lines) {
		$.each(doc.lines, function(index, data){
			doc.base_imponible += (data.unit_price * data.qty);
			doc.total_taxes += (data.unit_price_with_tax - data.unit_price) * data.qty;
		})
		doc.total += doc.base_imponible + doc.total_taxes;
	}


	refresh_field('base_imponible')
	refresh_field('total_taxes')
	refresh_field('total')
}

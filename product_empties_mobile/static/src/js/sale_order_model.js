odoo.define('product_empties_mobile.SaleOrderModel', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var BasicModel = require('web.BasicModel');

    var SaleOrderModel = BasicModel.extend({

        init: function (parent, options) {
            this._super.apply(this, arguments);
            if (options['so_id']) {
                this.so_id = options['so_id'];
            } else {
                this.so_id = options['active_id'];
            }
            if (options['previous_action']) {
                this.previous_action = options['previous_action']
            }
        },
        load: function (context) {
            var self = this;
            self.productManualEmpty = [];
            self.productEmpty = {};
            self.empties = {};
            self.saleOrder = {}
            self.saleOrderLines = {}

            // Product empty lines
            var def_productEmpty = self._rpc({
                model: 'product.empty',
                method: 'search_read',
                fields: ['id', 'quantity', 'product_id'],
            }).then(function (productEmpty) {
                _.each(productEmpty, function(line){
                    self.productEmpty[line.id] = line
                });
            });

            var def_empties = self._rpc({
                model: 'product.product',
                method: 'search_read',
                fields: ['id', 'name', 'is_empty', 'product_empty_ids', 'is_manual_empty', 'display_name', 'barcode', 'image'],
                domain: ['|', ['is_empty', '=', true], ['is_manual_empty', '=', true]]
            }).then(function (empties) {
                _.each(empties, function(empty){
                    self.empties[empty.id] = empty
                });
            });


            // Product data
            // var def_products = self._rpc({
            //     model: 'product.product',
            //     method: 'search_read',
            //     fields: ['id', 'name', 'is_empty', 'product_empty_ids', 'is_manual_empty', 'display_name', 'barcode', 'image'],
            // }).then(function (products) {
            //     _.each(products, function(product){
            //         self.products[product.id] = product
            //     });
            // });
            // Sale Order Data
            var def_saleOrder = self._rpc({
                model: 'sale.order',
                method: 'search_read',
                domain: [['id', '=', self.so_id]],
                fields: ['id', 'name', 'partner_id', 'order_line', 'note'],
            }).then(function (sale_order) {
                if (sale_order.length) {
                    self.saleOrder = sale_order[0]
                }
            });
            var def_saleOrderLine = self._rpc({
                model: 'sale.order.line',
                method: 'search_read',
                domain: [['order_id', '=', self.so_id], ['product_id', '!=', false]],
                fields: ['id', 'order_id', 'name', 'product_uom_qty', 'product_id'],
            }).then(function (sale_order_lines) {
                _.each(sale_order_lines, function(so_line){
                    if (so_line.product_id) {
                        self.saleOrderLines[so_line.id] = so_line
                    }
                });
            });
            return $.when(def_productEmpty, def_empties, def_saleOrder, def_saleOrderLine).then(function () {
                _.each(self.empties, function(empty){
                    // Product empties
                    var product_emptys = {}
                    _.each(empty.product_empty_ids, function(product_empty_line){
                        var empty_line = self.productEmpty[product_empty_line]
                        product_emptys[empty_line.product_id[0]] = {
                            product_id: empty_line.product_id,
                            quantity: 0,
                            button_quantity: empty_line.quantity,
                            barcode: self.empties[empty_line.product_id[0]]['barcode']
                        }
                    });
                    empty.product_empty_ids = product_emptys
                });

                // Product manual empties
                self.productManualEmpty = _.filter(self.empties, function (product) {
                    return product.is_manual_empty === true;
                });
            });
        },

    });

    return {
        SaleOrderModel: SaleOrderModel,
    };
});

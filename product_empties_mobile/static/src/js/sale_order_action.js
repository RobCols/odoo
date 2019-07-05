odoo.define('product_empties_mobile.SaleOrderMobile', function (require) {
    "use strict";

    var SaleOrderModel = require('product_empties_mobile.SaleOrderModel');

    var concurrency = require('web.concurrency');
    var AbstractAction = require('web.AbstractAction');
    var mobile = require('web_mobile.rpc');
    var Dialog = require('web.Dialog');
    var Session = require('web.session');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var SaleOrderMobile = AbstractAction.extend({
        template: 'sale_order_barcode_lines_widget',

        events: {
            "click .empty_product_button": "_onClickEmptyButton",
            'click .o_sale_order_mobile_barcode': 'open_mobile_scanner',
            "click .scanned_item_delete": '_onDeleteScannedItem',
            "click .scanned_item_col": '_onSelectScannedItem',
            "click .empty_product_value": "_onClickValueButton",
            "click .o_exit": "_onExit",
            "click .button_qty": "_onChangeButtonQty",
            "click .product_button_add": "_onClickButtonAdd",
            "click .so_button_cancel": "_onClickButtonCancel",
            "click .product_button_back": "_onClickButtonBack",
            "click .o_back": "_onClickButtonBack",
            "click .so_button_confirm": "_onClickConfirm",
            "click .button_crate": "_onClickCrate",
        },
        custom_events: {
            'exit': "_onExit",
        },
        config: {
            Model: SaleOrderModel.SaleOrderModel,
        },

        init: function (parent, params) {
            this._super.apply(this, arguments);
            this.actionManager = parent;
            this.params = params;
            this.title = 'Sale Order';
            this.new_order_line_id = 1;
            this.model = new this.config.Model(this, {
                modelName: params['context']['active_model'],
                so_id: params['context']['so_id'],
                active_id: params['context']['active_id'],
                previous_action: params["context"]["previous_action"]
            });
            this.mutex = new concurrency.Mutex();
            this.product_data;
            this.empty_product_lines;
        },

        _onExit: function (ev) {
            ev.stopPropagation();
            var self = this;
            let previous_action = this.model.previous_action;
            let active_id = this.params['context']['active_id'];
            let order_id = this.params['context']['so_id']
            let active_ids = this.params['context']['active_ids']
            let res_ids = this.params["context"]["ids"];
            let model_name = this.params['context']['active_model'];
            let ctx = this.params['context']
            this.mutex.exec(function () {

                if (previous_action) {
                    rpc.query({
                        model: 'route.route',
                        method: 'open_orders',
                        context: ctx,
                        args: [active_id]
                    }).then(function (response) {
                        response["view_type"] = "list"
                        response["res_id"] = order_id;
                        response["context"] = {}
                        response["context"]["active_id"] = active_id
                        response["context"]["active_ids"] = active_ids
                        response["context"]["res_ids"] = res_ids
                        console.log(response);
                        var $so_container = self.$el.find('div.o_sale_order_barcode_main_menu');
                        var $product_container = self.$el.find('div.o_sale_order_product_main_menu');
                        $product_container.remove();
                        $so_container.remove();
                        self.do_action(response, {
                            "res_id": order_id,
                            "res_ids": res_ids,
                            "context": response["context"],
                            "clear_breadcrumbs": true,
                        });
                    })
                }
                else {
                    self.do_action('sale.action_quotations_with_onboarding', {
                        clear_breadcrumbs: true,
                    });
                }
            });
        },

        // Sale Order Screen
        start: function () {
            var self = this;
            var $orderLines = [];
            if (this.model.saleOrder.name !== undefined) {
                this.title += ' ' + this.model.saleOrder.name;
            }
            else {
                this.title = 'New ' + this.title;
            }

            $orderLines.push(self.add_blank_line());

            var $notes = $(QWeb.render('sale_order_mobile_view_notes', {
                sale_order: self.model.saleOrder,
            }));
            var $buttn_confirm = $(QWeb.render('sale_order_mobile_view_button_confirm', {}));

            core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
            if (!mobile.methods.scanBarcode) {
                this.$el.find(".o_sale_order_mobile_barcode").remove();
            }
            if (this.model.saleOrderLines) {
                console.log(Object.keys(this.model.empties))
                for (let item of Object.keys(this.model.saleOrderLines)) {
                    if ($.inArray(this.model.saleOrderLines[item]['product_id'][0] + "", Object.keys(this.model.empties)) > -1) {
                        let quantity = 0;
                        if (this.model.saleOrderLines[item]['product_uom_qty'] < 0) {
                            quantity = -this.model.saleOrderLines[item]['product_uom_qty'];
                        }
                        else {
                            quantity = this.model.saleOrderLines[item]['product_uom_qty'];
                        }
                        $orderLines.push($(QWeb.render('sale_order_mobile_view_so_lines', {
                            id: this.model.saleOrderLines[item]['id'],
                            product: this.model.saleOrderLines[item]['name'],
                            product_id: this.model.saleOrderLines[item]['product_id'][0],
                            qty: quantity,
                        })))
                    }
                }
            }
            return this._super.apply(this, arguments).then(function () {
                self.$el.find('.scanned_items').append($orderLines);
                self.$el.find('.o_sale_order_barcode_main_menu').append($notes);
                self.$el.find('.o_sale_order_barcode_main_menu').append($buttn_confirm);
            })

            if (!Object.keys(self.model.saleOrder).length) {
                self.model.saleOrder = {
                    'id': false,
                    'name': 'New',
                    'partner_id': [],
                    'order_line': [],
                    'note': false,
                };
            }
        },

        _onClickCrate: function (ev) {
            var self = this;
            let $lines = Array.from(self.$el.find('.selected_item_row'));
            for (let $line of $lines) {
                for (let product_empty of Object.keys(self.product_data.product_empty_ids)) {
                    var product_id = $line.children[0].children[0].innerText;
                    if (product_empty == product_id) {
                        var new_qty = self.product_data.product_empty_ids[product_empty]["quantity"] + self.product_data.product_empty_ids[product_empty]["button_quantity"]
                        $line.children[2].children[0].innerText = new_qty;
                        self.product_data.product_empty_ids[product_empty]['quantity'] = new_qty;
                    }
                }
            }
        },

        _onClickConfirm: function (ev) {
            var self = this;
            var so_note = $('.sale_order_notes input').val();
            self.model.saleOrder['note'] = so_note;
            var so_lines = self.model.saleOrderLines;
            var order_id = self.model.saleOrder['id'];
            self._save(order_id, so_lines, so_note);
        },

        _save: function (order_id, so_lines, sale_order_note) {
            var self = this;
            Session.rpc('/update/sale_order/product_return', {
                order_id: order_id || _t('New'),
                sale_order_note: sale_order_note,
                so_lines: so_lines,
            }).then(function (result) {
                if (result.message) {
                    self.open_message_popup(result.message, _t('Status!!!'), true);
                } else if (result.error) {
                    self.open_message_popup(result.error, _t('Warning!!!'), false);
                } else {
                    self.trigger_up('exit');
                }
            });
        },

        open_message_popup: function (message, title, flag_exit) {
            var self = this;
            if (!title) {
                title = _t('Warning!!!')
            }
            var options = {
                title: _t(title),
                size: 'small',
                $content: '<div>' + message + '</div>',
                buttons: [
                    {
                        text: _t("OK"), close: true, classes: 'btn-primary', click: function (ev) {
                            if (flag_exit) {
                                self.trigger_up('exit');
                            }
                        }
                    },
                ],
            };
            var error_popup = new Dialog(self, options).open();
        },

        willStart: function () {
            var self = this;
            var def = this.model.load(this.params.context).then(this._super.bind(this));
            return def;
        },

        destroy: function () {
            core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
            this._super();
        },

        add_blank_line: function () {
            return $(QWeb.render("sale_order_blank_line", {}));
        },

        remove_blank_line: function () {
            var $line = $('div.scanned_items').find('.row_blank');
            $line.remove();
        },

        _onManualButtonClicked: function (id) {
            var self = this;
            if (!$.contains(document, this.el)) {
                return;
            }
            var $so_container = self.$el.find('div.o_sale_order_barcode_main_menu');
            var $product_view_container = self.$el.find('div.o_sale_order_product_main_menu');

            if ($so_container.length && !$so_container.hasClass('d-none')) {
                Session.rpc('/sale_order/product/add_from_manual_button', {
                    product_id: id,
                }).then(function (result) {
                    if (result.warning) {
                        self.do_warn(result.warning);
                    } else if (Object.keys(result).length) {
                        self.product_data = result;
                        self.open_product_screen(result);
                    }
                });
            } else if ($product_view_container.length) {
                var $line = $product_view_container.find('div.empty_product_lst').find(".selected_item_row[data-product-id='" + id + "']");
                if ($line.length) {
                    var product_id = $line.find('.empty_product_id').find('span').text();
                    var old_qty = self.product_data.product_empty_ids[product_id]['quantity'];
                    var new_qty = 1 + parseInt(old_qty);
                    self.change_empty_product_quantity($line, new_qty);
                } else {
                    self.do_warn(_t("No prduct find with scanned barcode. Please try again with correct one."));
                }
            }
        },

        _onBarcodeScanned: function (barcode) {
            var self = this;
            if (!$.contains(document, this.el)) {
                return;
            }
            var $so_container = self.$el.find('div.o_sale_order_barcode_main_menu');
            var $product_view_container = self.$el.find('div.o_sale_order_product_main_menu');

            if ($so_container.length && !$so_container.hasClass('d-none')) {
                Session.rpc('/sale_order/product/scan_from_so_mobile_view', {
                    barcode: barcode,
                }).then(function (result) {
                    if (result.warning) {
                        self.do_warn(result.warning);
                    } else if (Object.keys(result).length) {
                        self.product_data = result;
                        self.open_product_screen(result);
                    }
                });
            } else if ($product_view_container.length) {
                var $line = $product_view_container.find('div.empty_product_lst').find(".selected_item_row[data-product-barcode='" + barcode + "']");
                if ($line.length) {
                    var product_id = $line.find('.empty_product_id').find('span').text();
                    var old_qty = self.product_data.product_empty_ids[product_id]['quantity'];
                    var new_qty = 1 + parseInt(old_qty);
                    self.change_empty_product_quantity($line, new_qty);
                } else {
                    self.do_warn(_t("No prduct find with scanned barcode. Please try again with correct one."));
                }
            }
        },

        open_mobile_scanner: function () {
            var self = this;
            mobile.methods.scanBarcode().then(function (response) {
                var barcode = response.data;
                if (barcode) {
                    self._onBarcodeScanned(barcode);
                    mobile.methods.vibrate({ 'duration': 100 });
                } else {
                    mobile.methods.showToast({ 'message': 'Please, Scan again !!' });
                }
            });
        },

        _onClickEmptyButton: function (event) {
            event.preventDefault();
            var self = this;
            var button = $(event.currentTarget);
            var product_id = button.find('input.product_empty').val();
            self._onManualButtonClicked(product_id)
        },

        open_popup_get_quantity: function (product_data) {
            var self = this;
            var $content = "<div><input type='text' class='o_input' name='empty_product_quantity'/><br />"
            $content += "<span class='warning' style='font-size:11px;color:red;'><span></div>"
            var options = {
                title: _t("Product quantity"),
                size: 'small',
                $content: $content,
                buttons: [
                    {
                        text: _t("Add"), close: false, classes: 'btn-primary', click: function (ev) {
                            ev.preventDefault();
                            var $input = $('input[name="empty_product_quantity"]');
                            var quantity = $input.val();
                            if (!quantity) {
                                $input.css('border-bottom', 'solid 2px red');
                                $('span.warning').text('*Quantity is required!');
                            } else {
                                quantity = parseInt(quantity);
                                if (!quantity) {
                                    $input.css('border-bottom', 'solid 2px red');
                                    $('span.warning').text('*Only integers are allowed!');
                                } else {
                                    this.close();
                                    if (product_data) {
                                        self.add_product_line(product_data, quantity);
                                    } else {
                                        var $line = $('div.scanned_items').find('.selected_scanned_line');
                                        if ($line.length) {
                                            self.change_quantity_in_selected_line($line, quantity);
                                        } else {
                                            self.open_message_popup("Please select product line", 'Warning!!!', false);
                                        }
                                    }
                                }
                            }
                        }
                    },
                ],
            };
            var quantity_popup = new Dialog(self, options).open();
        },

        add_product_line: function (product_data, quantity, add_flag) {
            var self = this;
            let found = false;
            for (let item of Object.keys(self.model.saleOrderLines)) {
                let added_product = self.model.saleOrderLines[item];
                if (added_product["product_id"][0] == product_data["id"]) {
                    added_product["product_uom_qty"] = quantity

                    var $line = self.$el.find(".scanned_item_row[data-product-id='" + product_data["id"] + "']");
                    if ($line) {
                        self.change_quantity_in_selected_line($line, added_product["product_uom_qty"]);
                        found = true;
                    }
                }
            }
            if (!found) {
                self.model.saleOrderLines['new-' + self.new_order_line_id] = {
                    'id': 'new-' + self.new_order_line_id,
                    'product_uom_qty': quantity,
                    'product_id': [product_data['id'], product_data['name']],
                };
                var order_line = $(QWeb.render('sale_order_mobile_view_so_lines', {
                    id: 'new-' + self.new_order_line_id,
                    product: product_data['name'],
                    product_id: product_data['id'],
                    qty: quantity,
                }));
                self.new_order_line_id += 1;
                self.remove_blank_line();
                self.$el.find('.scanned_items').append(order_line);
            }
        },

        change_quantity_in_selected_line: function (line, quantity, add_flag) {
            var self = this;
            var col_qty = line.find('span.scanned_item_qty');
            if (add_flag) {
                quantity += parseInt(col_qty.text());
            }
            var sol_id = line.find('span.scanned_item_id').text();
            self.model.saleOrderLines[sol_id]['product_uom_qty'] = quantity;
            col_qty.text(quantity);
        },

        _onClickValueButton: function (ev) {
            var self = this;
            self.open_popup_get_quantity();
        },

        _onDeleteScannedItem: function (ev) {
            var self = this;
            var $line = $(ev.currentTarget).closest('div.scanned_item_row');
            var sale_line_id = $line.find('.scanned_item_id').text()
            delete self.model.saleOrderLines[sale_line_id]
            $line.remove();
        },

        _onSelectScannedItem: function (ev) {
            var self = this;
            var $selected_line = $(ev.currentTarget);
            var $old_selected_lines = $selected_line.closest('div.scanned_items').find('div.selected_scanned_line');
            _.each($old_selected_lines, function (line) {
                $(line).removeClass('selected_scanned_line');
            })
            $selected_line.addClass('selected_scanned_line');
            if ($selected_line[0]["attributes"]) {
                let product_id = $selected_line[0].dataset.productId;
                self._onManualButtonClicked(product_id);
            }
        },

        _onClickButtonCancel: function (ev) {
            $('.o_barcode_header').find('a.o_exit').click();
        },

        _change_exit_button: function () {
            var button_exit = $('.o_barcode_header').find('a.o_exit');
            var button_back = $('.o_barcode_header').find('a.o_back');
            if (button_exit.length) {
                button_exit.removeClass('o_exit');
                button_exit.addClass('o_back');
            }
            else if (button_back.length) {
                button_back.removeClass('o_back');
                button_back.addClass('o_exit');
            }
        },

        // Product Screen
        open_product_screen: function (product_data) {
            var self = this;
            let quantity = 0;
            for (let item of Object.keys(self.model.saleOrderLines)) {
                let added_product = self.model.saleOrderLines[item];
                if (added_product["product_id"][0] == product_data["id"]) {
                    quantity = added_product["product_uom_qty"]
                }
                else if (Object.keys(product_data["product_empty_ids"]).length) {
                    if ($.inArray(added_product["product_id"][0] + "", Object.keys(product_data["product_empty_ids"])) > -1) {
                        if (self.model.saleOrderLines[item]["product_uom_qty"] < 0) {
                            product_data["product_empty_ids"][added_product["product_id"][0]]["quantity"] = -self.model.saleOrderLines[item]["product_uom_qty"]
                        }
                        else {
                            product_data["product_empty_ids"][added_product["product_id"][0]]["quantity"] = self.model.saleOrderLines[item]["product_uom_qty"]
                        }
                    }
                }
            }
            self._change_exit_button();
            var $so_container = self.$el.find('div.o_sale_order_barcode_main_menu');
            var $product_view_container = self.$el.find('div.o_sale_order_product_main_menu');
            $so_container.addClass('d-none');
            if (!$product_view_container.length) {
                let productPageParameters = {}
                if (product_data.is_empty) {
                    productPageParameters['product'] = product_data
                    productPageParameters['product']['product_empty_ids'] = {}
                    productPageParameters['product']['product_empty_ids'][product_data.id] = {
                        "product_id": [product_data.id, product_data.name],
                        "quantity": quantity,
                        "button_quantity": 0,
                        "barcode": product_data.barcode,
                    };
                } else {
                    productPageParameters['product'] = product_data;
                }
                var $productPage = $(QWeb.render('sale_line_product_for_empty', productPageParameters));
            }
            $('.o_sale_order_main_container').append($productPage);
            if (!mobile.methods.scanBarcode) {
                $($productPage[0]).find('.o_sale_order_mobile_barcode').remove();
            }
        },

        _onChangeButtonQty: function (ev) {
            var self = this;
            var button = $(ev.currentTarget);
            var $line = button.closest('.selected_item_row');
            var product_id = $line.find('.empty_product_id').find('span').text();
            var qty = button.attr('data');
            var old_qty = self.product_data.product_empty_ids[product_id]['quantity'];
            var new_qty = parseInt(qty) + parseInt(old_qty);
            if (new_qty >= 0) {
                self.change_empty_product_quantity($line, new_qty);
            }
        },

        change_empty_product_quantity: function ($line, quantity) {
            var self = this;
            $line.find('.empty_product_qty').find('span').text(quantity);
            var product_id = $line.find('.empty_product_id').find('span').text();
            self.product_data.product_empty_ids[product_id]['quantity'] = quantity;
        },

        add_scanned_product_to_sale_order: function (product_data) {
            var self = this;

            _.each(product_data.product_empty_ids, function (product_empty_line, index) {
                var product = {
                    id: product_empty_line['product_id'][0],
                    name: product_empty_line['product_id'][1],
                };
                var quantity = product_empty_line['quantity'];
                if (quantity) {
                    self.add_product_line(product, quantity, true);
                }
            });
            self._onClickButtonBack();
        },

        _onClickButtonAdd: function (ev) {
            var self = this;
            self.add_scanned_product_to_sale_order(self.product_data);
        },

        _onClickButtonBack: function (ev) {
            var self = this;
            self._change_exit_button();
            var $so_container = self.$el.find('div.o_sale_order_barcode_main_menu');
            var $product_container = self.$el.find('div.o_sale_order_product_main_menu');
            $product_container.remove();
            $so_container.removeClass('d-none');
            $back_btn = self.$el.find('.o_back_button')
            $back_btn.remove();
        },
    });

    core.action_registry.add('open_sale_order_mobile_view', SaleOrderMobile);

    return {
        SaleOrderMobile: SaleOrderMobile,
    };

});

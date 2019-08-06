odoo.define('flex_routes.hide_selector_column_on_route_tree', function (require) {
    "use strict";

    var core = require('web.core');
    var ListRenderer = require("web.ListRenderer");
    ListRenderer.include({
        init: function (parent, state, params) {

            this._super.apply(this, arguments);
            console.log(this);
            if(this.state.context.hide_selectors) {
                this.hasSelectors = false;
            };
        },
    });
});
odoo.define('web_widget_leaflet_multi', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var widgetRegistry = require('web.widget_registry');
    var rpc = require('web.rpc');

    class MarkerModel {
        constructor(orderId, lat, lng) {
            this.orderId = orderId;
            this.lat = lat;
            this.lng = lng;
        }
    }
    var LeafletMarker = Widget.extend({
        template: "leaflet_marker_multi",

        init: function (view, record, node) {
            this._super(view, record, node);
            this.field_lat = node.attrs.lat;
            this.field_lng = node.attrs.lng;
            this.field_source_ids = node.attrs.source_ids;
            console.log(this.field_source_ids);
            this.field_zoom = node.attrs.zoom_field;
            this.field_map_type = node.attrs.map_type

            this.shown = $.Deferred();
            this.data = record.data;
            this.mode = view.mode || "readonly";
            this.record = record;
            this.view = view;
        },

        start: function () {
            var self = this;
            setTimeout(function () { self.on_ready(); }, 1000);
            return this._super();

        },

        on_ready: function () {
            var zoomLevel = this.data[this.field_zoom] || 13
            var markerCoords = []
            var $leafletEl = this.$el[0];
            var lat = this.data[this.field_lat];
            var lng = this.data[this.field_lng];
            let map = new L.map($leafletEl).setView([lat, lng], zoomLevel);
            let depot = L.marker([lat, lng]);
            markerCoords.push([lat, lng]);
            depot.addTo(map);
            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            }).addTo(map);
            if (this.field_map_type === "sat") {
                L.tileLayer.wms('http://geoservices.wallonie.be/arcgis/services/IMAGERIE/ORTHO_2018/MapServer/WMSServer?', {
                    layers: '0',
                    format: 'image/png32',
                    transparent: true,
                }).addTo(map);
                L.tileLayer('http://tile.informatievlaanderen.be/ws/raadpleegdiensten/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=ogwrgb13_15vl&STYLE=&FORMAT=image/png&TILEMATRIXSET=GoogleMapsVL&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', {
                }).addTo(map);

                L.tileLayer.wms('https://geoservices.informatievlaanderen.be/raadpleegdiensten/Adressen/wms?', {
                    layers: 'Adrespos',
                    format: 'image/png',
                    transparent: true, 
                }).addTo(map);
            }
            rpc.query({
                model: 'sale.order',
                method: 'search_read',
                fields: ['id', 'partner_latitude', 'partner_longitude'],
                domain: [['id', 'in', this.data[this.field_source_ids]["res_ids"]]],

            }).then(function (markers) {
                for (let data of markers) {
                    let marker = L.marker([Number(data["partner_latitude"]), Number(data["partner_longitude"])], {
                        draggable: false,
                    });
                    markerCoords.push([Number(data["partner_latitude"]), Number(data["partner_longitude"])]);
                    marker.addTo(map);
                    marker.on('dragend', function (ev) {
                        var position = marker.getLatLng();
                        marker.setLatLng(position, {
                            draggable: 'true'
                        }).bindPopup(position).update();
                        my_self.update_latlng(position.lat, position.lng);
                    });        
                }
                console.log(markerCoords);
                var polyLine = L.polyline(markerCoords, {color: 'red'}).addTo(map)
                map.fitBounds(polyLine.getBounds());    
            });
            var my_self = this;

            map.on('zoomend', function (ev) {
                if (my_self.mode == 'edit') {
                    my_self.update_zoom(map.getZoom());
                }
            });


            var observer = new MutationObserver(function (ev) {
                map.invalidateSize();
            });

            this.$el.parents().each(function (index) {
                observer.observe($(this)[0], {
                    attributes: true,
                    attributeFilter: ['class'],
                    childList: false,
                    characterData: false
                });
            });


        },

        update_latlng: function (lat, lng) {
            var def = $.Deferred();
            var changes = {};
            changes[this.field_lat] = lat;
            changes[this.field_lng] = lng;

            this.data[this.field_lat] = lat;
            this.data[this.field_lng] = lng;

            this.trigger_up('field_changed', {
                dataPointID: this.record.id,
                changes: changes,
                onSuccess: def.resolve.bind(def),
                onFailure: def.reject.bind(def),
            });
        },

        update_zoom: function (zoom) {
            var def = $.Deferred();
            var changes = {};

            if (this.field_zoom) {
                this.data[this.field_zoom] = zoom;
                changes[this.field_zoom] = zoom;
            }

            this.trigger_up('field_changed', {
                dataPointID: this.record.id,
                changes: changes,
                onSuccess: def.resolve.bind(def),
                onFailure: def.reject.bind(def),
            });
        },
    });
    widgetRegistry.add('leaflet_marker_multi', LeafletMarker);

    return {
        leaflet_marker_multi: LeafletMarker,
    };

});
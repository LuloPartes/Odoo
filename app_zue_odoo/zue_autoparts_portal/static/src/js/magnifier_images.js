odoo.define('zue_autoparts_portal.product_image_magnifier', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.ProductImageMagnifier = publicWidget.Widget.extend({
        selector: '.product-image-container',
        events: {
            'mousemove': '_onMouseMove',
            'mouseleave': '_onMouseLeave',
        },
        start: function () {
            this.$magnifyingGlass = this.$('.magnifying-glass');
            this.imageUrl = this.$el.data('zoom-image');
        },
        _onMouseMove: function (event) {
            const { offsetX: x, offsetY: y } = event;
            const { width, height } = this.$magnifyingGlass[0].getBoundingClientRect();
            const backgroundPositionX = -x * 2 + width / 2;
            const backgroundPositionY = -y * 2 + height / 2;

            this.$magnifyingGlass.css({
                display: 'block',
                left: `${x - width / 2}px`,
                top: `${y - height / 2}px`,
                backgroundImage: `url('${this.imageUrl}')`,
                backgroundSize: `${this.$('.product-image img').width() * 2}px ${this.$('.product-image img').height() * 2}px`,
                backgroundPosition: `${backgroundPositionX}px ${backgroundPositionY}px`,
            });
        },
        _onMouseLeave: function () {
            this.$magnifyingGlass.css('display', 'none');
        },
    });

    return publicWidget.registry.ProductImageMagnifier;
});

$(document).ready(function () {
    $('form[action="/shop/cart/update"] .a-submit, #comment .a-submit').off('click').on('click', function (e) {
        e.preventDefault();
        $.ajax({
            url: '/shop/cart/update',
            type: 'post',
            data: $(this).closest('form').serialize(),
            success: function () {
                $("#my_cart").load(location.href + " #my_cart");
                $("#my_cart").removeClass("d-none");
            }
        });
    });

    $(document).ajaxComplete(function (ev, data) {
        if ($('.min_qty_not_reached').length) {
            $(".checkout-btn").removeAttr("href");
        } else {
            $(".checkout-btn").each(function(){$(this).attr("href", "/shop/checkout");});
        }
    });


    $(function () {
        $('form[action="/shop/cart/update"]').on("submit", function (e) {
            e.preventDefault(); // cancel the actual submit
        });
    });

});
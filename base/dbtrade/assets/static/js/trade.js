$(document).ready(function() {
	var pusher = new Pusher('de504dc5763aeef9ff52');
	var trades_channel = pusher.subscribe('live_trades');
	var cb_last = $('.cb-last'), bs_last = $('.bs-last');
	if(cb_last.length && bs_last.length) {
		var per_of = parseFloat(cb_last.eq(0).html().replace(/[^0-9\.]/g, '')) / parseFloat(bs_last.eq(0).html().replace(/[^0-9\.]/g, ''));
	}
	trades_channel.bind('trade', function(data) {
		//console.log(data);
		if(bs_last.length) {
			$('.bs-last').html('$' + data.price.toFixed(2));
			if(cb_last.length) {
				var estimated_cb_price = data.price * per_of;
				$('.cb-last').html('$' + estimated_cb_price.toFixed(2) + '*');
			}
		}
	});
	order_book_tbody = $('#order-book');
	if(order_book_tbody.length) {
	    var order_book_channel = pusher.subscribe('live_orders');
	    order_book_channel.bind('data', function(data) {
	    	console.log(data);
	    });
    }
});

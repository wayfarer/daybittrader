$(document).ready(function() {
	var pusher = new Pusher('de504dc5763aeef9ff52');
	var trades_channel = pusher.subscribe('live_trades');
	var cb_last = $('.cb-last'), bs_last = $('.bs-last');
	if(cb_last.length && bs_last.length) {
		var per_of = parseFloat(cb_last.eq(0).html().replace(/$/g, '')) / parseFloat(bs_last.eq(0).html().replace(/$/g, ''));
	}
	trades_channel.bind('trade', function(data) {
		//console.log(data);
		if(cb_last.length && bs_last.length) {
			$('.bs-last').html('$' + data.price.toFixed(2));
			var estimated_cb_price = data.price * per_of;
			$('.cb-last').html('$' + estimated_cb_price.toFixed(2));
		}
	});
    /*var order_book_channel = pusher.subscribe('order_book');
    order_book_channel.bind('data', function(data) {
    	console.log(data);
    });*/
});

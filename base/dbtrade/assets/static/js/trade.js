$(document).ready(function() {
	var pusher = new Pusher('de504dc5763aeef9ff52');
	var trades_channel = pusher.subscribe('live_trades');
	trades_channel.bind('trade', function(data) {
		//console.log(data);
		$('.bs-last').html('$' + data.price);
	});
    /*var order_book_channel = pusher.subscribe('order_book');
    order_book_channel.bind('data', function(data) {
    	console.log(data);
    });*/
});

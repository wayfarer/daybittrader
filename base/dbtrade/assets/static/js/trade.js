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
	    var order_book_channel = pusher.subscribe('order_book');
	    order_book_channel.bind('data', function(data) {
	    	console.log(data);
	    	function build_tds(arr) {
	    		var total = parseFloat(arr[0]) * parseFloat(arr[1]);
	    		return '<td>$' + arr[0] + '</td><td>' + arr[1] + '</td><td>$' + total.toFixed(2) + '</td>';
	    	}
	    	bid_tds = [];
	    	for(var i=0; i<data.bids.length; i++) {
	    		tds = build_tds(data.bids[i]);
	    		bid_tds.push(tds);
	    	}
	    	ask_tds = [];
	    	for(var i=0; i<data.asks.length; i++) {
	    		tds = build_tds(data.asks[i]);
	    		ask_tds.push(tds);
	    	}
	    	var top_len = (data.bids.length < data.asks.length) ? data.asks.length : data.bids.length;
	    	var empty_tds = '<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>';
	    	var trs = '';
	    	for(var i=0; i<top_len; i++) {
	    		var bid_html = bid_tds[i];
	    		if(!bid_html) {
	    			bid_html = empty_tds;
	    		}
	    		var ask_html = ask_tds[i];
	    		if(!ask_html) {
	    			ask_html = empty_tds;
	    		}
	    		tr = '<tr>' + bid_html + '<td>&nbsp;&nbsp;</td>' + ask_html + '</tr>';
	    		trs += tr;
	    	}
	    	order_book_tbody.html(trs);
	    });
    }
});


$(document).ready(function() {
	$('.nav a').each(function() {
		if(window.location.href == this.href) {
			$(this).parent().addClass('active');
		}
	});
});

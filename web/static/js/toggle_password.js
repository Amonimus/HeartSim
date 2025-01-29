$(".toggle-password").click(function() {
	var input = $('input[name="password"]');
	if (input.attr("type") == "password") {
		input.attr("type", "text");
	} else {
		input.attr("type", "password");
	}
	var input = $('input[name="confirm_password"]');
	if (input.attr("type") == "password") {
		input.attr("type", "text");
	} else {
		input.attr("type", "password");
	}
});
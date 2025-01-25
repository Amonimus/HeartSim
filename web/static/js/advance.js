function Advance(){
	var char_id = document.getElementById("char_id").value;
	data = {
		csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
		char_id: char_id
	};
	try {
		var error_flag = false;
		$.ajax({
			url: "/ajax/advance",
			method: "POST",
			async: false,
			data: data,
			error: (error) => {
				console.error(error);
				error_flag = true;
			}
		});
		if (error_flag) {
			$('#error_status').text("Unable to fetch data!");
		} else {
			$('#error_status').text("");
		}
		GetLogs();
		GetCharacterStats();
	} catch (err)  {
		console.error(err);
		clearInterval(interval_id);
	}
}
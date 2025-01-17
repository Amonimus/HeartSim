function SendCommand(){
	var text = document.getElementById("command_input").value;
	var char_id = document.getElementById("char_id").value;
	data = {
		csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
		text: text,
		char_id: char_id
	};
	$.ajax({
		url: "/ajax/sendcommand",
		method: "POST",
		async: false,
		data: data,
		success: (data) => {
			console.log(data);
			GetLogs();
		},
		error: (error) => {
			console.log(error);
		}
	});
}
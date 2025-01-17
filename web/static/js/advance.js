function Advance(){
	var char_id = document.getElementById("char_id").value;
	data = {
		csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
		char_id: char_id
	};
	$.ajax({
		url: "/ajax/advance",
		method: "POST",
		async: false,
		data: data,
		error: (error) => {
			console.log(error);
		}
	});
	GetLogs();
	GetCharacterStats();
}
function GetCharacterStats(){
	var char_id = $('input[name=char_id]').val();
	data = {
		char_id: char_id
	};
	result = $.ajax({
		url: "/ajax/getstats",
		async: false,
		data: data,
		error: (error) => {
			console.log(error);
		}
	});
	if (result.status == 200){
		var stats = result.responseJSON;
		console.log(stats);
		$('#health').text(stats.stats.health);
		$('#stamina').text(stats.stats.stamina);
	} else {
		console.log(result);
	}
}
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
			console.error(error);
		}
	});
	if (result.status == 200){
		var stats = result.responseJSON;
		console.log(stats);
		$('#health').text(stats.stats.health);
		$('#stamina').text(stats.stats.stamina);
		GenerateList("status_list", stats.stats.statuses);
		GenerateList("task_list", stats.tasks);
	} else {
		console.error(result);
	}
}

function GenerateList(element_id, data){
		var container = document.getElementById(element_id);
		container.replaceChildren();
		const list = document.createElement("ul");
		container.appendChild(list);

		for(let i=0; i<data.length; i++){
			const node = document.createElement("li");
			const textnode = document.createTextNode(data[i]);
			node.appendChild(textnode);
			list.appendChild(node);
		}
}
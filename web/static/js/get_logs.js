function GetLogs(){
	var char_id = document.getElementById("char_id").value;
	data = {
		char_id: char_id
	};
	result = $.ajax({
		url: "/ajax/getlogs",
		async: false,
		data: data,
		error: (error) => {
			console.log(error);
		}
	});
	if (result.status == 200){
		var logs = result.responseJSON;

		var container = document.getElementById("logger");
		container.replaceChildren();

		const list = document.createElement("ul");
		container.appendChild(list);

		for(let i=0; i<logs.length; i++){
			const node = document.createElement("li");
			const textnode = document.createTextNode(logs[i].time + " > " + logs[i].text);
			node.appendChild(textnode);
			list.appendChild(node);
		}
	} else {
		console.log(result);
	}
}
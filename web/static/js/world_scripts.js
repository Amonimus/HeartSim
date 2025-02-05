function FetchWorldJson(){
	var world_id = $('input[name=world_id]').val();
	data = {
		world_id: world_id
	};
	result = AjaxCall("/api/world", data);
	if (result.status == 200){
		var world_json = result.responseJSON;
		console.log(world_json);
		ParseLogs(world_json.logs);
		var entity = world_json.entities[0];
		if(!entity.properties.alive){
			PrintError("Entity is not alive!");
		}
		$('#health').text(entity.properties.health);
		$('#stamina').text(entity.properties.stamina);
		$('#alive').text(entity.properties.alive);
		GenerateList("status_list", entity.states);
		GenerateList("task_list", entity.tasks);
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

function SendCommand(){
	var text = document.getElementById("command_input").value;
	var world_id = document.getElementById("world_id").value;
	data = {
		csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
		text: text,
		world_id: world_id
	};
	AjaxCall("/api/send_command", data, "POST", FetchWorldJson);
}

function Advance(){
	var world_id = document.getElementById("world_id").value;
	data = {
		csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
		world_id: world_id
	};
	try {
		var error_flag = false;
		AjaxCall("/api/advance", data, "POST", function(data) {
			//console.log(data);
		}, function(error) {
			error_flag = true;
			clearInterval(interval_id);
		});
		if (error_flag) {
			PrintError("Unable to fetch data!");
		} else {
			$('#error_status').text("");
			FetchWorldJson();
		}
	} catch (err) {
		console.error("Advance error");
		console.error(err);
		clearInterval(interval_id);
		return;
	}
}

function PrintError(text){
	$('#error_status').text(text);
}

function ParseLogs(logs){
	var logger = document.getElementById("logger");
	logger.replaceChildren();

	const list = document.createElement("ul");
	logger.appendChild(list);

	for(let i=0; i<logs.length; i++){
		const node = document.createElement("li");
		const textnode = document.createTextNode(logs[i].time + " > " + logs[i].text);
		node.appendChild(textnode);
		list.appendChild(node);
	}
	logger.scrollTop = logger.scrollHeight;
}
window.addEventListener('load', function () {
	FetchWorldJson();
});
var interval_id = setInterval(Advance, 1000);

var input = document.getElementById("command_input");
var logger = document.getElementById("logger");
input.addEventListener("keypress", function(event) {
	if (event.key === "Enter") {
		event.preventDefault();
		SendCommand();
		input.value = "";
	}
});
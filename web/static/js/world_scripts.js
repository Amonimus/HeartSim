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
		if(world_json.disabled){
			PrintError("World is paused!");
		}
		for (var entity_i in world_json.entities){
			var entity = world_json.entities[entity_i];
			PrintStats(entity);
		}
	} else {
		console.error(result);
	}
}

function PrintStats(entity){
	var world_stats = $("#world-stats");
	var entity_row = world_stats.children("#entity-"+entity.name);
	if(!entity_row.length){
		entity_row = $("<li></li>");
		entity_row.attr('id', "entity-"+entity.name);
		entity_row.text(entity.name);
		world_stats.append(entity_row);
	}
	var properties_list = entity_row.children("ul");
	if(!properties_list.length){
		properties_list = $("<ul></ul>");
		entity_row.append(properties_list);
	}

	if(entity.properties.hasOwnProperty("alive")){
		if(!entity.properties.alive){
			PrintError("Entity is not alive!");
		}
		GenerateList("status_list", entity.states);
		GenerateList("task_list", entity.tasks);
	}
	for (var property_name in entity.properties){
		var property = entity.properties[property_name];
		var property_row = properties_list.children("#property-"+entity.name+"_"+property_name);
		if(!property_row.length){
			property_row = $("<li></li>");
			property_row.attr('id', "property-"+entity.name+"_"+property_name);
			property_row.text(property_name+": ");
			property_row.append($("<span></span>").text(entity.properties[property_name]));
			properties_list.append(property_row);
		} else {
			property_row.children('span').text(entity.properties[property_name]);
		}
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
	$("#world-stats").text("");
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
		$('#error_status').text("");
		if (error_flag) {
			PrintError("Unable to fetch data!");
		} else {
			FetchWorldJson();
		}
	} catch (err) {
		console.error("Advance error");
		console.error(err);
		clearInterval(interval_id);
		PrintError("Script error!");
		return;
	}
}

function PrintError(text){
	var error_status = $('#error_status');
	if (error_status.text().indexOf(text) == -1){
		if(error_status.text().length){
			error_status.text([error_status.text(), text].join("; "));
		} else {
			error_status.text(text);
		}
	}
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
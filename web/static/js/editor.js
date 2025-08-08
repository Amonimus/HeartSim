function SaveJson(element){
	var table = element.parentElement.querySelector("table");
	if(table){
		dict_data = get_recursively(table);
		console.log(JSON.stringify(dict_data));

		data = {
			csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
			logic: JSON.stringify(dict_data)
		};
		if($(element.parentElement).find('input[name=state_id]').length){
			data['state_id'] = $(element.parentElement).find('input[name=state_id]').val();
			console.log(JSON.stringify(data));
			AjaxCall("/editor", data, "POST", Reload);
		} else if($(element.parentElement).find('input[name=task_id]').length){
			data['task_id'] = $(element.parentElement).find('input[name=task_id]').val();
			console.log(JSON.stringify(data));
			AjaxCall("/editor", data, "POST", Reload);
		}
	}
}

function get_recursively(element){
	var element_type = element.getAttribute("type");
	if (element_type == "dict"){
		var data = {};
		if (element.tagName.toLowerCase() == "table"){
			var rows = element.rows;
		} else {
			var rows = element.querySelector("table").rows;
		}
		for (var row_i=0; row_i < rows.length; row_i++){
			var row = rows[row_i];
			var data_name = row.children[0].innerText;
			var value_cell = row.children[1];
			var inner_data = get_recursively(value_cell);
			data[data_name] = inner_data;
		}
	} else if (element_type == "list") {
		var data = [];
		var rows = element.querySelector("table").rows;
		for (var row_i=0; row_i < rows.length; row_i++){
			var row = rows[row_i];
			if(row.children[1]){
				var dict_data = {};
				var data_name = row.children[0].innerText;
				dict_data[data_name] = [];
				var value_cell = row.children[1];
				var inner_data = get_recursively(value_cell);
				dict_data[data_name].push(inner_data);
				data.push(dict_data);
			} else {
				var value_cell = row.children[0];
				var inner_data = get_recursively(value_cell);
				data.push(inner_data);
			}
		}
	} else if (element_type == "str") {
		var data = element.innerText;
	} else if (element_type == "int") {
		var data = parseInt(element.innerText);
	} else if (element_type == "float") {
		var data = parseFloat(element.innerText);
	} else if (element_type == "bool") {
		var data = element.innerText.toLowerCase() == 'true';
	}
	return data;
}
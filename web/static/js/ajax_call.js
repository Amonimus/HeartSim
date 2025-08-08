function AjaxCall(url, data=null, method='GET', on_success=null, on_error=null){
	return $.ajax({
		url: url,
		method: method,
		async: false,
		data: data,
		contentType: 'application/x-www-form-urlencoded',
		success: (data) => {
			//console.log(data);
			if (on_success){
				on_success(data);
			}
		},
		error: (error) => {
			//console.log(error);
			if (on_error){
				on_error(error);
			}
		}
	});
}
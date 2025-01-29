const options = {
//	weekday: "long",
	year: "numeric",
	month: "short",
	day: "numeric",
	hour: "numeric",
	minute: "2-digit",
	second: "2-digit",
}

function getCurrentDate() {
	var d = new Date();
	var currentDate = document.getElementById('current-time');
	currentDate.innerText = d.toLocaleString("en-US", options);
}

$(function() {
	getCurrentDate();
	setInterval(getCurrentDate, 1 * 1000);
});
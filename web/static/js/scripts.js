GetLogs();
GetCharacterStats();
setInterval(Advance, 1000);

var input = document.getElementById("command_input");
input.addEventListener("keypress", function(event) {
	if (event.key === "Enter") {
		event.preventDefault();
		SendCommand();
	}
});
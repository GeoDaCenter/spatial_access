/*
Modifies html defaults
*/
function modifyDefaults() {
	
	$("#source_file").attr("type", "file");
	$("#destination_file").attr("type", "file");
	
	$("#source_unique_id_field").attr("disabled", "disabled");
	$("#source_population_field").attr("disabled", "disabled");
	$("#source_latitude_field").attr("disabled", "disabled");
	$("#source_longitude_field").attr("disabled", "disabled");
	$("#destination_unique_id_field").attr("disabled", "disabled");
	$("#destination_target_field").attr("disabled", "disabled");
	$("#destination_category_field").attr("disabled", "disabled");
	$("#destination_latitude_field").attr("disabled", "disabled");
	$("#destination_longitude_field").attr("disabled", "disabled");
}

/*
Sets up a listener on the origin and destination file input fields 
that activates the field mapping drop-down menus and populates them
with the field names in the origin/destination text files.  This
function is run once each for the origin and destination file input
fields.
*/
function handleFileInput(sourceOrDestination) {

	// Get references to the drop-down menus
	var inputFileType = "source_file";
	var sourceParameterFields = [$("#source_unique_id_field"),
	        		$("#source_population_field"),
	        		$("#source_latitude_field"),
	        		$("#source_longitude_field")];
        		
	if (sourceOrDestination === "destination") {
		inputFileType = "destination_file";
		sourceParameterFields = [$("#destination_unique_id_field"),
	        		$("#destination_target_field"),
	        		$("#destination_category_field"),
	        		$("#destination_latitude_field"),
	        		$("#destination_longitude_field")];
	}

	var inputFileField = document.getElementById(inputFileType);
	inputFileField.addEventListener("change", function(e) {
		var file = inputFileField.files[0];
		var textType = /text.*/;  // TODO: what is this?

		if (file.type.match(textType)) {

			// Set up objects to handle accessing files on the client machine (HTML5 File API)
			var reader = new FileReader();
			var fields = "";

			// Once a file has been chosen and loaded, activate and populate drop-down menus
			reader.onload = function(e) {
				
				// Get column names from the input text file
				var text = reader.result;
				var firstLine = text.split('\n').shift(); 
				var fields = firstLine.split(",");
        		
        		// Loop through drop-down menus
        		for (var i = 0; i < sourceParameterFields.length; i++) {
					sourceParameterFields[i].removeAttr("disabled");
					
					// For each drop-down menu, add all the column names in the data
					for (var j = 0; j < fields.length; j++) {
						var optionValue = fields[j].trim();
						if (optionValue !== "") {
							sourceParameterFields[i].append($('<option></option>').val(fields[j]).html(fields[j]));
						}
					}
				}
			}

			reader.readAsText(file);
		} else {
			fileDisplayArea.innerText = "File not supported!"
		}
	});
}

/* 
Once DOM is ready, modify HTML defaults and set up listeners
*/
window.onload = function() {
	modifyDefaults();
	handleFileInput("source");
	handleFileInput("destination");
}

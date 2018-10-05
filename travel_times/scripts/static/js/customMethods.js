// Global variables
var originFieldIds;
var destinationFieldIds;
var inputFileLines;	

var infoTitleHSSAScore = "HSSA Score";
var infoTextHSSAScore = 'Stands for blah blah blah blah.';

var infoTitleDistanceDecayFunction = "Distance decay function";
var infoTextDistanceDecayFunction = 'The farther away a facility is the less it should contribute to the HSSA Score.  ' +
	'The distance decay function determines the fraction by which a facility is discounted based on its distance from an origin.';

var infoTitleEpsilonValue = "Epsilon value";
var infoTextEpsilonValue = 'The streets considered for routing between origins and destinations are determined by the northernmost, ' +
	'southernmost, easternmost, and westernmost origin and destination points.  Shortest paths may lie on streets outside of this "bounding box".  ' +
	'The epsilon value is used to buffer this box.  A value of 0 means no buffering occurs.  A value of 0.5 corresponds roughly to a 0.5 degree distance.'

var infoTitleFacilityWeights = "Custom facility weights";
var infoTextFacilityWeights =  
	'<b>Format</b><br><br>' +
	'List numeric weights separated by commas. If only <i>n</i> weight values are given, the <i>n</i> + 1<sup>st</sup>' +
	' and subsequent facilities will be given a weight of 0. To apply a single weight list to all facilities, input values separated by commas. ' +
	'In the below example, the 5<sup>th</sup> facility will be weighted with the value 0.2, while the 6<sup>th</sup> facility will be given a weight of zero.  ' +
	'<blockquote>1, 0.8, 0.6, 0.4, 0.2</blockquote>' +
	'To provide different weight lists for different facility categories: ' + 
	'<blockquote>"Hospitals": 1, 0.5; "Health Clinics": 1, 0.67, 0.33; "Default": 1, 0.8, 0.6, 0.4, 0.2</blockquote>' +
	'In the above example, the weight list "Default" will be applied to all facilities not of category "Hospitals" or "Health Clinics".  ' + 
	'If no input is given, a weight list of 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 is used for all facilities.';

/*
Modifies html defaults
*/
function modifyDefaults() {
	
	$("#origin_file").attr("type", "file");
	$("#destination_file").attr("type", "file");
	
	$("#origin_population_field").parent().hide();
	$("#destination_target_field").parent().hide();
	
	$("#origin_unique_id_field").attr("disabled", "disabled");
	$("#origin_population_field").attr("disabled", "disabled");
	$("#origin_latitude_field").attr("disabled", "disabled");
	$("#origin_longitude_field").attr("disabled", "disabled");
	$("#destination_unique_id_field").attr("disabled", "disabled");
	$("#destination_latitude_field").attr("disabled", "disabled");
	$("#destination_longitude_field").attr("disabled", "disabled");
	$("#destination_target_field").attr("disabled", "disabled");
	$("#destination_category_field").attr("disabled", "disabled");
	$("#destination_categories").attr("disabled", "disabled");

	// Make input table field drop-downs inactive (while input table is still not set)
	for (var i = 0; i < window.originFieldIds.length; i++) {
		$("label[for='" + originFieldIds[i] + "']").addClass("inactive");
	}
	for (var i = 0; i < window.destinationFieldIds.length; i++) {
		$("label[for='" + destinationFieldIds[i] + "']").addClass("inactive");
	}
	
	// Make destination categories box inactive while the user hasn't set the destination category drop-down field yet
	$("label[for='destination_categories']").addClass("inactive");

	// Add placeholder text
	$("#custom_weight_dict").attr("placeholder", "[1, 0.8. 0.6, 0.4, 0.2]");

}


function handleFileInput(originOrDestination) {
	
	/*
	Sets up a listener on the origin and destination file input fields.  When those inputs
	are filled in, the listener activates the field mapping drop-down menus and populates them
	with the field names in the origin/destination text files.  This
	function is run once each for the origin and destination file input fields.
	*/

	if (originOrDestination === "origin") {
		
		
		var originFileField = document.getElementById("origin_file"); 
		originFileField.addEventListener("change", function(e) {
			readFileFields("origin", originFileField, window.originFieldIds);
			if ($("#origin_file").val() === "") {
				for (var i = 0; i < window.originFieldIds.length; i++) {
					$("label[for='" + originFieldIds[i] + "']").addClass("inactive");
					$("#" + originFieldIds[i]).attr("disabled", "disabled");
				}
				$("#origin_unique_id_field").attr("disabled", "disabled");
			} else {
				for (var i = 0; i < window.originFieldIds.length; i++) {
					$("label[for='" + originFieldIds[i] + "']").removeClass("inactive");
					$("#" + originFieldIds[i]).removeAttr("disabled");
				}
			}
		});
		
	} else {
		
		var destinationFileField = document.getElementById("destination_file"); 
		var destinationCategoryField = document.getElementById("destination_category_field"); 
		
		destinationFileField.addEventListener("change", function(e) {
			readFileFields("destination", destinationFileField, window.destinationFieldIds);
			if ($("#destination_file").val() === "") {
				for (var i = 0; i < window.destinationFieldIds.length; i++) {
					$("label[for='" + destinationFieldIds[i] + "']").addClass("inactive");
					$("#" + destinationFieldIds[i]).attr("disabled", "disabled");
				}

				$("label[for='destination_categories']").addClass("inactive");
				$("#destination_categories").attr("disabled", "disabled");
				
			} else {
				for (var i = 0; i < window.destinationFieldIds.length; i++) {
					$("label[for='" + destinationFieldIds[i] + "']").removeClass("inactive");
					$("#" + destinationFieldIds[i]).removeAttr("disabled");
				}

				$("label[for='destination_categories']").removeClass("inactive");
				$("#destination_categories").removeAttr("disabled");
			}
		});

		destinationCategoryField.addEventListener("change", function(e) {
			populateDestinationCategories(destinationFileField, destinationCategoryField);
		});
	}
}

function populateDestinationCategories(destinationFileField, destinationCategoryField) {
	
	/*
	When the destination category field is set, this listener handles populating the
	destination categories drop-down with values from the selected field.
	*/

	var categoryDropdownField = $("#destination_categories");
	categoryDropdownField.removeAttr("disabled");
	var chosenFieldIndex = destinationCategoryField.selectedIndex;
	var categoryList = [];
	for (var i = 0; i < window.inputFileLines.length; i++) {
		if (chosenFieldIndex > 0) {
			var value = window.inputFileLines[i].split(",")[chosenFieldIndex - 1];
			if (categoryList.indexOf(value) === -1 && typeof value != 'undefined') {
				categoryList.push(value);
			}
		}
	}
	categoryList.sort();
	populateDropdownOptions(categoryDropdownField, categoryList);
}

function handleDestinationCategoriesLabel() {
	
	/*
	Sets up a listener that applies the class 'inactive' to the destination_categories
	drop-down label when no value is selected, and removes it otherwise. 
	*/

	$("#destination_category_field").change(function () {
		if (this.value === "") {
			$("label[for='destination_categories']").addClass("inactive");
        } else {
        	$("label[for='destination_categories']").removeClass("inactive");
        }
    });
}

function readFileFields(originOrDestination, fileInputElement, fieldDropdownIdList) {

	/*
	This function reads in a file a user selects.
	It then populates the dropdown menus given in fieldDropdownIdList 
	with the column names in the origin file (i.e., the values in the field's first row)
	*/

	var file = fileInputElement.files[0];

	if (file) {
		
		// Set up objects to handle accessing files on the client machine (HTML5 File API)
		var reader = new FileReader();
		var fields = "";

		// Once a file has been chosen and loaded, activate and populate drop-down menus
		reader.onload = function(e) {
			
			// Get column names from the input text file
			var text = reader.result;
			window.inputFileLines = text.split(/\r|\n|\r\n|\n\r/);
			var firstLine = inputFileLines.shift(); 
			var fields = firstLine.split(",");
    		
    		// Loop through drop-down menus
			for (var i = 0; i < fieldDropdownIdList.length; i++) {
				$("#" + fieldDropdownIdList[i]).removeAttr("disabled");
				populateDropdownOptions($("#" + fieldDropdownIdList[i]), fields);
			}
			
			setTestingDefaults(file.name);
			
			// If the destination file has been set, populate the MultipleSelect field of destination categories
			if (originOrDestination === "destination") {
				var destinationFileField = document.getElementById("destination_file"); 
				var destinationCategoryField = document.getElementById("destination_category_field"); 
				populateDestinationCategories(destinationFileField, destinationCategoryField);
			}
		}

		reader.readAsText(file);
	}
}

function handleAccessAndCoverageDifferences() {

	/*
	This function updates the interface according to what measure(s) the user has chosen to calculate. 
	*/

	$(document).ready(function() {
	    	
		// Handle when there is a change in coverage measures selection
	    $("#coverage_measures_checkbox").click(function(){
	        
	        // If at least one coverage metric is selected, show the population field
	        if ($("#coverage_measures_checkbox").is(':checked')) {
	        	
	        	$("#origin_population_field").parent().slideDown();
	        	$("#destination_target_field").parent().slideDown();
        		
	        	// If the user has already chosen an origin file, populate the population dropdown with the origin file's field names.
	        	if ($("#origin_file").val() !== "") {
	        		var originFileField = document.getElementById("origin_file");
	        		readFileFields("origin", originFileField, window.originFieldIds);
	        	}

	        	// If the user has already chosen a destination file, populate the target dropdown with the origin file's field names.
	        	if ($("#destination_file").val() !== "") {
	        		var destinationFileField = document.getElementById("destination_file");
	        		readFileFields("destination", destinationFileField, window.destinationFieldIds);
	        	}
        	
        	// If no coverage measure is selected, hide the population field
	        } else {
	        	$("#origin_population_field").parent().slideUp();
	        	$("#destination_target_field").parent().slideUp();
	        }
	    });
	});	
}

function handleAdvancedSettingsDisplay() {
	$("#advancedSettingsButton").click(function() {
		$("#advancedSettingsContainer").slideToggle();
	});
}

function populateDropdownOptions(dropdownElement, optionList) {
	
	/*
	For the dropdownElement specified, add all the column names given in optionList as options 
	*/

	dropdownElement.empty()

	if (dropdownElement[0].id === "destination_category_field") {
		$("#destination_category_field").append($('<option></option>').val("").html("(no field selected)"));
	}
	
	for (var i = 0; i < optionList.length; i++) {
		var optionValue = optionList[i].trim();
		if (optionValue !== "") {
    		
			dropdownElement.append($('<option></option>').val(optionValue).html(optionValue));
		}
	}
}

function getDestinationCategoryOptions() {
	var values = [];
	$("#destination_categories").each(function() { 
	    values.push( $(this).attr('value') );
	});	
	return values;
}

function handleInformationButtons() {
	
	var dialogTitle = "";
	var dialogText = "";

	$("#dialog").dialog({
       autoOpen: false,
       width: "40%",
       minWidth: 350,
       maxWidth: 500
    });
    
    $(".infoButton").click(function() {
    	switch (event.target.id) {
    		case "decayFunctionInfoButton":
    			dialogTitle = window.infoTitleDistanceDecayFunction;
    			dialogText = window.infoTextDistanceDecayFunction;
    			break;
    		case "facilityWeightListInfoButton":
    			dialogTitle = window.infoTitleFacilityWeights;
    			dialogText = window.infoTextFacilityWeights;
    			break;
    		case "epsilonValueSliderInfoButton":
    			dialogTitle = window.infoTitleEpsilonValue;
    			dialogText = window.infoTextEpsilonValue;
    			break;
    		case "HSSAScoreInfoButton": 
    			dialogTitle = window.infoTitleHSSAScore;
    			dialogText = window.infoTextHSSAScore;
    			break;
    	}
    	$("#dialog p").html(dialogText);
    	$("#dialog").dialog({title: dialogTitle});
    	$("#dialog").dialog("open");
    });
}

function setTestingDefaults(filename) {

	if (filename === "blocks_chicago.csv") {
		$("#origin_unique_id_field option[value='geoid10']").prop('selected', true);
		$("#origin_population_field option[value='population']").prop('selected', true);
		$("#origin_latitude_field option[value='lat']").prop('selected', true);
		$("#origin_longitude_field option[value='lon']").prop('selected', true);	
		$("#destination_unique_id_field option[value='ID']").prop('selected', true);
		$("#destination_target_field option[value='target']").prop('selected', true);
		$("#destination_category_field option[value='category']").prop('selected', true);
		$("#destination_latitude_field option[value='lat']").prop('selected', true);
		$("#destination_longitude_field option[value='lon']").prop('selected', true);
	} else {
		$("#origin_unique_id_field option[value='BLOCKID10']").prop('selected', true);
		// $("#origin_population_field option[value='CE01_2014']").prop('selected', true);
		$("#origin_latitude_field option[value='lat']").prop('selected', true);
		$("#origin_longitude_field option[value='long']").prop('selected', true);
		$("#destination_unique_id_field option[value='agency_id']").prop('selected', true);
		$("#destination_target_field option[value='target']").prop('selected', true);
		$("#destination_category_field option[value='category']").prop('selected', true);
		$("#destination_latitude_field option[value='lat']").prop('selected', true);
		$("#destination_longitude_field option[value='lon']").prop('selected', true);
		
}
	}
	
function setTestingDefaults2() {
	$("#epsilonValueSliderId")[0].value = 0;
}

window.onload = function() {
	/* 
	Once DOM is ready, modify HTML defaults and set up listeners
	*/

	// Initialize global variables 
	originFieldIds = ["origin_unique_id_field",
        		"origin_latitude_field",
        		"origin_longitude_field",
        		"origin_population_field"];
    destinationFieldIds = ["destination_unique_id_field",
        		"destination_latitude_field",
        		"destination_longitude_field",
        		"destination_target_field",
        		"destination_category_field"];
	
	modifyDefaults();
	handleFileInput("destination");
	handleFileInput("origin");
	handleAccessAndCoverageDifferences();
	handleAdvancedSettingsDisplay();
	handleDestinationCategoriesLabel();
	handleInformationButtons();
	setTestingDefaults2();
}
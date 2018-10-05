from flask_wtf import FlaskForm
from wtforms import BooleanField, FileField, SelectField, SelectMultipleField, StringField, SubmitField, validators, ValidationError
from customized_flask_classes import SelectFieldWithoutPreValidation, SelectMultipleFieldWithoutPreValidation
import wtforms 
access_checked = False
coverage_checked = False
ACCESS_MEASURES_LABEL = 'Access measures'
COVERAGE_MEASURES_LABEL = 'Coverage measures'

def validate_access_or_coverage_chosen(form, field):
	
	"""
	This custom validator is used to verify that the user has checked at least one of the access measures checkbox
	or coverage measures checkbox. 
	"""

	global access_checked
	global coverage_checked

	if field.id == "access_measures_checkbox":
		access_checked = field.data
		return
	if field.id == "coverage_measures_checkbox":
		coverage_checked = field.data
		print("access_measures_checkbox checked:", access_checked, "; coverage_measures_checkbox checked:", coverage_checked)
		if access_checked is False and coverage_checked is False:
			raise ValidationError("Please check at least one of '" + ACCESS_MEASURES_LABEL + "' and '" + COVERAGE_MEASURES_LABEL + ".'")
		else:
			return
	
class InputForm(FlaskForm):
	
	global access_measures_label
	global coverage_measures_label

	access_measures_checkbox = BooleanField(ACCESS_MEASURES_LABEL, [validate_access_or_coverage_chosen])
	coverage_measures_checkbox = BooleanField(COVERAGE_MEASURES_LABEL, [validate_access_or_coverage_chosen])
	travel_mode = SelectField('Travel mode',
		choices=[('walk', 'Walk'),
		('drive', 'Drive')])

	# Advanced settings
	# walk_speed = 
	decay_function = SelectField("Distance decay function<i class='material-icons infoButton' id='decayFunctionInfoButton'>info</i>",
		choices=[('linear', 'Linear'),
		('root', 'Inverse square root'),
		('logit', 'Logit')])

	# epsilon_value = 
	# facilityWeightListInfoText = ('List numeric weights separated by commas.&#013;'
	# 	'If only n weight values are given, the n + 1st and &#013;'
	# 	'subsequent facilities will be given a weight of 0.&#013;&#013;'
	# 	'Weights can be entered with one of two formats:&#013;'
	# 	'&#009;1 (list format):  [1, 0.8, 0.6, 0.4, 0.2]&#013;'
	# 	'&#009;2 (dictionary format):  {"Hospitals": [1, 0.5], "All Free Health Clinics": [1, 0.67, 0.33], "Default": [1, 0.8, 0.6, 0.4, 0.2]}&#013;&#013;'
	# 	'If no input is given, a default weights list of [1,1,1,1,1,1,1,1,1,1]&#013;'
	# 	'is used.  If a dictionary is supplied, if it contains a "Default"&#013;'
	# 	'list (as above), then the default weights are applied to any&#013;'
	# 	'category not listed in the dictionary.')
	custom_weight_dict = StringField("Relative weight for the n<sup>th</sup> facility of the same category<i class='material-icons infoButton' id='facilityWeightListInfoButton'>info</i>")


	origin_file = FileField('Origin file', [validators.DataRequired('Please specify an origin file.')])
	origin_unique_id_field = SelectFieldWithoutPreValidation("Unique id field", choices=[])
	origin_latitude_field = SelectFieldWithoutPreValidation("Latitude (y-coordinate) field", choices=[])
	origin_longitude_field = SelectFieldWithoutPreValidation("Longitude (x-coordinate) field", choices=[])
	origin_population_field = SelectFieldWithoutPreValidation("Population field", choices=[])
	destination_file = FileField('Destination file', [validators.DataRequired('Please specify a destination file.')])
	destination_unique_id_field = SelectFieldWithoutPreValidation("Unique id field", choices=[])
	destination_latitude_field = SelectFieldWithoutPreValidation("Latitude (y-coordinate) field", choices=[])
	destination_longitude_field = SelectFieldWithoutPreValidation("Longitude (x-coordinate) field", choices=[])
	destination_target_field = SelectFieldWithoutPreValidation("Target field", choices=[])
	destination_category_field = SelectFieldWithoutPreValidation("Category field (Optional)", choices=[])
	destination_categories = SelectMultipleFieldWithoutPreValidation("Choose categories to calculate measures for (Optional)", choices=[])
	
	submit = SubmitField('Submit')




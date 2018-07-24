from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, regexp

class InputForm(FlaskForm):
	accessibility_metrics = SelectMultipleField('Accessibility metrics', 
		choices=[('HSSA Score', 'HSSA Score'),
		('Accessible facility count', 'Accessible facility count'), 
		('Time to closest facility', 'Time to closest facility')])
	coverage_metrics = SelectMultipleField('Coverage metrics',
		choices=[('Number of people within access space', 'Number of people within access space'),
		('Per capita spending', 'Per capita spending')])
	travel_mode = SelectField('Travel mode',
		choices=[('walk', 'Walk'),
		('transit', 'Transit'),
		('bike', 'Bike'),
		('drive', 'Drive')])
	maximum_travel_time = IntegerField("Maximum travel time",
		validators=[DataRequired()])
	source_file = FileField('Source file')
	source_unique_id_field = SelectField("Source unique id field", choices=[])
	source_population_field = SelectField("Source population field", choices=[])
	source_latitude_field = SelectField("Source latitude field", choices=[])
	source_longitude_field = SelectField("Source longitude field", choices=[])
	destination_file = FileField('Destination file')
	destination_unique_id_field = SelectField("Destination unique id field", choices=[])
	destination_target_field = SelectField("Target field", choices=[])
	destination_category_field = SelectField("Category field", choices=[])
	destination_latitude_field = SelectField("Destination latitude field", choices=[])
	destination_longitude_field = SelectField("Destination longitude field", choices=[])
	# destination_file = FileField('Destination file', validators=[regexp(".*\\.csv$")])
	#fields

	submit = SubmitField('Submit')
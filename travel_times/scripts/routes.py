name = "analytics_web_app"

import os, os.path, sys, inspect
import pandas as pd
import wtforms
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, flash

#Add current directory to sys.path to enable app to find local modules
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from CommunityAnalytics import *
from p2p import *

from forms import InputForm
from logging.config import dictConfig
from werkzeug.utils import secure_filename


def create_app(test_config=None):

	app = Flask(__name__)
	app.config.from_mapping(
		SECRET_KEY="development-key",
		UPLOAD_FOLDER="uploads",
		DATA_FOLDER="web_app_data",
		OUTPUT_DIRECTORY="web_app_data"
	)
	
	if test_config is None:
		# Load the instance configuration, if it exists, when not testing
		app.config.from_pyfile("config.py", silent=True)
	else:
		# Load the test configuration if passed in
		app.config.from_mapping(test_config)

	# Ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	@app.route("/", methods=['GET', 'POST'])
	def index():
		
		if not os.path.exists("uploads"):
			os.makedirs("uploads")

		form = InputForm()
		
		if request.method == 'POST':

			valid = True
			# parse custom_weight_dict
			custom_weight_dict = None
			if form.custom_weight_dict.data != "":
				try:
					custom_weight_dict = {}
					
					# If user has input more than just a single default list, it'll be separated by ;
					if form.custom_weight_dict.data.find(";") != -1:
						custom_lists = form.custom_weight_dict.data.split(";")
						for ls in custom_lists:
							list_name, values_string = ls.split(":")
							values_list_string = values_string.split(",")
							values_list = [float(value.strip()) for value in values_list_string]
							custom_weight_dict[list_name.strip()] = values_list
					# If a user has just input a default list
					else:
						list_name, values_string = form.custom_weight_dict.data.split(":")
						values_list_string = values_string.split(",")
						values_list = [float(value.strip()) for value in values_list_string]	
						custom_weight_dict["Default"] = values_list
				except:
					print("Error parsing custom weight dictionary")
					valid = False

			if form.validate():

				# retrieve file names and upload data to the server
				origin_file = request.files['origin_file']
				origin_filename = secure_filename(origin_file.filename)
				origin_file.save(os.path.join(app.config['UPLOAD_FOLDER'], origin_filename))
				destination_file = request.files['destination_file']
				destination_filename = secure_filename(destination_file.filename)
				destination_file.save(os.path.join(app.config['UPLOAD_FOLDER'], destination_filename))
				
				# create a dictionary associating field names used in the health code to the
				# fields in the data specified by the user
				origin_field_mapping = {"idx": form.origin_unique_id_field.data,
				"population": form.origin_population_field.data,
				"lat": form.origin_latitude_field.data,
				"lon": form.origin_longitude_field.data}
				destination_field_mapping = {"idx": form.destination_unique_id_field.data,
				"target": form.destination_target_field.data,
				"category": form.destination_category_field.data,
				"lat": form.destination_latitude_field.data,
				"lon": form.destination_longitude_field.data}

				categories = form.destination_categories.data
				if len(categories) == 0:
					categories = None # analytics code expects either None or a populated list
				maximum_travel_time = request.form["maximumTimeSlider"]
				
				# execute health code
				filenameAccess, filenameCoverage = run_health_code(form.access_measures_checkbox.data,
					form.coverage_measures_checkbox.data,
					form.travel_mode.data,
					maximum_travel_time,
					os.path.join(app.config['UPLOAD_FOLDER'], origin_filename), 
					origin_field_mapping,
					os.path.join(app.config['UPLOAD_FOLDER'], destination_filename),
					destination_field_mapping,
					destination_categories=categories,
					decay_function=form.decay_function.data,
					epsilon=float(request.form["epsilonValueSlider"]),
					walk_speed=float(request.form["walkSpeedSlider"]),
					custom_weight_dict=custom_weight_dict,
					file_path=app.config["OUTPUT_DIRECTORY"])

				return download_results(filenameAccess, filenameCoverage)

			else:
				print(form.errors)
				return render_template('index.html', form=form)

		elif request.method == 'GET':
			
			if form.validate_on_submit:
				return render_template("index.html", form=form)
			else:
				return render_template('about.html', form=form)

	# @app.route('/data/<filename>')
	@app.route("/return-file/<path:filename>")
	def return_file(filename):
		return send_from_directory(app.config["OUTPUT_DIRECTORY"], filename, as_attachment=True)

	@app.route("/download-results/")
	def download_results(filenameAccess, filenameCoverage):
		if filenameAccess:
			filenameAccess = os.path.basename(filenameAccess)
			flash(filenameAccess)
		if filenameCoverage:
			filenameCoverage = os.path.basename(filenameCoverage)
			flash(filenameCoverage)
		return render_template("download_results.html")

	return app

def run_health_code(access_measures_checkbox, 
	coverage_measures_checkbox,
	travel_mode,
	maximum_travel_time,
	origin_filename,
	origin_field_mapping,
	destination_filename,
	destination_field_mapping,
	destination_categories=None,
	decay_function=None,
	epsilon=None,
	walk_speed=None,
	custom_weight_dict=None,
	file_path=None):
	
	createTransitMatrix = True
	transit_matrix_file = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/contracts/analytics/data/walk_full_results_3.csv"
	filenameAccess = None
	filenameCoverage = None
	
	# Create a TransitMatrix
	if createTransitMatrix:

		if walk_speed:
			walk_speed = walk_speed * 1.6 # convert to metric
		print("origin_filename: " + origin_filename)
		transit_matrix = TransitMatrix(network_type=travel_mode,
							epsilon=epsilon,
							walk_speed=walk_speed,
	                    	primary_input=origin_filename,
							primary_input_field_mapping=origin_field_mapping,
							secondary_input=destination_filename,
							secondary_input_field_mapping=destination_field_mapping,
							write_to_file=True,
							load_to_mem=True,
							output_file_path=file_path)

		transit_matrix.process()
		transit_matrix_file = transit_matrix.output_filename
	
	# If any of the access metrics' checkboxes were checked,
	# create an AccessModel object and write output
	if access_measures_checkbox:

		access_model = AccessModel(network_type=travel_mode,
						source_filename=origin_filename,
	                    source_field_mapping=origin_field_mapping,
	                    dest_filename=destination_filename,
	                    dest_field_mapping=destination_field_mapping,
	                    sp_matrix_filename=transit_matrix_file,
	                    decay_function=decay_function,
	                    limit_categories=destination_categories,
	                    upper=int(maximum_travel_time))
		access_model.calculate(custom_weight_dict=custom_weight_dict)
		access_model.write_csv(file_path=file_path)
		filenameAccess = access_model.output_filename

	# If any of the coverage metrics' checkboxes were checked,
	# create an AccessModel object and write output
	if coverage_measures_checkbox:
		coverage_model = CoverageModel(network_type=travel_mode,
	                    source_filename=origin_filename,
	                    source_field_mapping=origin_field_mapping,
	                    dest_filename=destination_filename,
	                    dest_field_mapping=destination_field_mapping,
	                    sp_matrix_filename=transit_matrix_file,
	                    limit_categories=destination_categories,
	                    upper=int(maximum_travel_time))
		coverage_model.calculate()
		coverage_model.write_csv(file_path=file_path)
		filenameCoverage = coverage_model.output_filename

	return filenameAccess, filenameCoverage

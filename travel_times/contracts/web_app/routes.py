from flask import Flask, render_template, request, session, redirect, url_for
from forms import InputForm

from werkzeug.utils import secure_filename
from logging.config import dictConfig

import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
community_analytics_dir = os.path.join(parentdir, "analytics")
sys.path.insert(0, community_analytics_dir) 
print(sys.path)


from CommunityAnalytics import *


import logging

# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     'handlers': {'wsgi': {
#         'class': 'logging.StreamHandler',
#         'stream': 'ext://flask.logging.wsgi_errors_stream',
#         'formatter': 'default'
#     }},
#     'root': {
#         'level': 'INFO',
#         'handlers': ['wsgi']
#     }
# })


app = Flask(__name__)

# to handle csrf 
app.secret_key = "development-key"
app.config["UPLOAD_FOLDER"] = "uploads"


@app.route("/", methods=['GET', 'POST'])
def index():
	
	form = InputForm()
		
	if request.method == 'POST':

		if form.validate_on_submit:
			
			source_file = request.files['source_file']
			source_filename = secure_filename(source_file.filename)
			source_file.save(os.path.join(app.config['UPLOAD_FOLDER'], source_filename))

			destination_file = request.files['destination_file']
			destination_filename = secure_filename(destination_file.filename)
			destination_file.save(os.path.join(app.config['UPLOAD_FOLDER'], destination_filename))

			run_health_code(form.accessibility_metrics.data,
				form.coverage_metrics.data,
				form.travel_mode.data,
				form.maximum_travel_time.data,
				source_filename,
				destination_filename)
			
			return render_template("about.html", form=form)


		else:
			return render_template('index.html', form=form)

	elif request.method == 'GET':
		
		print("GET")
		
		if form.validate_on_submit:
			return render_template("index.html", form=form)
		else:
			return render_template('about.html', form=form)

def run_health_code(accessibility_metrics, coverage_metrics, travel_mode, maximum_travel_time, source_file, destination_file):
	
	HSSA_wlogit = HSSAModel(network_type=travel_mode,
                    source_filename=os.path.join("uploads", source_file),
                    dest_filename=os.path.join("uploads", destination_file),
                    sp_matrix_filename='data/walk_full_results_0.csv',
                    decay_function='logit',
                    limit_categories=None,
                    upper=int(maximum_travel_time))
	HSSA_wlogit.calculate(normalize=True)
	HSSA_wlogit.write_csv()


if __name__ == "__main__":
	app.run(debug=True)
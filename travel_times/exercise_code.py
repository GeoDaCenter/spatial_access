from CommunityAnalytics import *
from p2p import *

origins = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/contracts/analytics/resources/LEHD_subset.csv"
origins = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/contracts/web_app/uploads/LEHD_blocks_subset2.csv"
origins_full = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/contracts/analytics/resources/LEHD_blocks.csv"
origins_full = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/access/travel_times/scripts/data/ORIG/blocks_chicago.csv"
destinations = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/contracts/analytics/resources/marynia_health.csv"
destinations = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/contracts/web_app/uploads/destination_subset2.csv"
# destinations = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/access/travel_times/scripts/data/DEST/health_chicago.csv"
transit_matrix_file = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/contracts/analytics/data/drive_full_results_4.csv"
transit_matrix_file = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/contracts/analytics/data/drive_full_results_0.csv"
createTransitMatrix = True
access_measures_checkbox = True
coverage_measures_checkbox = True
filename1 = None
filename2 = None


# dir_path = "/Users/georgeyoliver/Documents/GitHub/CSDS/GeoDaCenter/contracts/analytics"
# speed_limit_dictionary_file = os.path.join(dir_path, "speed_limit_dictionary.txt")

# with open(speed_limit_dictionary_file, "r") as f:
#     speed_limit_dictionary_text = f.read()
#     x = ast.literal_eval(speed_limit_dictionary_text)
#     print(x)
# y = 1/0

# Create a TransitMatrix if 
if createTransitMatrix:
	transit_matrix = TransitMatrix(network_type="walk",
						primary_input=origins,
						primary_input_field_mapping=None,
						secondary_input=destinations,
						secondary_input_field_mapping=None,
						write_to_file=True,
						load_to_mem=True,
						walk_speed=None,
						epsilon=0.0)
	transit_matrix.process()
	transit_matrix_file = transit_matrix.output_filename

# If any of the access metrics' checkboxes were checked,
# create an AccessModel object and write output
if access_measures_checkbox:

	access_model = AccessModel(network_type="walk",
                    source_filename=origins,
                    source_field_mapping=None,
                    dest_filename=destinations,
                    dest_field_mapping=None,
                    sp_matrix_filename=transit_matrix_file,
                    decay_function='logit',
                    limit_categories={"School-Based Health Centers", "Hospitals"},
                    upper=int(30))
	access_model.calculate(custom_weight_dict={"Hospitals": [10000000,100,1,0.1], "Default": [1, 0.67, 0.33]})
	access_model.write_csv()
	filename1 = access_model.output_filename

# If any of the coverage metrics' checkboxes were checked,
# create an AccessModel object and write output
if coverage_measures_checkbox:

	coverage_model = CoverageModel(network_type="walk",
                    source_filename=origins,
                    source_field_mapping=None,
                    dest_filename=destinations,
                    dest_field_mapping=None,
                    sp_matrix_filename=transit_matrix_file,
                    limit_categories={"School-Based Health Centers", "Hospitals"},
                    upper=int(30))
	coverage_model.calculate()
	coverage_model.write_csv()
	filename2 = coverage_model.output_filename

# transit_matrix = TransitMatrix(network_type="walk",
# 						primary_input=origins,
# 						primary_input_field_mapping=None,
# 						secondary_input=origins,
# 						secondary_input_field_mapping=None,
# 						write_to_file=True,
# 						load_to_mem=True)
# transit_matrix.process()


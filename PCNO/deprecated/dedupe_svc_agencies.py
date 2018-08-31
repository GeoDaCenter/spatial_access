# Adapted from:
# http://dedupeio.github.io/dedupe-examples/docs/csv_example.html
import os
import re
import csv
import dedupe
import logging
import optparse
from unidecode import unidecode
from future.builtins import next


optp = optparse.OptionParser()
optp.add_option('-v', '--verbose', dest='verbose', action='count',
                help='Increase verbosity (specify multiple times for more)'
                )
(opts, args) = optp.parse_args()
log_level = logging.WARNING
if opts.verbose:
    if opts.verbose == 1:
        log_level = logging.INFO
    elif opts.verbose >= 2:
        log_level = logging.DEBUG
logging.getLogger().setLevel(log_level)


input_file = 'SVC_AGENCIES.csv'
output_file = 'SVC_AGENCIES_deduplicated.csv'
settings_file = 'svc_agencies_learned_settings.dedupe'
training_file = 'svc_agencies_training.json'


def preProcess(column):
    try : # python 2/3 string differences
        column = column.decode('utf8')
    except AttributeError:
        pass
    column = unidecode(column)
    column = column.strip().strip('"').strip("'").strip().upper()


    # If data is missing, indicate that by setting the value to None
    if not column:
        column = None
    return column


def readData(filename):
    data_d = {}
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = [(k, preProcess(v)) for (k, v) in row.items()]
            #row_id = int(row[''])
            row_id = row['CSDS_Org_ID']
            data_d[row_id] = dict(clean_row)

    return data_d


if __name__ == '__main__':

    print('\nImporting data ...')
    data_d = readData(input_file)

    if os.path.exists(settings_file):
        print('\nReading from', settings_file)
        with open(settings_file, 'rb') as f:
            deduper = dedupe.StaticDedupe(f)
    #else:
    fields = [
    {'field' : 'Name', 'type': 'String'},
    {'field' : 'Address', 'type': 'String'},
    {'field' : 'ZipCode', 'type': 'Exact', 'has missing' : True},
    #{'field' : 'Phone', 'type': 'String', 'has missing' : True},
    {'field' : 'City', 'type': 'String'}
    ]

    deduper = dedupe.Dedupe(fields)
    deduper.sample(data_d, 1000)

    if os.path.exists(training_file):
        print('\nReading labeled examples from ', training_file)
        with open(training_file, 'rb') as f:
            deduper.readTraining(f)

    print('\nStarting active labeling...\n')

    dedupe.consoleLabel(deduper)

    deduper.train()

    with open(training_file, 'w') as tf:
        deduper.writeTraining(tf)

    with open(settings_file, 'wb') as sf:
        deduper.writeSettings(sf)

    threshold = deduper.threshold(data_d, recall_weight=1)

    print('\nClustering...')
    clustered_dupes = deduper.match(data_d, threshold)

    print('\n# duplicate sets', len(clustered_dupes))



    cluster_membership = {}
    cluster_id = 0
    for (cluster_id, cluster) in enumerate(clustered_dupes):
        id_set, scores = cluster
        cluster_d = [data_d[c] for c in id_set]
        canonical_rep = dedupe.canonicalize(cluster_d)
        for record_id, score in zip(id_set, scores):
            cluster_membership[record_id] = {
                "ClusterID" : cluster_id,
                "CanonicalRepresentation" : canonical_rep,
                "Confidence": score
            }

    singleton_id = cluster_id + 1

    with open(output_file, 'w') as f_output, open(input_file) as f_input:
        writer = csv.writer(f_output)
        reader = csv.reader(f_input)

        heading_row = next(reader)
        heading_row.insert(0, 'ConfidenceScore')
        heading_row.insert(0, 'ClusterID')
        canonical_keys = canonical_rep.keys()
        for key in canonical_keys:
            heading_row.append('Canonical_' + key)

        writer.writerow(heading_row)

        for row in reader:
            row_id = row[0]
            if row_id in cluster_membership:
                cluster_id = cluster_membership[row_id]["ClusterID"]
                canonical_rep = cluster_membership[row_id]["CanonicalRepresentation"]
                row.insert(0, cluster_membership[row_id]['Confidence'])
                row.insert(0, cluster_id)
                for key in canonical_keys:
                    row.append(canonical_rep[key].encode('utf8'))
            else:
                row.insert(0, None)
                row.insert(0, singleton_id)
                singleton_id += 1
                for key in canonical_keys:
                    row.append(None)
            writer.writerow(row)

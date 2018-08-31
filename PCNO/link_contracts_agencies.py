# Adapted from:
# https://dedupeio.github.io/dedupe-examples/docs/record_linkage_example.html
from __future__ import print_function
from future.builtins import next

import os
import csv
import re
import collections
import logging
import optparse
import numpy

import dedupe
from unidecode import unidecode


# Define filenames
DATA1 = '../../../rcc-uchicago/PCNO/CSV/chicago/hq_agencies_names.csv'
DATA2 = '../../../rcc-uchicago/PCNO/CSV/chicago/service_agencies_names.csv'
output_file = '../../../rcc-uchicago/PCNO/CSV/chicago/2018-07-03_link_agencies_output.csv'
settings_file = '../../../rcc-uchicago/PCNO/CSV/chicago/2018-07-03_link_agencies_learned_settings.dedupe'
training_file = '../../../rcc-uchicago/PCNO/CSV/chicago/2018-07-03_link_agencies_training.json'


def preProcess(column):
    '''
    Does minor pre-processing on a cell value.
    '''
    try : # python 2/3 string differences
        column = column.decode('utf8')
    except AttributeError:
        pass
    column = unidecode(column)
    column = re.sub(' OF ',' ',column)
    column = column.strip().strip('"').strip("'").strip()

    return column


def readData(filename):
    '''
    Reads in the data, passing the values to the pre-processor for cleaning.
    Returns a dictionary.
    '''
    data_d = {}

    with open(filename) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            clean_row = dict([(k, preProcess(v)) for (k, v) in row.items()])
            data_d[filename + str(i)] = dict(clean_row)

    return data_d


if __name__ == '__main__':

    optp = optparse.OptionParser()
    optp.add_option('-v', '--verbose', dest='verbose', action='count',
                    help='Increase verbosity (specify multiple times for more)'
                    )
    (opts, args) = optp.parse_args()
    log_level = logging.WARNING
    if opts.verbose :
        if opts.verbose == 1:
            log_level = logging.INFO
        elif opts.verbose >= 2:
            log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)


    print('importing data ...')
    data_1 = readData(DATA1)
    data_2 = readData(DATA2)


    if os.path.exists(settings_file):
        print('reading from', settings_file)
        with open(settings_file, 'rb') as sf :
            linker = dedupe.StaticRecordLink(sf)
    else:
        fields = [
        {'field' : 'VendorName', 'type': 'String'}]

        linker = dedupe.RecordLink(fields)

        linker.sample(data_1, data_2, 15000)

        if os.path.exists(training_file):
            print('reading labeled examples from ', training_file)
            with open(training_file) as tf :
                linker.readTraining(tf)


        print('starting active labeling...')

        dedupe.consoleLabel(linker)

        linker.train()

        with open(training_file, 'w') as tf :
            linker.writeTraining(tf)

        with open(settings_file, 'wb') as sf :
            linker.writeSettings(sf)

        print('clustering...')
        linked_records = linker.match(data_1, data_2, 0)

        print('# duplicate sets', len(linked_records))

        cluster_membership = {}
        cluster_id = None
        for cluster_id, (cluster, score) in enumerate(linked_records):
            for record_id in cluster:
                cluster_membership[record_id] = (cluster_id, score)

        if cluster_id :
            unique_id = cluster_id + 1
        else :
            unique_id =0


        with open(output_file, 'w') as f:
            writer = csv.writer(f)

            header_unwritten = True

            for fileno, filename in enumerate((DATA1,DATA2)):
                with open(filename) as f_input :
                    reader = csv.reader(f_input)

                    if header_unwritten :
                        heading_row = next(reader)
                        heading_row.insert(0, 'SourceFile')
                        heading_row.insert(0, 'LinkScore')
                        heading_row.insert(0, 'ClusterID')
                        writer.writerow(heading_row)
                        header_unwritten = False
                    else :
                        next(reader)

                    for row_id, row in enumerate(reader):
                        cluster_details = cluster_membership.get(filename + str(row_id))
                        if cluster_details is None :
                            cluster_id = unique_id
                            unique_id += 1
                            score = None
                        else :
                            cluster_id, score = cluster_details
                        row.insert(0, fileno)
                        row.insert(0, score)
                        row.insert(0, cluster_id)
                        writer.writerow(row)

from pyjarowinkler import distance
import pandas as pd
import threading, os, csv, multiprocessing, re, sys, json
from threading import Thread
from queue import Queue
from STANDARDIZE_NAME import standardize_name

#Logan Noel
#Sep 11, 2017


#Observe the functionality of this program by calling "sample_run()", or
#run deduped_contract from Ipython3 to disambiguate an entire file.

#running python3 dedupe_contracts.py -f filename will run a specific file
#adding a -r tag will launch in recovery mode


'''
Additional notes, 2018/06/12, Erin M. Ochoa
-------------------------------------------
This file deduplicates the names of contracting agencies from the Chicago, Cook,
and Illinois contacts dataset.

UPDATED: Added a global constant with the correct path to the input file.

TO EXECUTE A SAMPLE RUN:
-----------------------
-In iPython3:
               from dedupe_contracts import *
               sample_run()
'''


INPUT = '../CSV/chicago/MERGED_chi_cook_il_FULL_VARS.csv'

def sub_job(index, data, subset, threshold, completion):
    '''
    The job for a single thread. Iterates through the names and tries
    to find a match. If it does, writes to temp csv.
    '''
    primary = data['VendorName']
    already_examined = set([])
    if completion:
        print("~{} percent done with matching".format(completion))
    for sub_index, sub_data in subset.iterrows():
        secondary = sub_data['VendorName']
        if index != sub_index and secondary not in already_examined:
            jw_score = distance.get_jaro_distance(primary, secondary, winkler=True)
            if jw_score >= threshold and jw_score < 1:
                with open('dedupe_working_data.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([primary, secondary])
        already_examined.add(secondary)


class Worker(Thread):
    '''
    A single thread, which executes querying tasks.
    '''
    def __init__(self, queue):
       Thread.__init__(self)
       self.queue = queue

    def run(self):
       while True:
           index, data, subset, threshold, completion = self.queue.get()
           sub_job(index, data, subset, threshold, completion)
           self.queue.task_done()


def load_data(filename=INPUT,seed=345, subset=False):
    '''
    Load the csv of uncleaned contracts into a dataframe.
    '''
    df = pd.read_csv(filename)
    df = df.sort_values(by='VendorName',axis=0,inplace=False)
    if subset:
        print('==================================================')
        print('WARNING: YOU ARE WORKING WITH A SUBSET OF THE DATA')
        print('==================================================')
        if seed:
            df = df.sample(n=subset,random_state=seed)
        else:
            df = df.sample(n=subset)
    print("Loaded Data")
    return df


def apply_matches(df, actual_matches, conflicts):
    '''
    Use the actual matches input to apply standardization.
    '''
    to_modify = {}
    for key, value in actual_matches.items():
        if key in conflicts:
            val_list = list(value)
            val_list.append(key)
            print("You gave conflicting information for the following names.")
            print("Select the best option below:")
            for i, item in enumerate(val_list):
                print("{}: {}".format(i + 1, item))
            feedback = ''
            while feedback not in list(range(1,len(val_list) + 1)):
                feedback = input("")
                try:
                    feedback = int(feedback)
                except:
                    feedback = ''
            selected_name = val_list.pop(feedback - 1)
            print("You selected: {}".format(selected_name))
            to_modify[(key, selected_name)] = set(val_list)

    for key, item in to_modify.items():
        old_key = key[0]
        new_key = key[1]
        values = item
        actual_matches.pop(old_key, None)
        actual_matches[new_key] = values

    for key, value in actual_matches.items():
        for index, data in df.iterrows():
            if data['VendorName'] in value:
                old_name = data['VendorName']
                df.loc[index, 'VendorName'] = key
                print("changed {} to {}".format(old_name, key))
    return df


def generate_matches(df, threshold):
    no_cores = multiprocessing.cpu_count() - 1
    if no_cores >= 10:
        no_cores -= 6
    queue = Queue()
    for x in range(no_cores):
        worker = Worker(queue)
        worker.daemon = True
        worker.start()

    if os.path.exists('dedupe_working_data.csv'):
        os.remove('dedupe_working_data.csv')

    len_df = len(df)
    percentages = range(1,20)
    percentages = [round(f / 20 * len_df) for f in percentages]
    counter = 0
    already_examined = set([])
    for index, data in df.iterrows():
        if counter in percentages:
            completion = round(counter / len_df * 100)
        else:
            completion = None
        primary = data['VendorName']
        counter += 1
        if primary not in already_examined:
            subset = df[counter:]
            queue.put((index, data, subset, threshold, completion))
            already_examined.add(primary)
    queue.join()

    return


def match_records(df, rejected=None):
    '''
    Create a new data frame with a column displaying possible
    matching records.
    '''
    if rejected:
        pass
    else:
        threshold = ''
        print('Choose a sensativity threshold for matching records.')
        print('(0.75 is very conservative and will give many false positives,')
        print('while 0.9 will be very quick, although may result in false negatives)')
        while type(threshold) != type(2.718):
            threshold = input("Desired threshold: ")
            try:
                threshold = float(threshold)
                if threshold <= 0 or threshold > 1:
                    print("Invalid threshold. Choose another.")
                    threshold = ''
                else:
                    continue
            except:
                threshold = ''
    for index, data in df.iterrows():
        primary = data['VendorName']
        df.loc[index, 'VendorName'] = standardize_name(primary)
    if rejected:
        pass
        rejected_a = set([(i[0], i[1]) for i in rejected])
        rejected_b = set([(i[1], i[0]) for i in rejected])
    else:
        generate_matches(df, threshold)

    potential_matches = set([])
    with open('dedupe_working_data.csv', 'r') as f:
        reader = csv.reader(f)
        for primary, secondary in reader:
            if (secondary, primary) not in potential_matches:
                potential_matches.add((primary, secondary))

    if rejected:
        potential_matches -= rejected_a
        potential_matches -= rejected_b

    actual_matches = {}
    no_matched = 0
    len_po_matches = len(potential_matches)
    print("If names are a match, enter 1 or 2 to select which name to keep")
    print("If names are not a match, enter 3")
    conflicts = set([])
    rejected = []
    for primary, secondary in potential_matches:

        print("Potential matches evaluated: {} of {} ({} percent done)".format(no_matched, len_po_matches, round(no_matched / len_po_matches * 100)))
        print()
        feedback = 0
        no_matched += 1
        while feedback not in ('1', '2', '3'):
            print("Are the below names a match:")
            feedback = input("1: {}\n2: {}\n3: Not a match\n".format(primary, secondary))
        matched = False
        if feedback == '1':
            if primary in actual_matches.keys():
                actual_matches[primary].add(secondary)
                matched = True
            for key, value in actual_matches.items():
                if primary in value:
                    actual_matches[key].add(secondary)
                    conflicts.add(key)
                    matched = True
                elif secondary in value:
                    actual_matches[key].add(primary)
                    conflicts.add(key)
                    matched = True
            if not matched:
                actual_matches[primary] = set([secondary])
        elif feedback == '2':
            if secondary in actual_matches.keys():
                actual_matches[secondary].add(primary)
                matched = True
            for key, value in actual_matches.items():
                if secondary in value:
                    actual_matches[key].add(primary)
                    matched = True
                    conflicts.add(key)
                elif primary in value:
                    actual_matches[key].add(secondary)
                    conflicts.add(key)
                    matched = True
            if not matched:
                actual_matches[secondary] = set([primary])
        else:
            rejected.append([primary, secondary])

        if no_matched % 25 == 0:
            print('Saving work...')
            path = 'dedupe_recovery_data/'
            file1 = path + 'actual_matches_rec.json'
            file2 = path + 'conflicts.csv'
            file3 = path + 'rejected.csv'
            for key, item in actual_matches.items():
                actual_matches[key] = list(item)
            if os.path.exists(file1):
                os.remove(file1)
            if os.path.exists(file2):
                os.remove(file2)
            if os.path.exists(file3):
                os.remove(file3)
            to_json(actual_matches, file1)
            to_csv(list(conflicts), file2)
            to_csv(rejected, file3)
            print('Saved work to .../dedupe_recovery_data/..')
            for key, item in actual_matches.items():
                actual_matches[key] = set(item)

    df = apply_matches(df, actual_matches, conflicts)
    os.remove('dedupe_working_data.csv')

    return df


def recover_dat(filename=INPUT, sample=False):
    if os.path.exists('dedupe_recovery_data'):
        pass
    else:
        print('No recovery data exists. Exit now')

    actual_matches = from_json('dedupe_recovery_data/actual_matches_rec.json')
    conflicts = read_csv('dedupe_recovery_data/conflicts.csv')

    if filename:
        if sample:
            df = load_data(filename, 12345, 300)
        else:
            df = load_data(filename)
    else:
        if sample:
            df = load_data(seed=12345,subset=300)
        else:
            df = load_data()
    df = apply_matches(df, actual_matches, conflicts)

    return df


def from_json(filename):
    with open(filename) as json_file:
        data = json.load(json_file)

    for key, value in data.items():
        data[key] = set(value)
    return data

def to_json(data, filename):
    with open(filename, 'w') as fp:
        json.dump(data, fp)

def to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename)

def read_csv(filename):
    df = pd.read_csv(filename)
    if len(df) > 0:
        if filename == 'dedupe_recovery_data/rejected.csv':
            data = []
            for i, row in df.iterrows():
                data.append((row[1], row[2]))
            return data
        else:
            return list(df['0'])
    else:
        return []


def write_data(df, filename='deduped_contract_results.csv'):
    '''
    Write dataframe to file.
    '''
    filename = os.getcwd() + '/' + filename
    df.to_csv(filename)
    print()
    print('Data was written to {}'.format(filename))

    return

def assign_id(df):
    '''
    Assign a unique ID to each vendor in the dataset.
    '''
    df['CSDS_Vendor_ID'] = ''
    df = df.sort_values(by='VendorName',axis=0,inplace=False)
    prev_names = {}
    counter = 0
    for i, data in df.iterrows():
            if df.loc[i,'VendorName'] in prev_names.keys():
                df.loc[i, 'CSDS_Vendor_ID'] = prev_names[df.loc[i,'VendorName']]
            else:
                counter += 1
                id_string = 'vendor_{}'.format(counter)
                df.loc[i, 'CSDS_Vendor_ID'] = id_string
                prev_names[df.loc[i,'VendorName']] = id_string
    return df

def sample_run(seed=12345, recovery_df=None):
    '''
    Runs the full process through a subset of the data as a demonstration.
    '''
    df = load_data(INPUT, seed, 300)
    df = match_records(df)
    df = assign_id(df)
    write_data(df,'sample_deduped_contract_results.csv')


def main(filename):
    if os.path.exists('dedupe_recovery_data'):
        pass
    else:
        os.mkdir('dedupe_recovery_data')
    if filename:
        df = load_data(filename)
    df = match_records(df)
    df = assign_id(df)
    write_data(df)

def recovery(filename):
    if filename:
        df = recover_dat(filename)
    print('Applied recorded matches. Continuting on:')
    print()
    rejected = read_csv('dedupe_recovery_data/rejected.csv')
    df = match_records(df, rejected=rejected)
    df = assign_id(df)
    write_data(df)


def sample_recovery():
    df = recover_dat(sample=True)
    sample_run(recovery_df=df)

    return


if __name__ == '__main__':
    for i in range(0,len(sys.argv)):
        if sys.argv[i] == '-f':
            filename = sys.argv[i + 1]
    if '-r' in sys.argv:
        print('Launching in recovery mode')
        recovery(filename)
    else:
        main(filename)

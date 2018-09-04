import re
import numpy as np
from string import digits as DIGITS
from string import punctuation as PUNCTUATION


NPC = ['\n','\r','\t']
PD = PUNCTUATION + DIGITS
BAD_SUBSTRINGS = ['�']


def standardize_name(input_txt):
    '''
    Written by Hossein Pourreza.

    Ported to Python 3.6 (str.translate has been deprecated); modified.

    Standardizes organization names by converting them to upper-case, removing
    punctuation, standardizing certain abbreviations, replacing multiple spaces
    with a single space, and stripping spaces from the beginning and end.
    '''
    input_txt = str(input_txt)

    # Because all but one of the re.sub expressions require the substring to end
    # in a space, and because this does not work for substrings at the end of a
    # string, add a single space to the end of all strings (which is later
    # stripped off).
    input_txt = input_txt.upper() + ' '

    # NOTE: I commented this out because it was causing np.NaN to turn up in the
    # IRS organization names; a few organizations in Chicago have 'LOS ANGELES'
    # in their name.
    # Return np.NaN for org names that include 'POMONA' OR 'LOS ANGELES'
    #if 'POMONA' in input_txt or 'LOS ANGELES' in input_txt:
        #return np.NaN

    # Replace each non-printing character with a space
    for char in NPC:
        input_txt = input_txt.replace(char,' ')

    # Replace each character in BAD_SUBSTRINGS with the empty string
    for substr in BAD_SUBSTRINGS:
        input_txt = input_txt.replace(substr,'')

    # Replace '&' with ' AND '
    input_txt = re.sub("&"," AND ",input_txt)

    # Fix a stubborn non-ASCII character
    if input_txt.startswith('MUJERES LATINAS EN '):
        return 'MUJERES LATINAS EN ACCION'

    # Fix Y.M.C.A.
    input_txt = re.sub('(^|\s)Y.M.C.A.',' YMCA ',input_txt)

    # Remove punctuation: delete apostrophes (and similar); replace others and
    # digits with spaces
    input_txt = re.sub("'","",input_txt)    # Apostrophe
    input_txt = re.sub("’","",input_txt)    # Angled apostrophe
    input_txt = re.sub("`","",input_txt)    # Backtick
    input_txt = ''.join([x if x not in PD else ' ' for x in input_txt])

    # Standardize several common words, delete stop words, and fix some known
    # misspellings
    input_txt = re.sub(" INC($|\s)"," ",input_txt)
    input_txt = re.sub("(^|\s)THE "," ",input_txt)
    #input_txt = re.sub("(^|\s)(NEW YORK CITY|CITY OF NEW YORK|NEW YORK|NYC) ", " NY ", input_txt)
    input_txt = re.sub("(^|\s)(ASSOC|ASSN|ASSCTN) ", " ASSOCIATION ", input_txt)
    input_txt = re.sub("(^|\s)BENEV ", " BENEVOLENT ", input_txt)
    input_txt = re.sub("(^|\s)(SVC|SVCS|SERV|SRVS|SERVICE) ", " SERVICES ", input_txt)
    input_txt = re.sub("(^|\s)AMBULANCE CORP ", " AMBULANCE CORPS ", input_txt)
    input_txt = re.sub("(^|\s)(CORP|CORPORATION) ", " ", input_txt)
    input_txt = re.sub("(^|\s)(CO|COMPANY) ", " ", input_txt)
    input_txt = re.sub("(^|\s)NPF ", " ", input_txt)
    input_txt = re.sub("(^|\s)DBA ", " ", input_txt)
    input_txt = re.sub("(^|\s)C O ", " ", input_txt)
    input_txt = re.sub("(^|\s)(SCH|SCHL) ", " SCHOOL ", input_txt)
    input_txt = re.sub("(^|\s)SAINT ", " ST ", input_txt)
    #input_txt = re.sub("(^|\s)COMM ", " COMMUNITY ", input_txt)
    input_txt = re.sub("(^|\s)ORG ", " ORGANIZATION ", input_txt)
    input_txt = re.sub("(^|\s)MGMT ", " MANAGEMENT ", input_txt)
    input_txt = re.sub("(^|\s)(THEATRE|THTR) ", " THEATER ", input_txt)
    input_txt = re.sub("(^|\s)WKSHP ", " WORKSHOP ", input_txt)
    input_txt = re.sub("(^|\s)HOSP ", " HOSPITAL ", input_txt)
    input_txt = re.sub("(^|\s)REHABILITATION ", " REHAB ", input_txt)
    input_txt = re.sub("(^|\s)(DEV|DVLPMNT) ", " DEVELOPMENT ", input_txt)
    input_txt = re.sub("(^|\s)COORD ", " COORDINATING ", input_txt)
    input_txt = re.sub("(^|\s)BKLYN ", " BROOKLYN ", input_txt)
    input_txt = re.sub("(^|\s)DPSTRY ", " DEPOSITORY ", input_txt)
    input_txt = re.sub("(^|\s)(CTR|CNTR|CENT) ", " CENTER ", input_txt)
    input_txt = re.sub("(^|\s)(IL|ILL|ILLIOIS) ", " ILLINOIS ", input_txt)
    input_txt = re.sub("(^|\s)CENTERS ", " CENTER ", input_txt)
    input_txt = re.sub("(^|\s)(CHGO|CHICGO|CHIC) ", " CHICAGO ", input_txt)
    input_txt = re.sub("(^|\s)CHLDN ", " CHILDREN ", input_txt)
    input_txt = re.sub("(^|\s)ALTERNTV ", " ALTERNATIVE ", input_txt)
    input_txt = re.sub("(^|\s)SYSTS ", " SYSTEMS ", input_txt)
    input_txt = re.sub("(^|\s)SUBN  ", " SUBURBAN ", input_txt)
    input_txt = re.sub("(^|\s)INST ", " INSTITUTE ", input_txt)
    input_txt = re.sub("(^|\s)HMN ", " HUMAN ", input_txt)
    input_txt = re.sub("(^|\s)(DEPT|DPT) ", " DEPARTMENT ", input_txt)
    input_txt = re.sub("(^|\s)(FNDT|FND) ", " FOUNDATION ", input_txt)
    input_txt = re.sub("(^|\s)(UNIV|UNIVERITY) ", " UNIVERSITY ", input_txt)
    input_txt = re.sub("(^|\s)HLTH ", " HEALTH ", input_txt)
    input_txt = re.sub("(^|\s)PLCY ", " POLICY ", input_txt)
    input_txt = re.sub("(^|\s)DIST ", " DISTRICT ", input_txt)
    input_txt = re.sub("(^|\s)FMLY ", " FAMILY ", input_txt)
    input_txt = re.sub("(^|\s)WKS ", " WORKS ", input_txt)
    input_txt = re.sub("(^|\s)CMNTY ", " COMMUNITY ", input_txt)
    input_txt = re.sub("(^|\s)NTWRK ", " NETWORK ", input_txt)
    input_txt = re.sub("(^|\s)INC ", " INCORPORATED ", input_txt)
    input_txt = re.sub("(^|\s)FOUNDATION FOUNDATION ", "FOUNDATION ", input_txt)
    #input_txt = re.sub("(^|\s)CITY OF ", "", input_txt)

    # One vendor's name is missing a space, so just delete all remaining
    # instances of 'CORPORATION '
    input_txt = re.sub("CORPORATION ", " ", input_txt)
    input_txt = re.sub("(^|\s)AND ", " ", input_txt)
    input_txt = re.sub("(^|\s)OR ", " ", input_txt)
    input_txt = re.sub("(^|\s)IN ", " ", input_txt)
    input_txt = re.sub("(^|\s)ON ", " ", input_txt)
    input_txt = re.sub("(^|\s)AT ", " ", input_txt)
    input_txt = re.sub("(^|\s)FOR ", " ", input_txt)
    input_txt = re.sub("(^|\s)THE ", " ", input_txt)
    #input_txt = re.sub("(^|\s)A ", " ", input_txt)
    input_txt = re.sub("(^|\s)AN ", " ", input_txt)
    input_txt = re.sub("(^|\s)LLC ", "", input_txt)
    input_txt = re.sub("(^|\s)NFP ", "", input_txt)
    input_txt = re.sub("(^|\s)PC ", "", input_txt)
    input_txt = re.sub("(^|\s)DHQ ", " ", input_txt)
    input_txt = re.sub("(^|\s)THEIR ", " ", input_txt)
    input_txt = re.sub("(^|\s)SPF ", " ", input_txt)

    # Replace multiple spaces with one and trim leading and trailing whitespace
    input_txt = re.sub('\s+',' ',input_txt)
    input_txt = input_txt.strip()

    return input_txt

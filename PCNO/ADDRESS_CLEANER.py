import re
import numpy as np
import pandas as pd


def address_cleaner(string):
    '''
    Cleans addresses by replacing forbidden characters with spaces or deleting
    them.  Also standardizes addresses to some extent.
    '''

    # Strip leading and trailing spaces, commas, & periods; convert to uppercase
    string = string.strip(' ,./').upper()

    # Contains non-printing characters that will be cleaned out of strings
    cleaner = ['\n','\r','\t']

    # If present in the string, replace each NPC from cleaner with a space
    for npc in cleaner:
        string = string.replace(npc, ' ')

    # Replace multiple spaces with a single space
    string = re.sub(r'\s+',' ',string)

    # Remove replacement character, which will break things later on
    string = string.replace('�','')

    # Replace each parenthesis with a space
    string = re.sub(r'\(',' ',string)
    string = re.sub(r'\)',' ',string)

    # Standardize P.O. BOX
    string = re.sub(r'^P\.?\s?O\.?\s?BOX','P.O. BOX',string)
    string = re.sub(r'^POST\s?OFFICE\s?BOX','P.O. BOX',string)
    string = re.sub(r'^POST\s?OFC\s?BOX','P.O. BOX',string)

    # Replace any PO BOX address with the empty string
    string = re.sub(r'^P.O. BOX\s?([0-9]+)?','',string)

    # Remove the EFT ST, EFT, and BSMT strings from the end of the address
    string = re.sub(r'\sEFT ST\s?$','',string)
    string = re.sub(r'\sEFT\sDR$',' DRIVE',string)
    string = re.sub(r'\sEFT\s?$','',string)
    string = re.sub(r'\sBSMT\s?$','',string)

    # Replace spelled-out numbered street names with ordinal names
    string = re.sub(r'\sFIRST',' 1ST',string)
    string = re.sub(r'\sSECOND',' 2ND',string)
    string = re.sub(r'\sTHIRD',' 3RD',string)
    string = re.sub(r'\sFOURTH',' 4TH',string)
    string = re.sub(r'\sFIFTH',' 5TH',string)
    string = re.sub(r'\sSIXTH',' 6TH',string)
    string = re.sub(r'\sSEVENTH',' 7TH',string)
    string = re.sub(r'\sEIGHTH',' 8TH',string)
    string = re.sub(r'\sNINTH',' 9TH',string)
    string = re.sub(r'\sTENTH',' 10TH',string)

    # Replace spelled-out address number with a digit
    string = re.sub(r'^ONE ','1 ',string)
    string = re.sub(r'^TWO ','2 ',string)
    string = re.sub(r'^THREE ','3 ',string)
    string = re.sub(r'^FOUR ','4 ',string)
    string = re.sub(r'^FIVE ','5 ',string)
    string = re.sub(r'^SIX ','6 ',string)
    string = re.sub(r'^SEVEN ','7 ',string)
    string = re.sub(r'^EIGHT ','8 ',string)
    string = re.sub(r'^NINE ','9 ',string)

    # Remove floor, suite, unit, and room numbers
    string = re.sub(r'\s#\s[0-9]+[A-Z]+$','',string) # '# 511 MB'
    string = re.sub(r'\s[A-Z]+\/+[A-Z]+\s[0-9]+$','',string) # M/C 779
    string = re.sub(r'\s#\s[A-Z]+[0-9]+','',string) # '# MC6091'
    string = re.sub(r'\sFL\s[0-9]+,?\s?[0-9]+\sAND\s[0-9]+$','',string) # FL 1,2 AND 3
    string = re.sub(r'\sFL\s[0-9]+,?([0-9]+)?$','',string) # FL 1,2
    string = re.sub(r'\s[0-9]+(TH)\s(SUITE|APARTMENT|NUMBER|FLOOR|ROOM|UNIT|STE\.?|NO\.?|FL\.?|RM\.?|APT\.?)','',string)
    string = re.sub(r'\s[0-9]+\s(TH)\s(STE\.?|APT\.?|NO\.?|FL\.?|RM\.?)(?=\s+|$)','',string)
    string = re.sub(r'\s(SUITE|APARTMENT|NUMBER|FLOOR|ROOM|UNIT|STE\.?|NO\.?|FL\.?|RM\.?|APT\.?)\s+\d+(ST|ND|RD|TH)','',string) # Floor/Suite with ordinal after
    string = re.sub(r'\s(SUITE|APARTMENT|NUMBER|FLOOR|ROOM|UNIT|STE\.?|NO\.?|FL\.?|RM\.?|APT\.?)\s(\d+[A-Z]\d+)-([0-9])$','',string) #Complex suite after
    string = re.sub(r'\s(SUITE|APARTMENT|NUMBER|FLOOR|ROOM|UNIT|STE\.?|NO\.?|FL\.?|RM\.?|APT\.?)\s([0-9]+|[A-Z]+)-([0-9]+|[A-Z]+)$','',string) #Slightly simpler suite after
    string = re.sub(r'\s(\d+[A-Z])(?=$)','',string) # Number and letter unit after
    string = re.sub(r'\s#\s(\d+)?[A-Z](?=$)','',string) # Letter unit after
    string = re.sub(r'\s(SUITE|APARTMENT|NUMBER|FLOOR|ROOM|UNIT|STE\.?|NO\.?|FL\.?|RM\.?|APT\.?)\s?(\d+-?\d*)$','',string) # FLOOR before
    string = re.sub(r'(\s|,|\.)+\s?(SUITE|APARTMENT|NUMBER|FLOOR|ROOM|UNIT|STE\.?|NO\.?|FL\.?|RM\.?|APT\.?)\s(\w+)','',string) # ROOM|SUITE before  HERE
    string = re.sub(r'\s#\s?\d+','',string) # Pound sign with number after
    string = re.sub(r'\s(SUITE|APARTMENT|NUMBER|FLOOR|ROOM|UNIT|STE\.?|NO\.?|FL\.?|RM\.?|APT\.?)\s+\d+(,)*(\s)*(\d)*(\s)*(AND)*(\s)*(\d)*','',string) # Floor with comma after
    string = re.sub(r'\s\d+(\/)*(\s)*(\d)*(\s)*$','',string) # Numbers with slash after
    string = re.sub(r'\s(\d+)(?=$)','',string) # Number (no label) after
    string = re.sub(r'\s(SUITE|APARTMENT|NUMBER|FLOOR|ROOM|UNIT|STE\.?|NO\.?|FL\.?|RM\.?|APT\.?)\s?$','',string) # Label with no number after
    string = re.sub(r'\s\d+\s*(ST|ND|RD|TH)*\s(FLOOR|SUITE|ROOM|UNIT|FL\.?|STE\.?)','',string) # Number with ordinal and floor after
    string = re.sub(r'\s[0-9]+$','',string) # Trailing unit number with no label
    string = re.sub(r'\s[0-9]+[A-Z]*\sF$','',string) # Trailing floor with partial label afterward

    # Replace abbreviated directions with full words
    string = re.sub(r'\sE\.?(?=\s|$)',' EAST',string)
    string = re.sub(r'\sW\.?(?=\s|$)',' WEST',string)
    string = re.sub(r'\sN\.?(?=\s|$)',' NORTH',string)
    string = re.sub(r'\sS\.?(?=\s|$)',' SOUTH',string)

    # Fix hyphenated addresses that have spaces
    string = re.sub(r'\s?-\s?','-',string)

    # Strip off hyphens, commas, pound signs, and extra spaces
    string = string.strip(' -,#')

    # Replace street type abbreviations with full words
    string = re.sub(r'\sTERR\.?(?=\s|$|,)',' TERRACE ',string)
    string = re.sub(r'\sTER\.?(?=\s|$|,)',' TERRACE ',string)
    string = re.sub(r'\sSQ\.?(?=\s|$|,)',' SQUARE ',string)
    string = re.sub(r'\sCT\.?(?=\s|$|,)',' COURT ',string)
    string = re.sub(r'\sRD\.?(?=\s|$|,)',' ROAD ',string)
    string = re.sub(r'\sPL\.?(?=\s|$|,)',' PLACE ',string)
    string = re.sub(r'\sPLZ\.?(?=\s|$|,)',' PLAZA ',string)
    string = re.sub(r'\sLP\.?(?=\s|$|,)',' LOOP ',string)
    string = re.sub(r'\sLN\.?(?=\s|$|,)',' LANE ',string)
    string = re.sub(r'\sCIR\.?(?=\s|$|,)',' CIRCLE ',string)
    string = re.sub(r'\sBLVDRD\.?(?=\s|$|,)',' BOULEVARD ',string)
    string = re.sub(r'\sBLVD\.?(?=\s|$|,)',' BOULEVARD ',string)
    string = re.sub(r'\sAVE\.?(?=\s|$|,)',' AVENUE ',string)
    string = re.sub(r'\sEXPWY\.?(?=\s|$|,)',' EXPRESSWAY ',string)
    string = re.sub(r'\sHWY\.?(?=\s|$|,)',' HIGHWAY ',string)
    string = re.sub(r'\sPWY\.?(?=\s|$|,)',' PARKWAY ',string)
    string = re.sub(r'\sPKWY\.?(?=\s|$|,)',' PARKWAY ',string)
    string = re.sub(r'\sST\.?(?=$|\s$|,\s$)',' STREET ',string) # Ends in ST|ST.
    string = re.sub(r'\sDR\.?(?=$|\s$|,\s$)',' DRIVE ',string) # Ends in DR|DR.

    # Hard-coded replacements for unusual values
    string = re.sub(r'^(C/O WEST DOLIN-|ATTN DEBORAH FOSTER-BONNER|C/O C EILIAN)','',string)
    string = re.sub(r'\sIL4-135-14-19','',string)
    string = re.sub(r'(/ ROBERT JOHNSON|KELLY WHITE AT THE PRIVATEBANK)$','',string)
    string = re.sub(r'\sRIVERSIDE PLAZA(R|O)\s?$',' RIVERSIDE PLAZA',string)
    string = re.sub(r'^(C/O M M LTD|C/O MARY PAGE|C/O BRIAN BLACKLAW|C/O APUCHOVITZ)','',string)
    string = re.sub(r'^(HH LLP|C/O BEN M ROTH|C/O ABDUZ-ZAHIR MOHYUDDIN|C/O MJMS)','',string)
    string = re.sub(r'(-C297|H-1|\sRM/-1|-B|UPPER LEVEL|3C-19|)$','',string)

    string = re.sub(r'\s+',' ',string)

    return string.strip()

def round2(df):
    '''
    Hard-coded cleaning for the addresses that can be salvaged. Returns a
    dataframe.
    '''

    # Define some shortcuts
    nm = 'Name'
    ct = 'City'
    st = 'State'
    add1 = 'Address1'
    add2 = 'Address2'
    z = 'ZipCode'
    chicago = 'CHICAGO'
    il = 'IL'

    # If the city is Chicago and the state is missing, add the state
    df[st] = df.apply(lambda x: il if x[ct].upper() == chicago else x[st], axis=1)

    # Values that need to be overridden
    badvals = ['UNION PARK FIELDHOUSE','AUSTIN SCHOOL HEALTH CENTER',
               'LOWER WEST SIDE NEIGHBORHOOD HEALTH CENTER','ASHLAND CLINIC',
               'AUSTIN/LAWNDALE','REAVIS SCHOOL-BASED HEALTH CENTER',
               '& SOFTWARE','ADVOCATE OCCUP HLTH','GRANTS & CONTRACTS MC 551',
               'CHGO JANE ADDAMS COLLEGE','VELOPMENT COMMISSION',
               'ATT. MARK BALLARD','ST. PIUS V PARISH/HOPE','ST. SABINA PARISH',
               'ARCHDIOCESE OF CHICAGO','MORGAN PARK HIGH SCHOOL',
               'ASSOCIATION INC','CIVIL RIGHTS','WOMENS NETWORK      (EFT)',
               'IT ADDS UP','HOUSING','ATTN: DIRECTOR OF RESTRICTED ACCOUNTING',
               '8601 S STATE ST # 1','DEV. CORP.','GIRLS OF GRACE YOUTH CENTER',
               'CENTER (AGENT)ROBERT BUCHANAN','METROPOLITAN OF CHICAGO',
               'COUNCIL','& GOODWILL, INC','FOR JOBS INC.','C/O THOMAS TRESSER',
               'C/O REYES GUACOLDA','PLAZA ARMS','ST. SABINA','MARIA SHELTER',
               'DEPT OF MEDICINE RM W 600','COMMUNITY DEVELOPMENT COUNCIL',
               'WESTERN KENTUCKY UNIV.','ATTN: BUSINESS OFFICE/J. REED',
               'CENTER','MARQUETTE NATIONAL BANK','INVESTMENT CORP.',
               'INDUSTRY ASSOCIATION (HACIA)','INDUSTRY ASSOCIATION HACIA',
               'CENTER AGENT ROBERT BUCHANAN','& GOODWILL INC','FOR JOBS INC']

    badvals2 = [r'BUSINESS ASSOC',r'NEIGHBORS AGAINST GANG VIOLENC']

    # Replace null values in add1 and add2
    df[add1] = df[add1].replace(np.NaN,'')
    df[add2] = df[add2].replace(np.NaN,'')

    # Delete strings that start with a phone number
    df[add2] = df[add2].apply(lambda x: '' if x.startswith('PHONE') else x)

    # If there's nothing in add1, copy in add2
    df[add1] = df.apply(lambda x: x[add2] if x[add1] == '' else x[add1], axis=1)

    # If add1 should be overridden, override it with add2
    df[add1] = df.apply(lambda x: x[add2] if x[add1] in badvals else x[add1], axis=1)

    # If add2 == add1, delete the string in add2
    df[add2] = df.apply(lambda x: '' if x[add1] == x[add2] else x[add2], axis=1)

    # If the string is in badvals2, replace it with the empty string
    df[add1] = df[add1].apply(lambda x: '' if x.strip('.') in badvals2 else x)

    # Fix the values for Comer Children's Hospital
    cch = '"COMER CHILDRENS HOSPITAL, 5721 SOUTH MARYLAND AVENUE"'
    cch_fixed = '5721 SOUTH MARYLAND AVENUE'
    df[add1] = df[add1].replace(cch,cch_fixed)

    # Fix the values for Anixter Center
    aac = 'ACCESS @ ANIXTER CENTER-2020 NORTH CLYBOURN AVENUE'
    aac_fixed = '2020 N CLYBOURN AVENUE'
    df[add1] = df[add1].replace(aac,aac_fixed)

    # Fix the values for Rush U
    rush = 'RUSH WEST CAMPUS, 2150 WEST HARRISON STREET'
    rush_fixed = '2150 W HARRISON STREET'
    df[add1] = df[add1].replace(rush,rush_fixed)

    # Fix the values for a certain Resurrection location
    res = 'DOWNERS GROVE 2001 BUTTERFIELD ROAD'
    res_fixed = '2001 BUTTERFIELD ROAD'
    df[add1] = df[add1].replace(res,res_fixed)

    # Strip off unit numbers
    df[add1] = df[add1].apply(lambda x: x.split(' NO ')[0])

    # Fix the Sedgwick addresses
    sedg = '1530 NORTH SEDGWICK AVENUE'
    sedg_fixed = '1530 N SEDGWICK STREET'
    z60610 = 60610
    df[add1] = df[add1].replace(sedg,sedg_fixed)
    df[z] = df.apply(lambda x: z60610 if x[add1] == sedg_fixed else x[z], axis=1)

    # Fix the N Desplaines addresses
    desp = '506 NORTH DES PLAINES'
    desp_fixed = '506 N DESPLAINES STREET'
    desp2 = '126 NORTH DES PLAINES'
    desp2_fixed = '126 N DESPLAINES STREET'
    z60654 = 60654
    z60661 = 60661
    df[add1] = df[add1].replace(desp,desp_fixed)
    df[z] = df.apply(lambda x: z60654 if x[add1] == desp_fixed else x[z], axis=1)
    df[z] = df.apply(lambda x: z60661 if x[add1] == desp2_fixed else x[z], axis=1)

    # Fix the W Hubbard zip
    hub = '162 WEST HUBBARD'
    df[z] = df.apply(lambda x: z60654 if x[add1] == hub else x[z], axis=1)

    # Fix the N Dearborn address and zip
    dear = '801 NORTH DEARBORN'
    dear2 = 'ONE NORTH DEARBORN'
    dear2_fixed = '1 N DEARBORN'
    df[z] = df.apply(lambda x: z60610 if x[add1] == dear else x[z], axis=1)
    df[add1] = df[add1].replace(dear2,dear2_fixed)

    # Fix the Greater Auburn-Gresham addresses
    gag = '7901 WEST 79TH STREET'
    gag_fixed = '1159 W 79TH STREET'
    z60620 = 60620
    df[add1] = df[add1].replace(gag,gag_fixed)
    df[z] = df.apply(lambda x: z60620 if x[add1] == gag_fixed else x[z], axis=1)

    # Fix the Racine addresses
    raci = '7800 SOUTH RACINE STREET'
    raci_fixed = '7800 S RACINE AVENUE'
    df[add1] = df[add1].replace(raci,raci_fixed)
    df[z] = df.apply(lambda x: z60620 if x[add1] == raci_fixed else x[z], axis=1)

    # Fix the Wilson zips
    wils = '1945 SOUTH WILSON AVENUE'
    wils2 = '939 WEST WILSON'
    wils3 = '909 WEST WILSON'
    z60640 = 60640
    df[z] = df.apply(lambda x: z60640 if x[add1] == wils else x[z], axis=1)
    df[z] = df.apply(lambda x: z60640 if x[add1] == wils2 else x[z], axis=1)
    df[z] = df.apply(lambda x: z60640 if x[add1] == wils3 else x[z], axis=1)

    # Fix the Sunnyside zip
    sunny = '1807 WEST SUNNYSIDE'
    df[z] = df.apply(lambda x: z60640 if x[add1] == sunny else x[z], axis=1)

    # Fix the Sheridan zips
    sher = '4730 NORTH SHERIDAN'
    sher2 = '4750 NORTH SHERIDAN'
    sher3 = '4838 NORTH SHERIDAN'
    df[z] = df.apply(lambda x: z60640 if x[add1] == sher else x[z], axis=1)
    df[z] = df.apply(lambda x: z60640 if x[add1] == sher2 else x[z], axis=1)
    df[z] = df.apply(lambda x: z60640 if x[add1] == sher3 else x[z], axis=1)

    # Fix the Ravenswood zips
    rav = '4411 NORTH RAVENSWOOD'
    rav2 = '4432 NORTH RAVENSWOOD'
    rav3 = '4711 NORTH RAVENSWOOD'
    df[z] = df.apply(lambda x: z60640 if x[add1] == rav else x[z], axis=1)
    df[z] = df.apply(lambda x: z60640 if x[add1] == rav2 else x[z], axis=1)
    df[z] = df.apply(lambda x: z60640 if x[add1] == rav3 else x[z], axis=1)

    # Fix the Broadway zips
    bro = '4554 NORTH BROADWAY'
    bro2 = '5050 NORTH BROADWAY'
    bro3 = '5110 BROADWAY STREET'
    df[z] = df.apply(lambda x: z60640 if x[add1] == bro else x[z], axis=1)
    df[z] = df.apply(lambda x: z60640 if x[add1] == bro2 else x[z], axis=1)
    df[z] = df.apply(lambda x: z60640 if x[add1] == bro3 else x[z], axis=1)

    # Fix the Devon zip
    dev = '1541 WEST DEVON'
    z60660 = 60660
    df[z] = df.apply(lambda x: z60660 if x[add1] == dev else x[z], axis=1)

    # Fix the Ames Middle School address
    ames = 'AMES MIDDLE SCHOOL'
    ames_fixed = '1920 N HAMLIN AVENUE'
    df[add1] = df[add1].replace(ames,ames_fixed)

    # Fix the College Heights address
    coll = '1906 COLLEGE BOULEVARD'
    coll_fixed = '1906 COLLEGE HEIGHTS BOULEVARD'
    df[add1] = df[add1].replace(coll,coll_fixed)

    # Fix the Flournoy address, though I'm not sure what is wrong
    flo = '3728 WEST FLOURNOY'
    flo_fixed = '3728 W FLOURNOY STREET'
    df[add1] = df[add1].replace(flo,flo_fixed)

    # Fix the LaSalle address
    las = '1 NORTH LA SALLE'
    las_fixed = '1 N LASALLE STREET'
    df[add1] = df[add1].replace(las,las_fixed)

    # Fix the Belmont zip
    bel = '1110 WEST BELMONT'
    z60657 = 60657
    df[z] = df.apply(lambda x: z60657 if (x[add1] == bel and x[z] == 66057) else x[z], axis=1)

    # Fix the Gregory Street address
    greg = '12935 SOUTH GREGORY'
    greg_fixed = '12935 GREGORY STREET'
    df[add1] = df[add1].replace(greg,greg_fixed)

    # Fix the Randolph addresses
    ran = '1501 WEST RANDOLPH STREET'
    ran_fixed = '1501 W RANDOLPH STREET'
    ran2 = '205 WEST RANDOLPH'
    ran2_fixed = '205 W RANDOLPH STREET'
    df[add1] = df[add1].replace(ran,ran_fixed)
    df[add1] = df[add1].replace(ran2,ran2_fixed)

    # Fix the Ashland address
    ash = '1713 SOUTH ASHLAND'
    ash_fixed = '1713 S ASHLAND AVENUE'
    df[add1] = df[add1].replace(ash,ash_fixed)

    # Fix the Hazel Crest city
    ehc = 'EAST HAZEL CREST'
    hc = 'HAZEL CREST'
    df[add1] = df[add1].replace(ehc,hc)

    # Fix the Cermak address
    cer = '2015 WEST CERMAK ROAD'
    cer_fixed = '2015 W CERMAK ROAD'
    df[add1] = df[add1].replace(cer,cer_fixed)

    # Fix the Round Lake Beach address
    round = '224 CLARENDON AVENUE'
    round_fixed = '224 W CLARENDON DRIVE'
    z60073 = 60073
    df[z] = df.apply(lambda x: z60657 if (x[add1] == round_fixed and x[z] == 60101) else x[z], axis=1)

    # Fix the Pine Ave. address
    pine = '231 NORTH PINE'
    pine_fixed = '231 N PINE AVENUE'
    df[add1] = df[add1].replace(pine,pine_fixed)

    # Fix the Wabash address and zip
    wab = '333 SOUTH WABASH'
    wab_fixed = '333 S WABASH AVENUE'
    z60604 = 60604
    df[add1] = df[add1].replace(wab,wab_fixed)
    df[z] = df.apply(lambda x: z60604 if x[add1] == wab_fixed else x[z], axis=1)

    # Fix the Dr. King addresses
    king = '4150 SOUTH DR MARTIN LUTHER KING JR DRIVE'
    king_fixed = '4150 S MARTIN LUTHER KING DRIVE'
    df[add1] = df[add1].replace(king,king_fixed)

    # Fix the Division addresses
    div = '4909 WEST DIVISION'
    div_fixed = '4909 W DIVISION STREET'
    div2 = '5901 WEST DIVISION AVENUE'
    div2_fixed = '5901 W DIVISION STREET'
    z60651 = 60651
    df[add1] = df[add1].replace(div,div_fixed)
    df[add1] = df[add1].replace(div2,div2_fixed)
    df[z] = df.apply(lambda x: z60651 if x[add1] == div2_fixed else x[z], axis=1)

    # Fix the Fullerton address and zip
    full = '5005 WEST FULLERTON'
    full_fixed = '5005 W FULLERTON AVENUE'
    z60639 = 60639
    df[add1] = df[add1].replace(full,full_fixed)
    df[z] = df.apply(lambda x: z60639 if x[add1] == full_fixed else x[z], axis=1)

    # Fix the Dominican U address
    dom = '7000 WEST DIVISION STREET'
    dom_fixed = '7000 DIVISION STREET'
    df[add1] = df[add1].replace(dom,dom_fixed)

    # Fix the Ingleside address
    ing = '7200 SOUTH INGLESIDE'
    ing_fixed = '7200 S INGLESIDE AVENUE'
    z60619 = 60619
    df[add1] = df[add1].replace(ing,ing_fixed)
    df[z] = df.apply(lambda x: z60619 if x[add1] == ing_fixed else x[z], axis=1)

    # Fix the St. Lawrence address
    stlaw = '7249 ST LAWRENCE'
    stlaw_fixed = '7249 S ST LAWRENCE AVENUE'
    df[add1] = df[add1].replace(stlaw,stlaw_fixed)

    # Fix the Harvard address
    har = '7525 SOUTH HARVARD'
    har_fixed = '7525 S HARVARD AVENUE'
    df[add1] = df[add1].replace(har,har_fixed)
    df[z] = df.apply(lambda x: z60620 if x[add1] == har_fixed else x[z], axis=1)

    # Fix the 50th Street address
    fif = '834 EAST 50TH STREET'
    fif_fixed = '834 E 50TH STREET'
    df[add1] = df[add1].replace(fif,fif_fixed)

    # Fix the Constance address
    con = '8618 SOUTH CONSTANCE'
    con_fixed = '8618 S CONSTANCE AVENUE'
    z60617 = 60617
    df[add1] = df[add1].replace(con,con_fixed)
    df[z] = df.apply(lambda x: z60617 if x[add1] == con_fixed else x[z], axis=1)

    # Fix La Rabida's address
    rab = 'EAST 65TH STREET AT LAKE MICHIGAN'
    rab_fixed = '6501 S PROMONTORY DRIVE'
    df[add1] = df[add1].replace(rab,rab_fixed)

    if nm in df.columns:
        # Fix the Habilitative Systems address, city, state, & zip
        habs = 'HABILITATIVE SYSTEMS'
        habs_add1 = '1018 NORTH MENARD'
        habs_add1_fixed = '1018 N MENARD AVENUE'
        z60651 = 60651
        df[add1] = df.apply(lambda x: habs_add1_fixed if (x[nm] == habs and x[add1] == habs_add1) else x[add1], axis=1)
        df[ct] = df.apply(lambda x: chicago if x[add1] == habs_add1_fixed else x[ct], axis=1)
        df[st] = df.apply(lambda x: il if x[add1] == habs_add1_fixed else x[st], axis=1)
        df[z] = df.apply(lambda x: z60651 if x[add1] == habs_add1_fixed else x[z], axis=1)

        # Fix the Chicago Horticultural Society info
        chs = 'CHICAGO HORTICULTURAL SOCIETY'
        chs_add1 = '2600 WEST 26TH PLACE'
        chs_add1_fixed = '1000 LAKE COOK ROAD'
        chs_ct_fixed = 'GLENCOE'
        df[add1] = df.apply(lambda x: chs_add1_fixed if (x[add1] == chs_add1 and x[nm] == chs) else x[add1], axis=1)
        df[ct] = df.apply(lambda x: chs_ct_fixed if (x[nm] == chs and x[add1] == chs_add1_fixed) else x[ct], axis=1)

        # Fix the Center of Higher Development information
        chd = 'CENTER OF HIGHER DEVELOPMENT'
        chd_add1 = '3515 SOUTH BURLEY AVENUE'
        chd_add1_fixed = '3515 S COTTAGE GROVE AVENUE'
        z60637 = 60637
        df[add1] = df.apply(lambda x: chd_add1_fixed if (x[add1] == chd_add1 and x[nm] == chd) else x[add1], axis=1)
        df[z] = df.apply(lambda x: z60637 if (x[nm] == chd and x[add1] == chd_add1_fixed) else x[z], axis=1)

        # Fix the Aunt Martha's information
        aunt = 'AUNT MARTHAS YOUTH SERVICES CENTER'
        aunt_add1 = '409 WEST JEFFERSON AVENUE'
        aunt_add1_fixed = '409 W JEFFERSON STREET'
        z60435 = 60435
        df[add1] = df.apply(lambda x: aunt_add1_fixed if (x[add1] == aunt_add1 and x[nm] == aunt) else x[add1], axis=1)
        df[z] = df.apply(lambda x: z60435 if (x[nm] == aunt and x[add1] == aunt_add1_fixed) else x[z], axis=1)

        # Fix the Children's Home & Aid Society of Illinois info
        chasi = 'CHILDRENS HOME AID SOCIETY OF ILLINOIS'
        chasi_add1 = '6201 SOUTH STEWARD AVENUE'
        chasi_add1_fixed = '125 S WACKER DRIVE'
        z60606 = 60606
        df[add1] = df.apply(lambda x: chasi_add1_fixed if (x[add1] == chasi_add1 and x[nm] == chasi) else x[add1], axis=1)
        df[z] = df.apply(lambda x: z60606 if (x[nm] == chasi and x[add1] == chasi_add1_fixed) else x[z], axis=1)

    return df

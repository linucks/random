#!/Users/jmht/miniconda2/envs/py36/bin/python
import os,sys
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import numpy as np
import savReaderWriter as spss
from collections import defaultdict

"""
To fire up python3 environment: source activate py36


https://bitbucket.org/fomcl/savreaderwriter
http://pythonhosted.org/savReaderWriter/

Edited /Users/jmht/miniconda2/envs/py36/lib/python3.6/site-packages/savReaderWriter/savWriter.py
And changed line 422 to allow mixed datatypes:

elif pandasOK and isinstance(records, pd.DataFrame):
    #jmht
    #records[records.isnull()] = self.sysmis
    records = records.where(records.notnull(), other=self.sysmis)


Each survey has its own ID (F0002)
Liam has given each person a unique ID and if they submit multiple samples, then they get a .1, .2 appended
Guy suggested: each “person” an ID value ({yyyy}-{dd}-{event code}-{incremented number} or something similar) 
Fiona wants to code each event with a number (e.g. 1 = SGP, 2 = KC)


Once Liam has finished coding all the paper intervention sheets, we want to:

    *Import the test data for each service user who now has an SPSS data file for their intervention;
    *We also want to import the second and third samples’ test data for those who have 1 intervention 
    but submitted multiple samples for testing. Guy and Liam worked out a way to already indicate
    those by ID/sample numbers;
    *Also there is the issue of the Boomtown interventions that were only recorded electronically and 
    how we import them from Google Forms to SPSS retaining all their intervention data and tweaking it to 
    the SPSS requirements (eg. Dealing with missing data etc);


"""

def writeSav(df, fname):
    varNames = df.columns
    varTypes = {}
    for c in df.columns:
        #print("DATA TYPE ",df[c].dtype)
        if is_string_dtype(df[c]):
            # Currently falls over if null/float values as tries to get len so just use 1 for now
            #df[c].fillna(b'',inplace=True)
            df[c].fillna('',inplace=True)
            # Also need to change eveyrthing to bytes
            #df[c] = df[c].apply(lambda elt: str(int(elt)).encode() if isinstance(elt, float) else str(elt).encode())
            df[c] = df[c].apply(lambda elt: str(elt).encode() if isinstance(elt, float) else str(elt).encode())
            d = df[c].map(len).max()
            #d = 1
        elif is_numeric_dtype(df[c]):
            d = 0
        varTypes[c] = d
    with spss.SavWriter(fname, varNames, varTypes, ioUtf8=False) as writer:
         writer.writerows(df)

def readSav(fname):
    with spss.SavReader(fname) as reader:
        header = reader.header
        records = reader.all()
    df = pd.DataFrame(records,columns=header)
    # Decode the encoded data
    df.rename(columns=lambda x: x.decode("utf-8"), inplace=True)
    df.rename(columns=lambda x: x.translate(str.maketrans(' /()?','_____')), inplace=True)
    for c in df.columns:
        if is_string_dtype(df[c]): df[c] = df[c].str.decode("utf-8")
    return df

def FixIntervention(df):
    """Fix sample number and add Event column"""
    def f(sn):
        if not np.isnan(sn):
            sn = 'F{:04d}'.format(int(sn))
        return sn
    # Delete any columns where SampleNumber is NA as we can't do anything with it
    df['SampleNumber'].dropna(inplace=True)
    df['Sample_Number'] = df['SampleNumber'].apply(f)
    df.drop('SampleNumber',axis=1)

    festival_codes = { 'BoomTown' : ('BT2017',4),
                       'KC' : ('KC2017',1),
                       'SGP' : ('SGP2017',2)
                       }
    festival_codes = { 4 : ('BT2017',4),
                       1 : ('KC2017',1),
                       2 : ('SGP2017',2)
                       }
    # Delete any columns where Festival is nan
    df['Festival'].dropna(inplace=True)
    #df.where("Festival" != np.nan, inplace=True)
    def f(x):
        #if x in ['2017-08-11', '2017-08-11 00:00:00' ]: x = 'BT2017'
        return festival_codes[x][0]
    df['Event_Name'] = df['Festival'].apply(f)
    #del df['Festival']
    df.drop('Festival',axis=1)
    
    labels = ['SubmittedSubstanceAs']
    df.loc[:, labels] = df[labels].apply(lambda x: x.str.upper())
    return

def condition_data(df):
    labels = ['Bought_as', 'Client_suspicion', 'Service_User_Pill_Logo', 'Tester_Logo_Suggestion',
              'Colour', 'FTIR_main_result']
    df.loc[:, labels] = df[labels].apply(lambda x: x.str.upper())
    #return  df[labels].apply(lambda x: x.str.upper())
#     return  df[labels].apply(lambda x: x.str.upper())
    #df[labels].str.upper()
#     labels = ['Tester_Logo_Suggestion']
#     for l in labels:
#         fix = defaultdict(set) # Dict of key to possible variations
#         #print(df[l].dtype)
#         #df[c] = df[c].astype(int)
#         all = list(set(df[l].values))
#         print("ALL ",sorted([str(a) for a in all]))
#         #Check if are same when capitalised
#         for i in range(len(all)):
#             for j in range(len(all)):
#                 if j <= i: continue
#                 if str(all[i]).lower() == str(all[j]).lower():
#                     fix[str(all[i].lower())].update([str(all[i]),str(all[j])])
#                     
#         print("MATCH FOR ",fix)
    

fn_testing = '2017 The Loop - collated sample data.xlsx'
df1 = pd.read_excel(fn_testing ,sheetname='Collated Data', converters={'Sample submission time': str})
df1.rename(columns=lambda x: x.translate(str.maketrans(' /()?','_____')), inplace=True)
condition_data(df1)

fn_intervention = 'The_Loop_2017_Final_Interventions_labels.xlsx'  
fn_intervention = 'The_Loop_2017_Final_Interventions.xlsx'  
df2 = pd.read_excel(fn_intervention, converters={'Date': str, 'Time' : str})
FixIntervention(df2)

dft = pd.merge(df1, df2, how='inner', on=['Event_Name','Sample_Number'])

writer = pd.ExcelWriter('merged.xlsx')
dft.to_excel(writer,'MergedData',index=False)
writer.save()

sys.exit()

if False:
    # Attempt to convert to numeric datatype but even if onvert to numpy int still gets converted to float
    df2 = pd.read_csv('variable_definitions.csv')
    c2t = {}
    NANI = -999
    for c in df.columns:
        cd = df2[df2['Name'] == c]
        ctype = cd.Type.values[0]
        d = cd.Decimals.values[0]
        if ctype == 'Numeric' and d == 0:
            c2t[c] = int
            df[c].fillna(NANI,inplace=True)
            df[c] = df[c].astype(int)
            # Can't convert back as numpy can't stor NAN's in int arrays
            #df[c] = df[c].replace(NANI,np.nan)
    # Batch Mode
    #df.astype(c2t,copy=False)


# fname = '2017 The Loop Collated pill data.xlsx'
# df = pd.read_excel(fname,sheetname=0, converters={'Date catalogued': str})
# df.rename(columns=lambda x: x.translate(str.maketrans(' /()','____')), inplace=True)
# 
# fname = '2017_The_Loop_Collated_pil_data.sav'
# # Write as sav file
# writeSav(df, fname)
# # Read into dataframe
# df = readSav(fname)
# 
# # Write out again
# df.to_csv('foo.csv')
# writer = pd.ExcelWriter('foo.xlsx')
# df.to_excel(writer,'Sheet1')
# writer.save()
# sys.exit()
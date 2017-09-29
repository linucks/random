#!/Users/jmht/miniconda2/envs/py36/bin/python
import os,sys
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import numpy as np
import savReaderWriter as spss

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
    for c in df.columns:
        if is_string_dtype(df[c]):
            df[c] = df[c].str.decode("utf-8")
    
    return df


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


fname = 'The Loop_662.sav'

df = readSav(fname)
print(df)
writeSav(df,'The Loop_662_2.sav')
df = readSav(fname)
print(df)
df.to_csv('foo.csv')

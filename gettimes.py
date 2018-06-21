#!/usr/bin/env ccp4-python

import os
import sys
import numpy as np
import pandas as pd

def parse_serial_modelling(mdir):
    df = None
    for i in range(1000):
        fsc = os.path.join(mdir, 'job_{}'.format(i), 'score.fsc')
        if df is None:
            df = pd.read_csv(fsc, sep='\s+')
        else:
            df = df.append(pd.read_csv(fsc, sep='\s+'))
    return df

dfa =  None
for pdb in ["1GU8", "2BHW", "2BL2", "2EVU", "2O9G", "2UUI", "2WIE", "2X2V", "2XOV", "3GD8", "3HAP", "3LDC", "3OUF", "3PCV", "3RLB", "3U2F", "4DVE"]:
    if pdb == '4DVE':
        mdir = os.path.join(pdb, 'AMPLE.0/modelling')
    else:
        mdir = os.path.join(pdb, 'AMPLE_0/modelling')
    df = parse_serial_modelling(mdir)
    df['pdb'] = pdb
    if dfa is None:
        dfa = df
    else:
        dfa = dfa.append(df)

dfa.to_csv('tm.csv')


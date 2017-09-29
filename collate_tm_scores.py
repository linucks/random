#!/usr/bin/env ccp4-python

from collections import OrderedDict
import os
import sys
import pandas as pd


root = '/media/scratch/TM/'

master_df = []
rtypes = ['rosettaMembrane', 'quark', 'gremlin', 'ccmpred', 'membrain', 'metapsicov' ]
for rtype in rtypes:
    print "DIR ",rtype
    df_spicker_list = []
    for pdb in ['1GU8', '2BHW', '2EVU', '2O9G', '2WIE', '2XOV', '3GD8', '3HAP', '3LDC', '3OUF', '3PCV', '3RLB', '3U2F', '4DVE']:
        if rtype == 'rosettaMembrane':
            cfile = os.path.join(root,'tm',pdb,"AMPLE_0/ensemble_workdir/spicker/spicker_cluster_1.list")
            tmfile = "/home/jmht/Dropbox/PHD/TM_paper/rosettaMembrane_tmscores.csv"
        elif rtype == 'quark':
            cfile = os.path.join('/home/jmht/Dropbox/PHD/TM_paper/quark',pdb,"AMPLE_0/ensemble_workdir/spicker/spicker_cluster_1.list")
            tmfile = "/home/jmht/Dropbox/PHD/TM_paper/quark_tmscores.csv"
        elif rtype == 'gremlin':
            cfile = os.path.join(root,'tm_gremlin_cut0',pdb,"AMPLE_1/ensemble_workdir/spicker/spicker_cluster_1.list")
            tmfile = "/home/jmht/Dropbox/PHD/TM_paper/tm_gremlin0.0_shelxe14_tmscores.csv"
        elif rtype == 'ccmpred':
            cfile = os.path.join(root,'contacts',pdb.lower()+'_ccmpred_fade1.0_weight1.0_dtn5',"AMPLE_0/ensemble_workdir/spicker/spicker_cluster_1.list")
            tmfile = "/home/jmht/Dropbox/PHD/TM_paper/ccmpred_fade1.0_weight1.0_dtn5_tmscores.csv"
        elif rtype == 'membrain':
            cfile = os.path.join(root,'contacts',pdb.lower()+'_membrain_fade1.0_weight1.0_dtn5',"AMPLE_0/ensemble_workdir/spicker/spicker_cluster_1.list")
            tmfile = "/home/jmht/Dropbox/PHD/TM_paper/membrain_fade1.0_weight1.0_dtn5_tmscores.csv"
        elif rtype == 'metapsicov':
            cfile = os.path.join(root,'contacts',pdb.lower()+'_metapsicov.stage1_fade1.0_weight1.0_dtn5',"AMPLE_0/ensemble_workdir/spicker/spicker_cluster_1.list")
            tmfile = "/home/jmht/Dropbox/PHD/TM_paper/metapsicov.stage1_fade1.0_weight1.0_dtn5_tmscores.csv"
        
        
        with open(cfile) as f: models = [os.path.splitext(os.path.basename(m.strip()))[0] for m in f]
        # Create dataframe with models as 'Model' column and PDB as PDB and then merge to get the list
        
        df_spicker_list.append(pd.DataFrame({'Model' : models, 'PDB': pdb}))
    
    # Collect individual PDB data into a single dataframe
    df_spicker = pd.concat(df_spicker_list)
    
    if rtype in ['quark','gremlin']:
        df_tm = pd.read_csv(tmfile, usecols=['structure_name','model_name','tmscore'])
        # Rename the columns we need to match
        df_tm.rename(columns={'structure_name':'PDB', 'model_name' : 'Model', 'tmscore' : 'TM'}, inplace=True)
    elif rtype in ['ccmpred', 'membrain', 'metapsicov']:
        df_tm = pd.read_csv(tmfile, usecols=['native_pdb_code','tmscore','subcluster_centroid_model'])
        # Rename the columns we need to match
        df_tm.rename(columns={'native_pdb_code':'PDB', 'subcluster_centroid_model' : 'Model', 'tmscore' : 'TM'}, inplace=True)
    else:
        df_tm = pd.read_csv(tmfile, usecols=['PDB','Model','TM'])
    
    # Merge in the TM score data
    dft = pd.merge(df_spicker, df_tm, how='inner', on=['PDB', 'Model'])
    
    # Now groupby to get the median
    df = dft.groupby(['PDB']).median().reset_index()
    print "ADDDING ",df
    master_df.append(df)
    
# Could use a multi-index to have all in two columns (pdb, TM), but have the index take care of rtype
master_df = pd.concat(master_df, keys=rtypes)
master_df.to_csv('allruns_tm.csv')
    



#!/usr/bin/env ccp4-python

import cPickle
import csv
import os
import re
import sys
import pandas as pd
from collections import Counter, defaultdict
from ample.util.sequence_util import Sequence

class MutationSummary(object):
    """Hold information on the mutations for a set of Rosetta PDBS"""

    def __init__(self, sites, directory):
        self.sites = sites

        self.configs = None
        self.max_config = None
        self.max_config_pdb = None
        if not os.path.isdir(directory):
            raise RuntimeError("Cannot find directory %s" % directory)
        self.directory = directory

        scorefile = os.path.join(directory, 'scorefile.tsv')
        if not os.path.isfile(scorefile):
            raise RuntimeError("Cannot find scorefile %s" % scorefile)

        # Add list of mutations
        self.df = pd.read_table(scorefile, sep='\s*', engine='python')

        # Sort by energy
        self.df.sort_values('total_score', inplace=True, ascending=False)

        self._get_mutations()
        # with open('foo.pkl', 'w') as w:
        #     cPickle.dump(self, w)
        self._set_max_config()

    def _get_mutations(self):
        self.df['pdb'] = None
        self.df['mutations'] = None
        self.df['mutations_key'] = None
        self.df['mutations'].astype(object, inplace=True)
        for i, pdbn in enumerate(self.df['description']):
            pdbn = pdbn + '.pdb'
            pdb = os.path.join(self.directory, pdbn)
            self.df.iat[i, self.df.columns.get_loc('pdb')] = pdbn
            seq = Sequence(pdb=pdb).sequences[0]
            muts = [seq[si-1] for si in sites]
            self.df.iat[i, self.df.columns.get_loc('mutations')] = muts
            self.df.iat[i, self.df.columns.get_loc('mutations_key')] = "".join(muts)

    def _set_max_config(self):
        configs = set(self.df['mutations_key'])
        config_dict = dict.fromkeys(configs)
        for c in configs:
            config_dict[c] = sum(self.df['mutations_key'] == c)
        self.configs = Counter(config_dict)
        self.max_config = self.configs.most_common(1)[0][0]
        # Pick first in list as df is sorted by total_score
        self.max_config_pdb = self.df['pdb'][self.df['mutations_key'] == self.max_config].iloc[0]

    def mutations_by_site(self):
        """Return list of string representation of the mutations at each site"""
        mutations = self.df['mutations'].values.tolist()
        by_site = []
        for i, site in enumerate(self.sites):
            c = Counter([m[i] for m in mutations])
            #print "Pos ", site, ": ", c
            by_site.append(str(c).lstrip(',Counter({').rstrip('})').translate(None, "'"))
        return by_site

    def max_config_by_site(self):
        return list(self.max_config)

    def top10_pdbs(self):
        return list(self.df.iloc[0:10, self.df.columns.get_loc('pdb')].values)

def write_csv(ddict):
    df = pd.DataFrame()
    df['sites'] = sites
    for runt in runtypes:
        df[runt] = ddict[runt].mutations_by_site()
        df[runt+'_maxconfig'] = ddict[runt].max_config_by_site()
    df.to_csv('mutations.csv', index=False)

def mklinks(ddict):
    def shrink_name(name):
        return re.sub('sax_softwts', 'm', name)
    cdir = 'compare'
    owd = os.getcwd()
    os.chdir(cdir)
    for runtype in ddict.keys():
        name = shrink_name(runtype)
        mutsum = ddict[runtype]
        rdir = os.path.join("..", mutsum.directory)
        for i, pdb in enumerate(mutsum.top10_pdbs()):
            pdb_path = os.path.join(rdir, pdb)
            lname = "{}_{}.pdb".format(name, i+1)
            os.symlink(pdb_path, lname)
        # Add symlink to max_config with lowest energy
        lname = "{}_maxc.pdb".format(name)
        maxpdb = os.path.join(rdir, mutsum.max_config_pdb)
        os.symlink(maxpdb, lname)
    #os.chdir(owd)
    return

if __name__ == '__main__':
    runtypes = ['sax_softwts', 'sax_softwts_fvrnat', 'sax_softwts_fvrnat2.0', 'sax_softwts_fvrnat5.0']
    #runtypes = ['sax_softwts_fvrnat']
    ddict = {}
    sites = [10, 22, 25, 145, 146, 147, 148, 149, 150, 151, 210, 225, 226, 253, 255, 307, 308, 310, 311, 312, 347]
    for runtype in runtypes:
        print("Runtype: %s" % runtype)
        ms = MutationSummary(directory=runtype, sites=sites)
        print("Max config for {0}  is {1} with pdb: {2}".format(runtype, ms.max_config, ms.max_config_pdb))
        #ms.df.to_csv('foo.csv')
        ddict[runtype] = ms

    mklinks(ddict)
    write_csv(ddict)

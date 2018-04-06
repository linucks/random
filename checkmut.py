#!/usr/bin/env ccp4-python

import csv
import os
import sys
import pandas as pd
from collections import Counter, defaultdict
from ample.util.sequence_util import Sequence

import cPickle


"""
List of runtypes
List of mutable residues

Runtype is top structures
next is residue

Get residue counts across a list of structures
Get residue counts for 10 lowest energy structures
Get the maximum configuration and the lowest energy structure with that configuration
Create a csv file with all data

ddict = {}
sites = [10, 22, 25, 145, 146, 147, 148, 149, 150, 151, 210, 225, 226, 253, 255, 307, 308, 310, 311, 312, 347]
for runtype in runtypes:
    ms = MutSummary(directory=runtype, sites = sites)
    print("Max config for {0}  is {1} with pdb: {2}".format(runtype, ms.max_config, ms.max_config_pdb)
    ddict[runtype] = ms

df = Dataframe()
df['sites'] = sites
for runt in runtypes:
    df[runt] = ddict[runt].mutations_by_site()
    df[runt+'max_config'].max_config_by_site()
df.to_csv()
"""


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

if __name__ == '__main__':
    runtypes = ['sax_softwts', 'sax_softwts_fvrnat']
    #runtypes = ['sax_softwts_fvrnat']
    ddict = {}
    sites = [10, 22, 25, 145, 146, 147, 148, 149, 150, 151, 210, 225, 226, 253, 255, 307, 308, 310, 311, 312, 347]
    for runtype in runtypes:
        ms = MutationSummary(directory=runtype, sites=sites)
        print "CONFIGS ", ms.configs
        print("Max config for {0}  is {1} with pdb: {2}".format(runtype, ms.max_config, ms.max_config_pdb))
        ddict[runtype] = ms

    df = pd.DataFrame()
    df['sites'] = sites
    for runt in runtypes:
        df[runt] = ddict[runt].mutations_by_site()
        df[runt+'_maxconfig'] = ddict[runt].max_config_by_site()
    df.to_csv('mutations.csv', index=False)

    sys.exit()



    # def max_config(mut_config):
    #     for runt in sorted(mut_config.keys()):
    #         print "MAX CONFIGURATION FOR ", runt
    #         mutmax = [0, None]
    #         for k, pdbs in mut_config[runt].items():
    #             lmut = len(pdbs)
    #             if lmut > mutmax[0]:
    #                 mutmax = [lmut, pdbs]
    #         print "MAX IS ", k, mutmax
    #
    #
    # # runtypes = [ 'sax_zubieta', 'sax_zubieta_repack', 'sax_jens', 'sax_jens_repack', 'sax_auto' ]
    # # runtypes = [ 'favour_natural_0.8', 'favour_natural_2.0', 'favour_natural_10.0' ]
    # runtypes = ['sax_softwts', 'sax_softwts_fvrnat']
    #
    # # for x in `cat resfile.* | grep ALLAA | cut -d " " -f 1 | sort -u | xargs`; do echo $x,; done | xargs
    # sites = [10, 22, 25, 145, 146, 147, 148, 149, 150, 151, 210, 225, 226, 253, 255, 307, 308, 310, 311, 312, 347]
    # results = [[str(s) for s in sites]]
    #
    # mut_config = {}
    # for runt in runtypes:
    #     mut_config[runt] = defaultdict(list)
    #     if False:
    #         with open(os.path.join(runt, 'top.10')) as f:
    #             pdbs = [os.path.join(runt, line.strip()) for line in f]
    #     else:
    #         pdbs = [os.path.join(runt, f) for f in os.listdir(runt) if f.endswith('pdb')]
    #     seqs = [Sequence(pdb=p).sequences[0] for p in pdbs]
    #     print "Checking ", runt
    # #     for si in sites:
    # #         c2 = [s[si-1] for s in seqs]
    # #         print "SITES ", c2
    #     muts = []
    #     for i, s in enumerate(seqs):
    #         x = [s[si-1] for si in sites]
    #         # print "SITES ",x
    #         muts.append(x)
    #         k = "".join(x)
    #         mut_config[runt][k].append(pdbs[i])
    #     results.append([])
    #     for i, si in enumerate(sites):
    #         c = Counter([m[i] for m in muts])
    #         print "Pos ", si, ": ", c
    #         results[-1].append(str(c).lstrip(',Counter({').rstrip('})').translate(None, "'"))
    #
    #
    # max_config(mut_config)
    #
    # results = map(list, zip(*results))
    # with open('mutations.csv', 'w') as w:
    #     cw = csv.writer(w)
    #     cw.writerow(['sites']+runtypes)
    #     for r in results:
    #         cw.writerow(r)

from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import common 
import time 

from frm.anygeom import AnyGeom
import frm.mapoverlay as fmo
import frm.plots as fplots 
import frm.support 


npmap = frm.support.npmap 



"""
1. Is the total population of my blocks and tracts about right?
    YES. 122*7 = 854k total pop.
        cb 854.5
        ct 854.5
        
2. Do I count every resident in my tesselation?
    No. Sum over tracts is 822k I'm dropping people
        Sum over blocks is 852, dropping far fewer
        
        
District: Council   BlockLevel   Tract Level
1       122.4       122.0   -0.4`   121.8
2       118.3       118.1   -0.2    116.1
3       124.5       110.9   -14     111.3
4       119.5       119.1   -0.4    119.7
5       116.2       127.2   + 7     117.1
6       128.3       124.4   - 4     125.5
7       127.4       130.4   + 3     110.5
        -----       -----           -----
        856.6       852.2           822.2


overb.sum(axis=0)
Should be equal to 1 for every census block. I'm seeing a whole bunch marked as zero


There's some kind of bug in overlap. Possily related to those error messages
Doesn't seem related to D3 though


It's not a problem with overlap.
cb[overlap[2] > .1].TotalPop.sum() == 110.9

Must be a problem with mapping of geomtrise to populations?
"""

#df comes from main.main()

def main(df, overlap=None):
    cb = common.load_census_blocks()
    
    if overlap is None:
        overlap = common.compute_frac_overlaps(df.geom.values, cb.geom.values)

    #Assign blocks that straddle my boundaries
    idx = overlap[2,:]  > .5  #Blocks in district 3
    
    idebug()
    out = cb.name.iloc[idx].copy().to_frame('fips')
    out['TotalPop'] = cb.TotalPop.iloc[idx].values
    out['district'] = 3
    out.to_csv('councilmap/computed_blocks_for_district3.csv')
    frm.meta.save_metadata('councilmap/computed_blocks_for_district3.csv.json')
    
    return out


def plot1(df, overb):
    cb = common.load_census_blocks()

    sm = overb.sum(axis=0)
    idx = sm > 1.1
    overcount = cb[idx]
    idx = (sm < .99) & (cb.TotalPop > 0)
    undercount = cb[idx]
    
    plt.figure(1)
    plt.clf()
    #common.plat_shape(overcount.geom.values, labels=overcount.name.values, color='r')
    #common.plat_shape(overcount.geom.values, color='r', lw=4)

    labels = undercount.astype(str).name.str[5:].values
    common.plat_shape(undercount.geom.values, labels=labels,  lw=2)
    common.plat_shape(df.geom.values, color='k')

    return undercount

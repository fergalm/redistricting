
from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import common 
import time 

import frm.plots as fplots

"""
Create a list of block groups and assign them to
districts based on the 2014 maps
"""

def main():
    districts = common.load_district_lines('v2010')
    
    cb = common.load_census_blocks()

    fplots.plot_shape(districts.geom.iloc[0], 'r-')
    plt.pause(.1)
    print("There are %i blocks" %(len(cb)))
    
    overlaps = common.compute_frac_overlaps(
        districts.geom.values, 
        cb.geom.values,
    )
    
    #Filter out cbs with no overlap at ll
    #idebug()
    out = pd.DataFrame()
    fips = cb.name.astype(str)
    out['block'] = fips
    out['tract'] = fips.str[6:11]
    out['group'] = fips.str[6:12]
    out['district'] = np.argmax(overlaps, axis=0) + 1
    out['geom'] = cb.geom.values 
    
    out.to_csv('tully3/blocks_to_districts.csv')
    return out 


import frm.support 
def check(out, districts):
    
    plt.clf()
    
    for g in districts.geom:
        fplots.plot_shape(g, 'k-')
        
    for i in range(1, 8):
        idx = out.district == i
        df  = out[idx] 
        #idebug()
    
        geom = frm.support.union_collection(df.geom.values )
        fplots.plot_shape(geom, 'r-')
        plt.pause(.1)

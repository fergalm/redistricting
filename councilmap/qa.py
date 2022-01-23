
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

import osgeo.gdal as gdal
gdal.UseExceptions()


def main(axl=None):
    cb = common.load_census_blocks()
    df = pd.read_csv('councilmap/block_to_pct_dist_draft2.csv')
    df = pd.merge(df, cb, on='name')

    print(df.groupby('District').TotalPop.sum())

    def union(row):
        return frm.support.union_collection(row.values)
    
    with frm.support.Timer("union"):
        df = df.groupby('District').geom.apply(union).to_frame('geom')
    plt.clf()

    if axl is not None:
        plt.axis(axl)
        common.plat_shape(  cb.geom, cb.name, color='grey', fontdict=dict(fontsize=10))
    common.plat_shape(df.geom, df.index, color='r')
    
    
    #plt.clf()
    #cm = plt.cm.rainbow
    #cm.set_under('#00FF0000')
    #fplots.chloropleth(df.geom, df.TotalPop, vmin=20, cmap=cm)
    #plt.axis([-76.92599135, -76.25729365, 39.12838905, 39.74953595])
    ##idx = df.Precinct == '01-001'
    
    #plt.clf()
    #plot_precinct(df, cb, pct, '01-001')
    #plot_precinct(df, cb, pct, '11-014')
    #plot_precinct(df, cb, pct, '15-026')
    #plot_precinct(df, cb, pct, '11-015')
    #return 

    #offset = 220
    #for i, name in enumerate(sorted(list(set(pct.name)))[offset:]):
        #plot_precinct(df, cb, pct, name)
        #print(offset+i)
        #plt.pause(1)
        ##return 

    
    #for name in set(df.Precinct):
def plot_precinct(df, cb, pct, name):
    
    fd = dict(fontsize=8)
    idx = df.Precinct == name
    df2 = df[idx] 
    
    #plt.clf()
    #if len(df2) > 0:
        #fplots.chloropleth(df2.geom.values, np.arange(len(df2)))
        
    labels = df2.name.astype(str).str[5:]
    #labels=None
    common.plat_shape(df2.geom.values, labels=labels, color='r', lw=0.5, fontdict=fd)

    #axl = plt.axis()
    #common.plat_shape(pct.geom, labels=pct.name, color='b', fontdict=dict(color='b'))
    #plt.axis(axl)
    
    fplots.plot_shape(pct[pct.name == name].geom.values[0], 'b-', lw=3)
    fmo.drawMap()
    plt.title(name)
    
    #key = cb.name.astype(str).str[5:9]
    #idx = key == '4518'
    #cb = cb[idx]
    #common.plat_shape(cb.geom, labels=cb.name, color='r', lw=1, fontdict=fd) 



def make_cb_mapping():
    cb = common.load_census_blocks()
    pct = common.load_vote_data_by_precinct()
    districts = pd.read_csv('councilmap/council_map.csv')
    districts['geom'] = npmap(lambda x: AnyGeom(x).as_geometry(), districts.geom)


    with frm.support.Timer("District mapping"):
        dis_overlap = common.compute_frac_overlaps(districts.geom.values, cb.geom.values)

    with frm.support.Timer("Precinct mapping"):
        pct_overlap = common.compute_frac_overlaps(pct.geom.values, cb.geom.values)

    cb = foo(pct_overlap, dis_overlap)
    return pct_overlap, dis_overlap 

def foo(pct_overlap, dis_overlap):  
    """inputs created by make_Cb_mapping()"""
    cb = common.load_census_blocks()
    pct = common.load_vote_data_by_precinct()
    districts = pd.read_csv('councilmap/council_map.csv')

    #Filter out zero population blocks
    #idx = cb.TotalPop > 0
    #cb = cb[idx]
    #pct_overlap = pct_overlap[:, idx]
    #dis_overlap = dis_overlap[:, idx]
    
    #idebug()
    assignment = pct_overlap.argmax(axis=0)
    pct_name = pct.name.iloc[assignment].values
    cb['Precinct'] = pct_name 

    assignment = dis_overlap.argmax(axis=0)
    dis_name = districts.district.iloc[assignment].values
    cb['District'] = dis_name 

    cols = ['District', 'Precinct', 'name']
    cb = cb[cols]
    cb.to_csv('councilmap/block_to_pct_dist_draft.csv')
    frm.meta.save_metadata('councilmap/block_to_pct_dist_draft.csv.json')
            
    return cb 

    idx = assignment == 0
    for g in cb[idx].geom:
        fplots.plot_shape(g)
        
    common.plat_shape(districts.geom, color='grey')
    return pct_overlap

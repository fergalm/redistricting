
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

def main(highlight=None):
    cb = common.load_census_blocks()
    #This is my proposed map for Ryan
    #df = pd.read_csv('councilmap/block_to_pct_dist_fergal.csv')
    
    #This is my recreation of the council map, I think
    #df = pd.read_csv('councilmap/block_to_pct_dist_council.csv')
    
    df = pd.read_csv('councilmap/block_to_pct_dist_legislation.csv')
    
    df = pd.merge(df, cb, on='name')
    ct = common.load_census_tracts()
    
    
    rep = report(df)
    print(rep)

    axl = plt.axis()
    plt.clf()
    #fplots.chloropleth(ct.geom, ct.TotalBlack, cmap=plt.cm.bone_r)
    
    pct = common.load_vote_data_by_precinct()
    labels = pct.name
    #labels = None
    common.plat_shape(pct.geom, labels, color='b', lw=1, fontdict=dict(fontsize=8))

    if highlight is not None:
        idx = df.District == highlight
        df2 = df[idx]
        labels = df2.name.astype(str).str[5:]
        common.plat_shape(df2.geom, labels, color='r', lw=1,)     
    
    if axl[-1] > 1:
        plt.axis(axl)
 
    plt.pause(.01)
    #plat = make_and_plot_district_lines(df)
    
    #save(rep, plat)
    
    #return plat, rep
 
def make_and_plot_district_lines(df):
    def union(row):
        return frm.support.union_collection(row.values)
    
    with frm.support.Timer("union"):
        dist = df.groupby('District').geom.apply(union).to_frame('geom')
    common.plat_shape(dist.geom, dist.index, color='r', lw=4)
    return dist 
    
def report(df):
    cols = """
        District
        TotalPop
        TotalWhite
        TotalBlack
        VotingTotal
        VotingWhite
        VotingBlack
    """.split()

    df2 = df[cols]
    df3 = df2.groupby('District').sum()
    df3['PercentBlack'] = df3['TotalBlack'] / df3['TotalPop']
    return df3



def osm_plat(dist, fileroot):

    plt.ioff()
    axl = plt.axis()
    plt.clf()
    plt.gcf().set_size_inches((24,24))
    common.plat_shape(dist.geom, dist.index, color='r', lw=4)
    fmo.drawMap('osm')
    
    if axl[-1] > 1:
        plt.axis(axl)
    
    plt.savefig(fileroot + '.png')
    plt.ion()
    
    
def save(plat, rep):
    fn = 'fergal_map'
    frm.meta.save_metadata(fn+".json")
    plat.to_csv(fn + "_geom.csv")
    rep.to_csv(fn + "_report.csv")
    osm_plat(plat, fn)

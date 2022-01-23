from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
from frm.parmap import parmap
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots
import frm.norm as fnorm
from tqdm import tqdm
import time
import os

import frm.census

DOC = """
My implementation of the proposed commission map as described in the legistlation
in their report. 

Read the list of precincts and census blocks from precincts.xls
and convert into 7 shapefiles.

This was increibly tedious, but I think I have it right.

There's one block missing in census 1, but I couldn't find it
in the document. 
"""


def main():
    
    fn = "merged_blocks_df.csv"
    dfp = load_merged_precinct_shapes()
    if not os.path.exists(fn):
        dfb = load_merged_block_shapes()
        dfb.to_csv(fn)
    else:
        dfb = pd.read_csv(fn)
        
    clr = 'xrgbkcmr'
    
    plt.clf()
    plt.axis([-76.92, -76.30, 39.167, 39.75])
    plot_precincts(dfp, clr)
    plot_blocks(dfb, clr)
    fmo.drawMap()
    fplots.add_watermark()
    
    dfo = make_shape_files(dfp, dfb)
    dfo = buffer_df(dfo)

    frm.meta.save_metadata('proposed_districts.csv.json', comment=DOC)
    dfo.to_csv('proposed_districts.csv')

    shapefile = '/home/fergal/data/elections/shapefiles/precinct2014/BaCoPrecinct-wgs84.shp'
    pct_geom = fgeom.load_geoms_as_df(shapefile)
    for name, g in zip(pct_geom.NAME, pct_geom.geoms):
        fplots.plot_shape(g, 'k-', lw=1)
        cent = AnyGeom(g).as_geometry().Centroid()
        plt.text(cent.GetX(), cent.GetY(), name, color='grey')
    #for name, g in zip(dfb.CensusBlock, dfb.geoms):
        #cent = AnyGeom(g).as_geometry().Centroid()
        #plt.text(cent.GetX(), cent.GetY(), name, color='pink')

    return dfo
        
        
        
def load_merged_precinct_shapes():
    shapefile = '/home/fergal/data/elections/shapefiles/precinct2014/BaCoPrecinct-wgs84.shp'
    df = pd.read_excel("precincts.xls", "Precinct")
    count = df.groupby('Precinct').count()
    print(count[count.CouncilDistrict > 1])

    pct_geom = fgeom.load_geoms_as_df(shapefile)
    df = pd.merge(pct_geom, df, left_on='NAME', right_on='Precinct')
    return df 


def load_merged_block_shapes():
    df = pd.read_excel("precincts.xls", "Blocks")
    count = df.groupby('CensusBlock').count()
    print(count[count.CouncilDistrict > 1])


    df['CensusBlock'] = list(map(lambda x: "%15i" %(x), df.CensusBlock))
    cache = '/home/fergal/data/elections/shapefiles/tiger/'
    tq = frm.census.TigerQuery(cache)
    geoms = tq.query_block(2020, '24005')

    df = pd.merge(df, geoms, left_on='CensusBlock', right_index=True)
    return df 


def plot_precincts(df, clr):
    #for i in range(1, 8):
        #idx = df.CouncilDistrict == i
        #for wkt in df[idx].geoms:
            #fplots.plot_shape(wkt, '-', color=clr[i])
    
    norm = fnorm.DiscreteNorm(7, vmin=1, vmax=7)
    cmap = plt.cm.tab10
    fplots.chloropleth(df.geoms, df.CouncilDistrict, norm=norm, cmap=cmap)
    
    #return df
    
def plot_blocks(df, clr):
    norm = fnorm.DiscreteNorm(7, vmin=1, vmax=7)
    cmap = plt.cm.tab10
    fplots.chloropleth(df.geoms, df.CouncilDistrict, norm=norm, cmap=cmap)
    #for i in range(1, 8):
        #idx = df.District == i
        #for wkt in df[idx].geoms:
            #fplots.plot_shape(wkt, '-', color=clr[i])
    #return df
    
def make_shape_files(dfp, dfb):
    grp = dfp.groupby('CouncilDistrict')
    grb = dfb.groupby('CouncilDistrict')

    fargs = dict(grp=grp, grb=grb)
    districts = np.arange(1,8)
    geoms = parmap(_func, districts, fargs=fargs, engine='serial')
    #idebug()
    out = pd.DataFrame()
    out['district'] = districts
    out['geom'] = geoms
    return out

def _func(district, grp, grb):
    dfp = grp.get_group(district)
    listp = list(dfp.geoms.values)
    try:
        dfb = grb.get_group(district)
        listb = list(dfb.geoms.values)
    except KeyError:
        listb = []
    
    geom_list = listp + listb 
    geom_list = list(map(lambda x: AnyGeom(x).as_geometry(), geom_list))
    geom = combine(geom_list)
    return geom
        
        
def combine(geom_list):
    if len(geom_list) == 1:
        return geom_list[0]
    
    if len(geom_list) == 2:
        return geom_list[0].Union(geom_list[1])
        
    size = int(np.floor(len(geom_list)/2))
    geom1 = combine(geom_list[:size])
    geom2 = combine(geom_list[size:])
    return geom1.Union(geom2)


def buffer_df(df):
    
    df['geom'] = df.geom.apply(lambda x: x.Buffer(+1e-4).Buffer(-1e-4))
    return df

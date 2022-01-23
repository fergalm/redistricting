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
from frm.fitter.lsf import Lsf
import frm.census 

from tqdm import tqdm
import common
import time
import os

import frm.support
from frm.support import npmap


def load_census_blocks():
    cb = load_block_geoms()
    cb = cb.rename({'GEOID20.1':'name', 'geoms':'geom'}, axis=1)
    cb = cb["name geom".split()].copy()
    return cb

def main(cb):

    for i in range(1, 4):
        with frm.support.Timer("Map %i" %(i)):
            df =create_shape("mdcong/LRAC%i.csv" %(i), cb)
            df.to_csv('geoms%i.csv' %(i))
            plat_df(df)
            plt.title(i)
            plt.pause(.1)

    
def create_shape(fn, cb):
    df = pd.read_csv(fn)
    df = df.rename({'Block':'name', 'DistrictID:1':'district'}, axis=1)
    
    cols = "name geom".split()
    cb = cb[cols]
    
    df2 = pd.merge(df, cb, on='name').reset_index()
    
    def union(series):
        geoms = npmap(lambda x: AnyGeom(x).as_geometry(), series)
        return frm.support.union_collection(geoms)
    
    shps = df2.groupby('district').geom.apply(union)
    return shps

def plat_df(districts, tracts):
    plt.clf()
    fplots.chloropleth(districts.geom, np.arange(len(districts)), alpha=.2)
    
    for g in tracts.geoms:
        fplots.plot_shape(g, 'k-', lw=.5)
    #plt.axis([-79, -74.8, 37, 41])
    fmo.drawMap()
    
    
def load_block_geoms():
    fn = "md_block_geoms.csv"
    cache = '/home/fergal/data/elections/shapefiles/tiger'
    if not os.path.exists(fn):
        tq = frm.census.TigerQuery(cache)
        df = tq.query_block(2020, '24')  #All blocks in state
        df.to_csv(fn)
        
    df = pd.read_csv(fn, index_col=0)
    return df
    
    
def load_census_tracts():
    cache = '/home/fergal/data/elections/shapefiles/tiger'

    fn = "md_census_tract_geoms.csv"
    if not os.path.exists(fn):
        tq = frm.census.TigerQuery(cache)
        df = tq.query_tract(2020, '24')  #All blocks in state
        df.to_csv(fn)
        
    geoms = pd.read_csv(fn, index_col=0)


    fn = "md_census_tract_pop.csv"
    mapper = dict(
        P1_001N='TotalPop',
        P1_003N='TotalWhite',
        P1_004N='TotalBlack',
        P3_001N='VotingTotal',
        P3_003N='VotingWhite',
        P3_004N='VotingBlack',
    )
    if not os.path.exists(fn):
        cq = frm.census.CensusQuery()
        df = cq.query_tract(2020, 'dec', 'pl', '24', mapper.keys())
        df = df.rename(mapper, axis=1)
        df.to_csv(fn)
    pop = pd.read_csv(fn, index_col=0)
    
    df = pd.merge(pop, geoms, left_on='fips', right_on='GEOID.1')
    df['name'] = df.fips 
    df['tractid'] = df.NAME 
    
    cols = 'name tractid ' + " ".join(mapper.values())
    cols += " geoms"
    df = df[cols.split()]
    idebug()

    return df

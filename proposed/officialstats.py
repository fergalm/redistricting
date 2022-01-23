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
import frm.support
from tqdm import tqdm
import time
import os

import frm.census

Timer = frm.support.Timer 

"""
Now that I have the geometry of the districts, query for block block_level 
population data and assign the results to each district
"""

def main():

    with Timer("Load district geoms"):
        dist_geom = pd.read_csv("proposed/proposed_districts.csv")
        
    with Timer("Load stats"):
        stats = load_stats()
        
    with Timer("Load blocks geoms"):
        geoms = load_block_geoms()
    
    with Timer("Merge"):
        df = merge_block_data(stats, geoms)
        
    #with Timer("Assigning districts"):
        #df['district'] = assign_cb_to_districts(dist_geom, df)
    
    
    fn = "proposed/block_level_population.csv"
    frm.meta.save_metadata(fn + ".json")
    df.to_csv(fn)
    
    
def print_report():
    df = pd.read_csv("block_level_population.csv", index_col=0)
    
    cols = ['district', 'TotalPop', 'TotalWhite', 'TotalBlack', 'VotingTotal',
       'VotingWhite', 'VotingBlack']
    
    df = df[ cols].groupby('district').sum()
    print(df)
    return df


def load_stats():
    cq = frm.census.CensusQuery()
    
    mapper = dict(
        P1_001N='TotalPop',
        P1_003N='TotalWhite',
        P1_004N='TotalBlack',
        P3_001N='VotingTotal',
        P3_003N='VotingWhite',
        P3_004N='VotingBlack',
    )

    df = cq.query_block(2020, 'dec', 'pl', '24005', mapper.keys())
    df = df.rename(mapper, axis=1)
    return df

    
def load_block_geoms():
    cache = '/home/fergal/data/elections/shapefiles/tiger'
    tq = frm.census.TigerQuery(cache)
    df = tq.query_block(2020, '24005')
    df = df[ ["geoms", "GEOID20"] ]
    return df


def merge_block_data(stats, geom):
    idebug()
    return pd.merge(stats, geom, left_on="fips", right_index=True)
    
    
def assign_cb_to_districts(dist_df, pop_df):
    dis_geom = []
    for j in range(len(dist_df)):
        dis_wkt = dist_df.geom.iloc[j]
        dis_geom.append(AnyGeom(dis_wkt).as_geometry())


    district = np.zeros(len(pop_df))
    for i in tqdm(range(len(pop_df))):
        cb_wkt = pop_df.geoms.iloc[i]
        cb_geom = AnyGeom(cb_wkt).as_geometry()
        
        for j in range(len(dis_geom)):
            if overlap(cb_geom, dis_geom[j]) > .5:
                district[i] = j+1
                continue 
    return district                


def overlap(geomA, geomB):
    """Measures the fraction of geomA that is within geomB"""
    
    inter = geomA.Intersection(geomB)
    frac = inter.Area() / geomA.Area()
    return frac

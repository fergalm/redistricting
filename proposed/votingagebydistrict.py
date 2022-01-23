from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots
from tqdm import tqdm
import time

import frm.parmap as parmap

"""
Computes the population of each district, and the voting age population
of each district
"""

def load():
    dist_df = pd.read_csv("proposed_2020_wkt.csv")
    pop_df = pd.read_csv("census_pop_data_bg_2020.csv")
    
    return dist_df, pop_df
    
def main():
    dist_df, pop_df = load()
    
    plot(dist_df, pop_df)
    
    pop_df['district'] = assign_cb_to_districts(dist_df, pop_df)

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
                            

def count_pop(pop_df):
    gr = pop_df.groupby('district')
    print(gr[['TotalPop', 'TotalBlack', 'TotalWhite']].sum())
    print(gr[['VotingTotal', 'VotingBlack', 'VotingWhite']].sum())

            
def plot(dist_df, pop_df):    
    plt.clf()
    idx = pop_df.district == 0
    for g in pop_df[idx].geoms:
        fplots.plot_shape(g, 'k-', lw=.5)

    for g in dist_df.geom:
        fplots.plot_shape(g, 'r-')
    fmo.drawMap()

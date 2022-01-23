from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots

import frm.census
import common

"""
Zoom in plot on district 5 showing the kiss

Run this from the directory one above
import proposed.district5 as pd5
...


"""



def main():
    prop = pd.read_csv("proposed/proposed_districts.csv")
    tracts = common.load_census_tracts()

    plt.gcf().set_size_inches((12,10))
    plt.clf()
    #for g in tracts.geom:
        #fplots.plot_shape(g, 'k-')
        
    fplots.plot_shape(prop.iloc[4].geom, 'm', lw=8)

    fmo.drawMap('osm', zoom_delta=-1)
    plt.title("District 5 is not compact", fontsize=24)
    
    decorate()
    fplots.add_watermark()
    
def decorate():
    ax = plt.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])    
    

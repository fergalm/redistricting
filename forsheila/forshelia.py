from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots
import time


import frm.get_geom as fgg 

def newVOld():
    old = "/home/fergal/data/elections/shapefiles/councildistricts/districts.shp"

    old = fgg.load_geoms_as_df(old)
    
    plt.clf()
    plt.gcf().set_size_inches((10,8))
    for g in old.geoms:
        fplots.plot_shape(g, 'r-')
    fplots.plot_shape(g, 'r-', label="2010-2020 District Lines")

    #These are the lines before the last minute amendments
    fn = "councilmap/council_map.csv"
    new = pd.read_csv(fn)
    
    ax = plt.gca()
    i = 1
    for g in new.geom:
        patch = AnyGeom(g).as_patch(color= f"C{i}", alpha=.4)
        for p in patch:
            ax.add_patch(p)
        i+=1
        
    fmo.drawMap()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    fplots.add_watermark()
    plt.legend()
    plt.savefig('newVold.png')


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots

def main():
    fn = '/home/fergal/data/elections/shapefiles/schools/highschool/High_School_Districts.shp'
    schools = fgeom.load_geoms_as_dict(fn, 'NAME')
    towson = schools['Towson HS']

    fn = '/home/fergal/data/elections/shapefiles/councildistricts/districts.shp'
    council = fgeom.load_geoms_as_dict(fn, 'COUNCILMAN')
    
    plt.clf()
    plt.gcf().set_size_inches((15,12))
    fplots.plot_shape(towson, 'r-')
    axl = plt.axis()
    
    #District names are strings

    ax = plt.gca()
    clr = "x x C0 C1 x C2 C3 x".split()
    for district in "2 3 5 6".split():
        #fplots.plot_shape(council[district], '-')
        patch = AnyGeom(council[district]).as_patch(fc=clr[int(district)], alpha=.2, ec='w')
        ax.add_patch(patch[0])
        
    
    plt.text(-76.65, 39.39, "2", fontsize=32)
    plt.text(-76.614, 39.42, "3", fontsize=32)
    plt.text(-76.61, 39.39, "5", fontsize=32)
    plt.text(-76.588, 39.38, "6", fontsize=32)
    
    plt.plot(-76.600065, 39.390380, 'rs', ms=14)
    plt.axis(axl)
    fmo.drawMap(zoom_delta=-1)
    
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])

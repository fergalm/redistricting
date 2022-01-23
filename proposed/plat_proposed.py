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

from tqdm import tqdm
import common
import time
import os

from frm.support import npmap


def main():
    plt.clf()
    plt.subplot(121)
    plat_current()
    plt.title("Current Districts")


    plt.subplot(122)
    plat_proposed()
    plt.title("Proposed Districts")
 #plat_proposed()
 
    fplots.add_watermark()
 
 
    
    
def plat_current():
    df = common.load_district_lines('v2010').sort_values('name')
    for i in range(len(df)):
        wkt = df.geom.iloc[i]
        fplots.plot_shape(wkt, 'b-', lw=3)
        cent = AnyGeom(wkt).as_geometry().Centroid()
        
        font = dict(
            size=18,
            backgroundcolor='w',
        )
        plt.text(cent.GetX(), cent.GetY(), i+1, fontdict=font)

    cmap = plt.cm.Set1
    _, cb = fplots.chloropleth(df.geom, np.arange(7), alpha=.2, cmap=cmap)
    fmo.drawMap('osm', zoom_delta=-1)
    decorate()
    
def plat_proposed():
    df = pd.read_csv('proposed/proposed_districts.csv')

    for i in range(len(df)):
        wkt = df.geom.iloc[i]
        fplots.plot_shape(wkt, 'b-', lw=3)
        cent = AnyGeom(wkt).as_geometry().Centroid()
        
        font = dict(
            size=18,
            backgroundcolor='w',
        )
        plt.text(cent.GetX(), cent.GetY(), i+1, fontdict=font)

    cmap = plt.cm.Set1
    _, cb = fplots.chloropleth(df.geom, np.arange(7), alpha=.2, cmap=cmap)  
    fmo.drawMap('osm', zoom_delta=-1)
    decorate() 
     
def decorate():
    ax = plt.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])

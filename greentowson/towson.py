from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.dfpipeline as dfp
import frm.plots as fplots
import frm.norm as fnorm
import frm.support 

import osgeo.gdal as gdal 
import osgeo.ogr as ogr 

ogr.UseExceptions()

from matchgeom import GeomMatcher, overlaps, intersects
import common 


def main():
    fn = 'gta_towson.kml'
    frm.meta.save_state('towson.json') 
    
    geomdict = fgeom.load_geoms_as_dict(fn)
    geom = geomdict['GTA_Towson']
    
    census = common.load_census_tracts()
    #census = common.load_census_blocks() 

    gm = GeomMatcher(census.geom)
    
    srt = gm.match([geom], intersects)
    idx = srt == 0
    census = census[idx]

    #Compute fractional overlap
    f = lambda x: common.overlap(x, geom)
    census['frac_overlap'] = frm.support.npmap(f, census.geom)

    for col in "TotalPop TotalWhite TotalBlack".split():
        val = np.sum(census[col] * census.frac_overlap)
        print(col, val)
        
    plt.clf()
    fplots.plot_shape(geom, 'r-')
    
    #for g in census.geom:
        #fplots.plot_shape(g, 'c-')
    cm = plt.cm.Greens
    fplots.chloropleth(census.geom, census.TotalPop, 
        cmap=cm, 
        vmin=0, 
        alpha=.5
    )
    
    fmo.drawMap('osm', zoom_delta=-1)
    decorate()
    fplots.add_watermark(-1)
    return census

def density():
    census = common.load_census_tracts()
    area_sqdeg = frm.support.npmap(lambda x: x.Area(), census.geom)
    area_sqkm = area_sqdeg * 12376.72413793103
    density = census['TotalPop'] / area_sqkm

    plt.clf()
    cm = plt.cm.Greens
    _, cb = fplots.chloropleth(census.geom, density, 
        cmap=cm, 
        alpha=.4
    )
    cb.set_label("Population / km$^2$")

    axl = [-76.9, -76.3, 39.1, 39.8]
    plt.axis(axl)
    ax = plt.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    fmo.drawMap('osm', zoom_delta=-1)
    fplots.add_watermark()

        
def decorate():
    axl = [-76.67, -76.53, 39.37, 39.45]
    plt.axis(axl)
    
    ax = plt.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    fmo.drawMap(zoom_delta=-2)

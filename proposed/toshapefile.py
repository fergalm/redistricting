from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom

#import shapeio
#import utils
#import toml
import frm.mapoverlay as fmo
import frm.plots as fplots
import frm.get_geom

import frm.meta 

import frm.dfpipeline as dfp 

def main():
    """Create approximate shapes for proposed new Baltimore County 
    councilmanic districts, as proposed by the redistricting commission.
    
    For these quick and dirty shapes, I assigned each split precinct
    wholly to one district or another as best I could
    
    This is meant for preliminary analysis only
    """
    
    precinct_list = "precinctlists.csv"
    shapefile = '/home/fergal/data/elections/shapefiles/precinct2014/BaCoPrecinct-wgs84.shp'
    outfile = 'proposed_2020_wkt.csv'
    
    idebug()
    frm.meta.save_state(outfile + ".json", note=main.__doc__)
    
    df = pd.read_csv(precinct_list)
  
    pct = frm.get_geom.load_geoms_as_df(shapefile)

    select_cols = ['geoms', 'NAME']
    pipeline = [
        dfp.SelectCols(*select_cols),
        dfp.RenameCols({'NAME':'PrecinctId'}),
    ]

    pct = dfp.runPipeline(pipeline, pct)
    df = pd.merge(df, pct, left_on='precinct', right_on='PrecinctId')

    df = df.groupby('district').apply(union)
    df = df.to_frame('geom').reset_index()
    df.to_csv(outfile)
    return df
    
    
def union(df):
    geoms = df.geoms.values
    
    big_geom = geoms[0]
    for g in geoms:
        big_geom = big_geom.Union(g)
    return big_geom


def plot(df):
    plt.clf()
    
    for i in range(len(df)):
        geom = df.geom.iloc[i]
        geom = geom.Buffer(-0.001)
        
        district = df.district.iloc[i]
        clr = 'C%i' %(district)
        fplots.plot_shape(geom, '-', color=clr)
        #plt.pause(1)
    #plt.legend()

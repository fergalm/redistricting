from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots
import frm.meta
import time


import frm.census as census 

def main():
    """Create up to date census tract geometry and population data from 
    the official source

    This uses the public law data (the pl table) which is the only
    one available through the API at time of writing
    """
    
    cache = '/home/fergal/data/elections/shapefiles/tiger'

    #cols = "P001_0001 ".split()
    cols = """
        P1_001N P1_003N P1_004N
        P3_001N P3_003N P3_004N 
    """.split()
    names = "TotalPop TotalWhite TotalBlack VotingTotal VotingWhite VotingBlack".split()
    outfile = "census_pop_data_2020.csv"
    cols_to_keep= "county fips INTPTLON INTPTLAT geoms ".split()
    cols_to_keep.extend(names)

    
    frm.meta.save_state(outfile +".json", note=main.__doc__)

    mapper = dict()
    for c, n in zip(cols, names):
        mapper[c] = n 
        
    print(cols)
    cq = census.CensusQuery()
    df = cq.query_tract(2020, 'dec', 'pl', '24005', cols) 
    df = df.rename(mapper, axis=1)

    tq = census.TigerQuery(cache)
    geoms = tq.query_tract(2020, '24005').reset_index(drop=True)
    #geoms = geoms[ "geoms GEOID".split()]
    
    df = pd.merge(df, geoms, left_on='fips', right_on='GEOID')
    
    df = df[ cols_to_keep ]
    df.to_csv(outfile)
    return df

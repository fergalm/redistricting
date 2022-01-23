
from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.dfpipeline as dfp
import frm.plots as fplots
import frm.support 
import geomcollect 

import osgeo.gdal as gdal 
import common 


def test_load_district_lines():
    for owner in "aclu commission".split():
        df = common.load_district_lines(owner)
    assert frm.support.check_columns_in_df(df, "name geom".split())
    return df
    
#No need for seperate unit tests her     
#def test_load_2014_district_lines():
    #assert False
    
#def test_load_commission_district_lines():
    #assert False
    
#def test_load_aclu_district_lines():
    #assert False
    
    
def test_load_census_tracts():
    df = common.load_census_tracts()
    assert frm.support.check_columns_in_df(df, "name geom".split())
    
    
#def test_load_census_blocks():
    #assert False
    
    
def test_load_vote_data():
    df = common.load_vote_data_by_precinct()
    assert frm.support.check_columns_in_df(df, "name geom Biden2020".split())
      
def test_plat_shape():
    df = common.load_precinct_data()
    
    plt.clf()
    common.plat_shape(df.geom, df.name, fontdict=dict(fontsize=6))
    
#def test_aggregate():
    #assert False
    
    
    

from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots
import time


"""
This module comes up with an alternative proposal that addresses the
objections raised by the committee.

1. It is no more gerrymandered than current district 5
2. It no more blends suburban and rural populations than proposed district 3
3. It no more splits a community than Towson is currently split 3 ways.


Population of county is 805324 as of 1 Apr 2020, as projected by 2019 ACS survey, 
of which 33% are "Black or African American"

A minority population deserves a district for every 14% of the population it reprsents,
or about 115k. By this logic, there should be two majority black districts.

In response to testimony, the commission argued that the black population is too spread out to do this properly. 

That claim is not true.

In order to be a majority minority, a district needs 805/14 or 57k residents. The black population west of -76.7 degrees longitude contains >140k residents who identified themselves as Black on their census forms. This is comfortable more than you need.
"""


def main():
    #https://www.census.gov/quickfacts/fact/table/baltimorecountymaryland/PST045219
    county_pop = 856273  #From Commission report
    print_sizes(county_pop)

    census_file = 'census_pop_data_2020.csv'
    #census_file = '/home/fergal/all/politics/misc-stats-code/tully2/all_census_results2018.csv'
    da_file = "./districta.txt"
    db_file = "./districtb.txt"
    dc_file = "./district1.txt"

    necessary_cols = "county fips INTPTLON INTPTLAT geoms TotalBlack TotalPop".split()
    
    #axl = [-77.023, -76.461, 39.214,39.587]
    axl = [-76.93, -76.25, 39.13, 39.75]
    while True:
        plt.clf()
        df = pd.read_csv(census_file)
        #df = df[necessary_cols]
        assert check_cols_in_df(df, necessary_cols)
        
        df = df[df.county == 5]
        tracts_a = load_tracts(da_file)
        tracts_b = load_tracts(db_file)
        tracts_c = load_tracts(dc_file)

        plot_demographics(df, axl)

        plot_urdl(axl)
        #pop, frac= mark_district(tracts_a, df, lw=6, color='lime')
        #print("District A: Population = %i, FracBlack = %.3f" 
              #%(pop, frac))
        
        #pop, frac= mark_district(tracts_b, df, lw=6, color='m')
        #print("District B: Population = %i, FracBlack = %.3f" 
              #%(pop, frac))

        #pop, frac= mark_district(tracts_c, df, lw=6, color='c')
        #print("District C: Population = %i, FracBlack = %.3f" 
              #%(pop, frac))
        
        break
        plt.pause(1)
        axl = plt.axis()
    
    #plot_commision_lines()
        
    #plt.axis([-77.023, -76.461, 39.214,39.587])
    fmo.drawMap(zoom_delta=-1)
    ax = plt.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    fplots.add_watermark()


import frm.get_geom as fgg
def plot_urdl(axl):
    fn = "/home/fergal/data/elections/shapefiles/urdl/Urban_Rural_Demarcation_Line.shp"
    df = fgg.load_geoms_as_df(fn)
    
    #idebug()
    for geom in df.geoms.iloc[36]:
        fplots.plot_shape(geom, 'r-', lw=4)
        plt.pause(1)
    #idebug()
    
def plot_commision_lines():
    comm = pd.read_csv("../proposed/proposed_2020_wkt.csv")
    for name, geom in zip(comm.district, comm.geom):
        if name not in [1,2,4]:
            continue 
        
        fplots.plot_shape(geom, 'r-', lw=4)
        cent = AnyGeom(geom).as_geometry().Centroid()
        plt.text(cent.GetX(), cent.GetY(), name, 
            color='k', 
            backgroundcolor='w',
            fontsize=16,
        )

    
def print_sizes(pop):
    per_district = pop/7 
    
    print("Within 5%% is %0.f %.0f %.0f" %(.95*per_district, per_district, 1.05*per_district))

def check_cols_in_df(df, cols):
    return set(df.columns) >= set(cols)


def load_tracts(fn):
    with open(fn) as fp:
        tracts_a = fp.readlines()
    tracts_a = set(list(map(lambda x: int(x[:-1]), tracts_a)))
    return tracts_a
    
    
def plot_demographics(df, axl):

    plt.clf()
    _, cb = fplots.chloropleth(df.geoms, df.TotalBlack, cmap=plt.cm.bone_r, ec='k')
    cb.set_label("Number of Black Residents")

    for i in range(len(df)):
        lng = df.INTPTLON.iloc[i]
        lat = df.INTPTLAT.iloc[i]
        val = df.fips.iloc[i]
        val = "%i" %(val)
        #plt.text(lng, lat, val[5:], color='r')
        
    if axl is not None:
        plt.axis(axl)
    return axl
    
def mark_district(tracts, df, *args, **kwargs):
    tracts = list(tracts)
    
    sum_pop = 0
    sum_black = 0
    union = AnyGeom(df[df.fips == tracts[0]].geoms.iloc[0]).as_geometry()
    for t in tracts:
        row = df[df.fips == t]
        
        if len(row) == 0:
            print("%s not in this census" %(t))
            continue
        #if t == 24005402305:
            #idebug()
        geom = row.geoms.iloc[0]
        pop = row.TotalPop.iloc[0]
        blackpop = row.TotalBlack.iloc[0]
        #pop = row.VotingTotal.iloc[0]
        #blackpop = row.VotingBlack.iloc[0]

        sum_pop += pop 
        sum_black += blackpop
        
        union = union.Union(AnyGeom(geom).as_geometry())
    
    eroded = union.Buffer(-0.002)
    fplots.plot_shape(eroded, *args, **kwargs)
    return sum_pop, sum_black / sum_pop

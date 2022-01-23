from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from frm.anygeom import AnyGeom
import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots

import frm.dfpipeline as dfp
import geomcollect 

import osgeo.gdal as gdal 
import common 

gdal.UseExceptions()
"""
Compute partisan lean of proposed ACLU districts

1. Read in precinct geometries 
2. Store in a Geometry collection
3. For each district
    Compute fractional overlap with each precinct 
    Multiply fract overlap with vote excess 
    Sum
    
"""

def main():
    #districts = load_proposed_districts()
    districts = load_current_districts()
    
    ##census_file = '/home/fergal/all/politics/misc-stats-code/tully2/all_census_results2020.csv'
    #census_file = '/home/fergal/all/politics/misc-stats-code/tully2/all_census_results2018.csv'
    #precincts = load_precint_data()
                 
    precinct_geoms = load_precinct_geoms()
    votes = pd.read_csv('./aclu/tully_input.csv', index_col=0)
    #census_data = pd.read_csv("./black_districts/census_pop_data_2020.csv")

    
    plt.figure(1)
    plot_partisan_lean(districts, precinct_geoms, votes)
    plt.title("Partisan Lean of Current Districts")
    
    #plt.figure(2)
    ##plat_district_boundaries(districts)
    #plat_districts_and_demographics(districts, census_data)


def plot_current_partisan_lean():
    votes = pd.read_csv('./aclu/tully_input.csv', index_col=0)
    

def plat_districts_and_demographics(districts, census_data):
    plt.clf()
    axl = [-76.9, -76.3, 39.2, 39.8]
    plot_demographics(census_data, axl, label=False)

    for i, d in enumerate(districts.geom):
        if i not in [0, 1, 3]:
            continue
        
        fplots.plot_shape(d.Buffer(-2e-3), 'C%i' %(i+2), lw=4)
        centroid = d.Centroid()
        
        plt.text(centroid.GetX(), centroid.GetY(), i+1, 
            fontsize=26,
            backgroundcolor='w',
        )

    ax = plt.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    fplots.add_watermark()


def plat_district_boundaries(districts):
    plt.clf()
    for i, d in enumerate(districts.geom):
        fplots.plot_shape(d.Buffer(-2e-3), 'C%i' %(i))
        centroid = d.Centroid()
        
        plt.text(centroid.GetX(), centroid.GetY(), i+1, fontsize=20)
    ax = plt.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    fmo.drawMap(zoom_delta=-1)
    fplots.add_watermark()


def plot_partisan_lean(districts, precinct_geoms, votes):
    gc = geomcollect.GeomCollection(precinct_geoms)
    races = set(votes.columns) - set("NAME Pop".split())

    x = 0
    plt.clf()
    for d, name in zip(districts.geom, districts.name):
        frac =  gc.measure_overlap(d)
        frac = pd.merge(frac, votes, left_on='name', right_on='NAME')
        #idebug()
        for r in races:
            #print(name, r, np.sum(frac.frac * frac[r]))
            score = np.sum(frac.frac * frac[r])
            clr= 'b'
            va = 'bottom'
            if score < 0:
                clr = 'r'
                va = 'top'
                
            plt.plot([x,x], [0, score], '-', color=clr)
            plt.text(x, score, f"   {r}    ", rotation=90, ha='center', va=va)
            x +=1
            
        plt.text(x-2, -40e3, "District %i" %(name), ha='center', fontsize=18)
        
        clr = 'lightblue'
        if np.sum(frac.frac * frac['Clinton2016']) < 0:
            clr = 'pink'
            
        plt.axvspan(x-5, x, color=clr, alpha=.2)
        x+=4
    
    plt.ylim(-50e3, 50e3)
    plt.ylabel("Vote Excess")
    plt.gca().set_xticks([])
    plt.title("Partisan Lean of Proposed Commission districts")
    fplots.add_watermark()
    
        
def load_proposed_districts():
    fn = 'proposed/proposed_districts.csv'
    districts = pd.read_csv(fn, index_col=0)
    
                       
    districts['name'] = districts.district
    districts['geom'] = list(map(lambda x: AnyGeom(x).as_geometry(), districts.geom))
    return districts


def load_current_districts():
    return common.load_district_lines('v2010')

def load_precinct_geoms():
    fn = '/home/fergal/data/elections/shapefiles/precinct2014/BaCoPrecinct-wgs84.shp'

    tasks = [
        LoadGeoms(fn),
        dfp.SelectCols('NAME', 'geoms'),
        dfp.RenameCols({'geoms': 'geom', 'NAME':'name'})
    ]
    
    return dfp.runPipeline(tasks)


class LoadGeoms(dfp.AbstractStep):
    def __init__(self, fn):
        self.fn = fn
        
    def apply(self, df):
        return fgeom.load_geoms_as_df(self.fn)


def plot_demographics(df, axl, label=True):
    """Show black population by census tract. The input file for this function
    is 'census_pop_data_2020.csv'
    """

    plt.clf()
    _, cb = fplots.chloropleth(df.geoms, df.TotalBlack, cmap=plt.cm.bone_r, ec='k')
    cb.set_label("Number of Black Residents")

    if label:
        for i in range(len(df)):
            lng = df.INTPTLON.iloc[i]
            lat = df.INTPTLAT.iloc[i]
            val = df.fips.iloc[i]
            val = "%i" %(val)
            plt.text(lng, lat, val[5:], color='r')
        
    if axl is not None:
        plt.axis(axl)
    return axl


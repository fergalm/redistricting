from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import frm.mapoverlay as fmo
import frm.get_geom as fgeom
import frm.plots as fplots

import frm.dfpipeline as dfp
import geomcollect 

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
    districts = load_proposed_districts()

    #print(districts.head())
    ##census_file = '/home/fergal/all/politics/misc-stats-code/tully2/all_census_results2020.csv'
    #census_file = '/home/fergal/all/politics/misc-stats-code/tully2/all_census_results2018.csv'
    #precincts = load_precint_data()
                 
    precinct_geoms = load_precinct_geoms()
    
    gc = geomcollect.GeomCollection(precinct_geoms)

    votes = pd.read_csv('tully_input.csv', index_col=0)

 
    races = set(votes.columns) - set("NAME Pop".split())
    
    x = 0
    plt.figure(1)
    plt.clf()
    for d, name in zip(districts.geom, districts.name):
        frac =  gc.measure_overlap(d)
        frac = pd.merge(frac, votes, left_on='name', right_on='NAME')
        
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
            
        plt.text(x-2, -40e3, "District %i" %(name+1), ha='center', fontsize=18)
        
        clr = 'lightblue'
        if np.sum(frac.frac * frac['Clinton2016']) < 0:
            clr = 'pink'
            
        plt.axvspan(x-5, x, color=clr, alpha=.2)
        x+=4
    
    plt.ylim(-50e3, 50e3)
    plt.ylabel("Vote Excess")
    plt.gca().set_xticks([])
    plt.title("Partisan Lean of Proposed ACLU districts")
    fplots.add_watermark()


    plt.figure(2)
    plt.clf()
    for i, d in enumerate(districts.geom):
        fplots.plot_shape(d.Buffer(-2e-3))
        centroid = d.Centroid()
        
        plt.text(centroid.GetX(), centroid.GetY(), i+1)
    ax = plt.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    fmo.drawMap(zoom_delta=-1)
    fplots.add_watermark()
        
def load_proposed_districts():
    fn = 'Baltimore_County_8_28_draft.zip'
    districts = fgeom.get_geometries(fn)
    #names = list(map(lambda x: x[1], districts))
    geoms = list(map(lambda x: x[0], districts))
    
    districts = pd.DataFrame()
    districts['geom'] = geoms
    districts['name'] = np.arange(len(districts))
    return districts


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

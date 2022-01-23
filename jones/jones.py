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

from matchgeom import GeomMatcher, overlaps
import common 


"""
Slide 1
Black population is 255,793 (30% of county)
With 7 seats, 14% of population represented by a councillor
Fair share for black population is 2 seats 

7% of total population (61k residents) represents a majority in any one district (assuming voter turnout is race-independent)

Slide 2
The Black Population is highly concentrated in west of county

Slide 3
The black population is the core of the Democratic vote in
the county 

Slide 4
The commission splits the black vote in the western part 
of the county to minimise its influence

Slide 5 
Multiple maps are possible, all concerns can be addressed


"""

def main():

    """Black/AA alone = 255793 in 2020 
    Total pop is 854,535
    """
    #plat_demographics()
    #plt.savefig('demographic_distribution.png')
    
    #plat_johnnyo()
    #plt.savefig('johnnyo.png')

    
    plat_demographics()
    overlay_commision_lines()
    plt.title("Number of black residents per district")
    
    plt.savefig('num_black_residents_per_district.png')
    
    
#def plat_turnout(df=None):
    #if df is None:
        #fn = '/home/fergal/data/elections/voterrolls/BaltimoreCountyVoterRoll2018929.txt'
        #df = pd.read_csv(fn)

    #df2 = df[df.StatusCode == 'A']
    ##df2 = df 
    #print(len(df2))
    #eligible_voters = df2.groupby('Precinct').LastName.count()
    
    #df3 = df2[df2['2016G'] == '2016G']
    #idebug()
    #actual_voters = df3.groupby('Precinct').LastName.count()
    
    #assert np.all(eligible_voters.index == actual_voters.index)
    ##idebug()
    #turnout = actual_voters / eligible_voters 
    #turnout = turnout.to_frame('Turnout')
    #turnout['TotalPop'] = eligible_voters
    #turnout['ActualVoters'] = actual_voters
    #return turnout 

def overlay_commision_lines():
    df = common.load_district_lines('commission')
    
    fontdict = dict(
        fontsize=32,
        backgroundcolor='w'
    )
    
    for name in [1,2,4]:
        idx = df.name == name
        district_geom = df[idx].geom.values[0]
        fplots.plot_shape(district_geom, 'r-', lw=4)
        
        tracts = common.load_census_tracts()
        total_black_pop = np.sum(tracts.TotalBlack)
        
        mt = GeomMatcher(tracts.geom.values)
        srt = mt.match([district_geom], overlaps)
        idx = srt == 0
        
        tracts = tracts[idx]
        f = lambda x: common.overlap(x, district_geom)
        frac_overlap = frm.support.npmap(f, tracts.geom)

        pop = np.sum(tracts.TotalBlack * frac_overlap)
        #percent = 100 * pop / total_black_pop 
        #msg = "%.0f%%" %(percent)
        
        cent = district_geom.Centroid()
        msg = "%ik" %(np.round(pop/1e3))
        plt.text(cent.GetX(), cent.GetY(), msg, 
            fontdict=fontdict,
            ha='center'
            )

    plt.text(-76.6, 39.7, 
        "61k residents consitutes\na district majority",
        fontsize=28,
        ha='center',
        backgroundcolor='lightgrey'
    )

    
    
def plat_demographics():
    df = common.load_census_tracts()
    
    plt.clf()
    cmap = plt.cm.bone_r
    #cmap = plt.cm.viridis
    #norm = fnorm.DiscreteNorm(7)
    _, cb = fplots.chloropleth(
        df.geom, 
        df['TotalBlack'], 
        cmap=cmap, 
        #norm=norm,
        ec='k',
    )
    cb.set_label("Black Population by Census Tract")

    decorate()
    
def plat_johnnyo():
    df = common.load_vote_data_by_precinct()
    
    race = 'JohnnyO2018'
    #race = 'Clinton2016'
    plt.clf()
    plt.gcf().set_size_inches((12.5, 11.5))
    cmap = plt.cm.RdBu
    #cmap = plt.cm.viridis
    norm = fnorm.DiscreteNorm(14, -1200, 1200)
    _, cb = fplots.chloropleth(df.geom, df[race], cmap=cmap, norm=norm)
    cb.set_label("Vote Surplus")
    
    plt.title(f"Vote Surplus by Precinct for {race}")
    decorate()
    
    
def decorate():
    axl = [-76.9, -76.3, 39.1, 39.8]
    plt.axis(axl)
    
    ax = plt.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    fmo.drawMap(zoom_delta=-2)
    fplots.add_watermark()

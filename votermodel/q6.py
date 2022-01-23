from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import scipy.optimize as spOpt
import frm.plots as fplots
import pandas as pd
import numpy as np
import common

import votermodel.utils as utils 
import frm.mapoverlay as fmo
    
"""
Is there a correlation between the number of democratic voters for a candidate and the 
racial demographics of the precinct?

x Create model for expected votes
x Get O-C for model
o Get per-precinct racial data 
o Plot excess votes as a func of white frac 
o Model turnout as a function of demographics 
o Plot excess votes as a func of white frac in DOIP voters


I know the number of white,black,other people in the precinct.
I know 
o Num reg DEM 
o Num that turnout 
o Num that vote for my candidate.

Is the simplest thing to plot the fraction of {people that show up to vote}
that {vote for my candidate} as a function of white frac?

DOIP == "Day-of, in-person (voters)"
"""

def main():
    candidate = "Peter Franchot"
    #candidate = "Ben Jealous"
    candidate = "John Johnny O Olszewski, Jr."
    year = 2018  #Have to get 2014 working

    plt.clf()
    ms=14
    plot_omc_versus_white_frac("Larry Hogan", 2018, 'C4o', ms=ms-4)

    plot_omc_versus_white_frac("Peter Franchot", 2018, 'C0o', ms=ms-4)
    plot_omc_versus_white_frac("Ben Jealous", 2018, 'C5o', ms=ms)
    plot_omc_versus_white_frac("John Johnny O Olszewski, Jr.", 2018, 'C1o', ms=ms-4)
    plt.xlabel("White Fraction")
    plt.ylabel("Vote Excess over Model")
    
    plt.legend()
    
def plot_omc_versus_white_frac(candidate, year, *args, **kwargs):    
    #Load data 
    votesWon = common.loadElectionResultsByPrecinct(year, primary=False)
    numDoip = common.load_DOIP_voters_by_precinct(year)
    demo = common.load_precinct_demographics()
    demo = demo.drop('geom', axis=1)
    
    #Fit model
    #Compute excess of model 
    df = utils.compute_vote_excess(candidate, numDoip, votesWon)
    
    #Plot excess as a func of white frac 
    df = pd.merge(df, demo, on='name')

    white_frac = df.VotingWhite.values  / df.VotingTotal
    x = 100*white_frac
    y = 100*df.frac_excess
    if candidate[:3] == 'Ben':
        y -= 24
    plt.plot(x, y, *args, label=candidate, **kwargs)

    
    
    
def gen_precinct_racial_data():
    """Use to create the precinct level racial data
    
    Too slow to be used in production, load the data 
    with 
    
    `common.load_precinct_demographics`
    """
    
    stats = load_block_level_pop()
    block_geoms = load_block_geoms()
    blocks = pd.merge(stats, block_geoms, left_on="fips", right_index=True)

    pct_geoms = common.load_precinct_geoms()
    
    overlap = common.compute_frac_overlaps(
        pct_geoms.geom, 
        blocks.geoms,
    )    
        
    cols = """
        TotalPop
        TotalWhite
        TotalBlack
        TotalWhiteNotHispanic
        VotingTotal
        VotingWhite
        VotingBlack
        VotingWhiteNotHispanic
    """.split()

    for c in cols:
        vals = blocks[c].values.astype(float)
        pct_geoms[c] = np.dot(overlap, vals)    

    idebug()
    outfn = "data/precinct_data/precinct_race_data.csv"
    frm.meta.save_metadata(outfn + ".json")
    pct_geoms.to_csv(outfn)
    return pct_geoms 


import frm.census
def load_block_level_pop():
    cq = frm.census.CensusQuery()
    
    mapper = dict(
        P1_001N='TotalPop',
        P1_003N='TotalWhite',
        P1_004N='TotalBlack',
        P2_005N='TotalWhiteNotHispanic',
        P3_001N='VotingTotal',
        P3_003N='VotingWhite',
        P3_004N='VotingBlack',
        P4_005N='VotingWhiteNotHispanic',
    )

    df = cq.query_block(2020, 'dec', 'pl', '24005', mapper.keys())
    df = df.rename(mapper, axis=1)
    return df

    
def load_block_geoms():
    cache = '/home/fergal/data/elections/shapefiles/tiger'
    tq = frm.census.TigerQuery(cache)
    df = tq.query_block(2020, '24005')
    df = df[ ["geoms", "GEOID20"] ]
    return df


def merge_block_data(stats, geom):
    idebug()
    return pd.merge(stats, geom, left_on="fips", right_index=True)

    

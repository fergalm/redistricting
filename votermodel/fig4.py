from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import frmplots.plots as fplots
import pandas as pd
import numpy as np
import common

import votermodel.utils as utils 
from frmbase.support import lmap 
import frmplots.plots as fplots
import frmplots.norm as fnorm
import frmplots.galaxyplot as fgp
import frmgis.plots as fgplots

import re


"""
The money plot

This plot shows impact of the racial demographics of a precinct on a candidate's performance. 

Performance is defined so that the vote share in a precinct with no white voters 

The baseline is chosen to be the votes won in a precinct over and above those predicted from the model, scaled so precinct with zero white voters is chosen as the baseline.

The solid black line shows the impact of increasing fraction of white voters on Anthony Brown's 2014 performance, while the dashed blue line shows Ben Jealous. The thin grey lines show other (white) Democratic candidates 


"""


def main():
    demo = common.load_precinct_demographics()
    demo = demo.drop('geom', axis=1)
    demo['white_frac'] = demo.VotingWhite.values  / demo.VotingTotal
    demo['black_frac'] = demo.VotingBlack.values  / demo.VotingTotal
    
    plt.clf()
    plt.gcf().set_size_inches((12,8))
    
    year = 2018
    candlist = [
        "Peter Franchot",
        "Scott Shellenberger",
        "Ben Cardin",
        "Brian E. Frosh",
        "Grace G. Connolly",
        "John Johnny O Olszewski, Jr.",
    ]
    for cand in candlist:
        show_candidate(cand, year, demo, clr='grey', ls='-', show_points=False, lw=2)
    show_candidate('Ben Jealous', year, demo, clr='C0', ls='--', lw=4, label=True)

    year = 2014
    candlist = [
        "R. Jay Fisher",
        "Scott Shellenberger",
        "Grace G. Connolly",
        "Peter Franchot",
        "Kevin Kamenetz",
    ]
    for cand in candlist:
        show_candidate(cand, year, demo, clr='grey', ls='-', show_points=False, lw=2)
    show_candidate('Anthony G. Brown', year, demo, clr='k', ls='-', lw=4, label=True)
        
        

    for i in np.linspace(20, 100, 9):
        plt.axhspan(-i, -100, color='r', alpha=.05, lw=0, ec="none")
        
    plt.ylim(-100, 25)
    plt.xlabel("Precinct White Fraction", fontsize=26)
    plt.ylabel("White Penalty", fontsize=26)
    #plt.ylabel("Performance above model (%)")
    plt.legend(loc=1)
    fplots.add_watermark()
    plt.savefig('votermodel/fig4.png')

def show_candidate(candidate, year, demo, clr='k', lw=4, ls='-', show_points=True, label=None):
    #Load and merge with race data
    df = load(candidate, year)
    df = pd.merge(df, demo, on='name')

    #Scale so Black districts are the reference
    #idx = df.black_frac > .75
    #med = np.median(df[idx].frac_excess)
    #df['frac_excess'] -= med
    
    xcol = 'white_frac'
    if label:
        label = candidate
    offset = add_fit(df, xcol, color=clr, ls=ls, lw=lw, label=label)
    #offset = 0
    if show_points:
        plt.plot(100*df[xcol], 100*df.frac_excess - offset, 'o', color=clr)
    
def load(candidate, year):
    votesWon = common.loadElectionResultsByPrecinct(year, primary=False)
    doipPerPrecinct = common.load_DOIP_turnout_by_precinct(year)
    df = utils.compute_vote_excess(candidate, doipPerPrecinct, votesWon)
    return df


from frmbase.fitter.lsf import Lsf
def add_fit(df, xcol, *args, **kwargs):
    x = df[xcol].values * 100 
    y = df.frac_excess.values * 100
    
    fObj = Lsf(x, y, 1, 2)
    offset, slope = fObj.getParams()
    #print(fObj.getParams())
    #f = offset + slope * x
    f = 0 + slope * x
    x = np.concatenate([x, [0]])
    f = np.concatenate([f, [0]])
    srt = np.argsort(x)

    #f = fObj.getBestFitModel()
    plt.plot(x[srt], f[srt], *args, **kwargs)
    return offset
    
def despace(name):
    return re.subn("\s", "_", name, 0)[0]
